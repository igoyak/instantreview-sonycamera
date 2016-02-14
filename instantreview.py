#!/usr/bin/env python3
from flask import Flask, Response
from threading import Thread
from queue import Queue
import json
import requests

DEBUG = False


def main():
    q = Queue()
    s = Thread(target=server, args=(q,))
    s.start()
    camera(q)


def camera(queue: Queue):
    start_recmode = {"method": "startRecMode", "params": [], "id": 1, "version": "1.0"}
    get_event = {"method": "getEvent", "params": [True], "id": 1, "version": "1.0"}
    url = "http://192.168.122.1:8080/sony/camera"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(start_recmode), headers=headers)
    if DEBUG:
        if response.status_code == 200:
            print("Enabled record mode")
        else:
            print("Failed to enable record mode")
    while True:
        response = requests.post(url, data=json.dumps(get_event), headers=headers)
        data = json.loads(response.content.decode())
        if len(data["result"][5]) > 0:
            pic_url = data["result"][5][0]['takePictureUrl'][0]
            if DEBUG: print("Got a picture: %s" % pic_url)
            queue.put(pic_url)


def server(queue: Queue):
    app = Flask(__name__)

    html = '''
<html>
<head>
    <style>
        .img {
        max-width: 100%;
        max-height: 100%;
        box-shadow: 0px 0px 5px 0px rgba(0,0,0,0.75);
        position: relative;
        top: 50%;
        transform: translateY(-50%);
        }
        .container {
        position: absolute;
        height: 100%;
        top: 0%;
        transition: all 0.3s;
        display: none;
        padding: 8px;
        box-sizing: border-box;
        }
}
    </style>
</head>
<body style="background: #202020; margin: 0; padding: 0;">
<div id="0" class="container"><img class="img" src="#"></div>
<div id="1" class="container"><img class="img" src="#"></div>
<div id="2" class="container"><img class="img" src="#"></div>
<div id="3" class="container"><img class="img" src="#"></div>
<div id="4" class="container"><img class="img" src="#"></div>
<div id="5" class="container"><img class="img" src="#"></div>
<script>
	var containers = [];
	for (i=0; i < 6; i++) {
		containers.push(document.getElementById(i))
	}

	function rotate(arr){
    	arr.unshift(arr.pop());
  		return arr;
	} 

	styles = [
	function(d) {
		// latest picture, large left
        d.style.width = "84%";
        d.style.height = "100%";
        d.style.right = "16%";
        d.style.top = "0";
        d.style.transition = "all 0.3s";
        d.style.display = "block";
    },
	function(d) {
        d.style.width = "16%";
        d.style.height = "25%";
        d.style.right = "0";
    },
    function(d) {
        d.style.width = "16%";
        d.style.height = "25%";
        d.style.right = "0";
        d.style.top = "25%";
    },
	function(d) {
        d.style.width = "16%";
        d.style.height = "25%";
        d.style.right = "0";
        d.style.top = "50%";
    },
	function(d) {
        d.style.width = "16%";
        d.style.height = "25%";
        d.style.right = "0";
        d.style.top = "75%";
    },
	function(d) {
		// Oldest picture. 
		// Hide and put on the left to make the next picture sweep in. 
        d.style.width = "84%";
        d.style.height = "100%";
        d.style.right = "120%";
        d.style.top = "0";
        d.style.display = "block";
        d.style.transition = "none";
    }]


    function update(newLink) {
		containers = rotate(containers)
		for (i=0; i < containers.length; i++) {
			styles[i](containers[i])
		}
		// Set the new picture
        var i = containers[0].getElementsByTagName("img")[0]
        i.src = newLink
    }

    // DEBUG
	/*
    function foo() {update("a.jpg")}
    setTimeout(function(){ foo() }, 20);
    setTimeout(function(){ foo() }, 500);
    setTimeout(function(){ foo() }, 1000);
    setTimeout(function(){ foo() }, 1500);
    setTimeout(function(){ foo() }, 2000);
	*/

    var eventSource = new EventSource("/stream");
    eventSource.onmessage = function(e) {
        function complete(data) {
            update(e.data)
        }
		// Preload the image, and show when loaded
        var preloadImg = new Image();
        preloadImg.onload = complete;
        preloadImg.src = e.data;
    };
</script>
</body>
</html>
    '''

    # SSE "protocol" is described here: http://mzl.la/UPFyxY
    class ServerSentEvent(object):

        def __init__(self, data):
            self.data = data
            self.event = None
            self.id = None
            self.desc_map = {
                self.data: "data",
                self.event: "event",
                self.id: "id"
            }

        def encode(self):
            if not self.data:
                return ""
            lines = ["%s: %s" % (v, k) for k, v in self.desc_map.items() if k]

            return "%s\n\n" % "\n".join(lines)

    @app.route("/stream")
    def stream():
        def eventStream():
            while True:
                a = queue.get()
                ev = ServerSentEvent(a)
                yield ev.encode()

        return Response(eventStream(), mimetype="text/event-stream")

    @app.route('/')
    def get_html():
        return html

    app.run(port=1256)


if __name__ == '__main__':
    main()

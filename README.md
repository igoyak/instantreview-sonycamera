# instantreview-sonycamera

This script displays the last taken photos in a web browser, when connected to a Sony camera. The purpose is to review photos on a screen that is larger and has a higher resolution than the camera's own screen. It's tested on the Sony a5000 (ILCE-5000), but will probably work on other modern Sony cameras with some tweaking. [Check here](https://developer.sony.com/develop/cameras/) for more info. 

# Usage

- Start the "Smart Remote Embedded" app on the camera
- Connect to the camera's wifi acces point
- Run ./instantreview.py
- Open 0.0.0.0:1256 in a web browser

As photos are taken, they will show up in the browser. 

# Python module dependencies

- flask
- requests

Tested with the Sony a5000 on Arch linux and chromium. 


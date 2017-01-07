#!/usr/bin/env python3

import json
from hackeriet.mqtt import MQTT

class Listener(object):
    def __init__(self):
        self.artist = None
        self.title = None
        self.mqtt = MQTT()

    def new_media_status(self, status):
        if status.artist != self.artist or status.title != self.title:
            self.artist = status.artist
            self.title = status.title
            print("{} -- {}".format(status.artist, status.title))
            #if status.artist != None or status.title != None:
            print(status.media_metadata)
            self.mqtt("hackeriet/chromecast", json.dumps(status.media_metadata))

def snoop():
    import pychromecast, time

    cast = pychromecast.get_chromecast()
    if cast is None: # shrug emoji
        cast = pychromecast.Chromecast("10.10.3.89")
    cast.wait()
    print("Connected to {}".format(cast.device.friendly_name))
    cast.media_controller.register_status_listener(Listener())
    while True:
        time.sleep(30)

if __name__ == "__main__":
    snoop()

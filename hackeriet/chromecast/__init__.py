#!/usr/bin/env python3

import json, os
from hackeriet.mqtt import MQTT

target_cast_name = os.getenv("CAST_NAME", "Hackeriet")
mqtt_topic = os.getenv("MQTT_CAST_TOPIC", "hackeriet/chromecast")

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
            print(status.media_metadata)
            self.mqtt(mqtt_topic, json.dumps(status.media_metadata))

def snoop():
    import pychromecast, time

    chromecasts = pychromecast.get_chromecasts()
    cast = next(cc for cc in chromecasts if cc.device.friendly_name == target_cast_name)
    cast.wait()
    print("Connected to {}".format(cast.device.friendly_name))
    cast.media_controller.register_status_listener(Listener())
    while True:
        time.sleep(15)

if __name__ == "__main__":
    snoop()

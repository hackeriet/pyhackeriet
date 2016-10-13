#!/usr/bin/env python3

class Listener(object):
    def __init__(self):
        import zmqclient

        self.artist = None
        self.title = None
        self.pub = zmqclient.pub()

    def new_media_status(self, status):
        if status.artist != self.artist or status.title != self.title:
            self.artist = status.artist
            self.title = status.title
            print("{} -- {}".format(status.artist, status.title))
            if status.artist != None or status.title != None:
                try:
                    self.pub.send(b"CHROMECAST", 2) # 2 == zmq.SNDMORE FIXME
                    self.pub.send_json(status.media_metadata)
                except Exception as e:
                    print(e)

if __name__ == '__main__':
    import pychromecast, time

    cast = pychromecast.get_chromecast()
    cast.wait()
    print("Connected to {}".format(cast.device.friendly_name))
    zmq = Listener()
    cast.media_controller.register_status_listener(zmq)
    while True:
        time.sleep(30)


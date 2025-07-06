#!/usr/bin/env python
from hackeriet import mifare
from hackeriet.door import users
import os, logging, time

logging.basicConfig(level=logging.DEBUG)


class MQTTSignaler:
  def __init__(self):
    from hackeriet.mqtt import MQTT
    self.door_name = os.getenv("DOOR_NAME", 'hackeriet')
    self.door_topic = "hackeriet/door/%s/open" % door_name
    self.mqtt = MQTT()
  def signal(self, user):
    self.mqtt(door_topic, user)

class HTTPSignaler:
    def __init__(self):
      # load config
      self.host = "localhost"
      self.port = 1234
    def signal(self, user):
      import urllib
      urllib.request.urlopen("http://%s:%d/open?%s" % (self.host, self.port, user)).read()

def main_loop(signaler):
  door_timeout = int(os.getenv("DOOR_TIMEOUT", 2))
  while True:
      users.load()
      # Read data from card reader
      logging.debug('mifare: waiting for data...')
      data = mifare.try_read()
      if data:
        logging.debug('mifare: data read')
        user = users.auth(data[0:16])
        if user:
          ascii_user = user.encode('ascii', 'replace').decode('ascii')
          logging.info('auth: card read for user %s' % ascii_user)
          signaler.signal(user)
        else:
          logging.debug('auth: card data does not belong to a user: %s' % data[0:16])
        # Avoid spewing messages every single ms while a card is in front of the reader
        time.sleep(door_timeout)
      else:
        logging.debug('mifare: no data read in last attempt')

def main():
  logging.debug('Starting main loop')

  parser = argparse.ArgumentParser()
  parser.add_argument('--experiment-with-mqtt', action='store_true')
  args = parser.parse_args()

  if args.experiment_with_mqtt:
    signaler = MQTTSignaler()
  else:
    signaler = HTTPSignaler()

  main_loop(signaler)


if __name__ == "__main__":
  main()


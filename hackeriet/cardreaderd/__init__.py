#!/usr/bin/env python
from hackeriet import mifare
from hackeriet.mqtt import MQTT
from hackeriet.door import users
import os, logging, time

logging.basicConfig(level=logging.INFO)

door_name = os.getenv("DOOR_NAME", 'hackeriet')
door_topic = "hackeriet/door/%s/open" % door_name
door_timeout = int(os.getenv("DOOR_TIMEOUT", 2))

mqtt = MQTT()

def main():
  logging.debug('Starting main loop')
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
        mqtt(door_topic, user)
      else:
        logging.debug('auth: card data does not belong to a user: %s' % data[0:16])
      # Avoid spewing messages every single ms while a card is in front of the reader
      time.sleep(door_timeout)
    else:
      logging.debug('mifare: no data read in last attempt')

if __name__ == "__main__":
  main()


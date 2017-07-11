#!/usr/bin/env python
from hackeriet import mifare
from hackeriet.mqtt import MQTT
from hackeriet.door import users
import os, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s')

door_name = os.getenv("DOOR_NAME", 'hackeriet')
door_topic = "hackeriet/door/%s/open" % door_name
door_timeout = int(os.getenv("DOOR_TIMEOUT", 2))

mqtt = MQTT()

def main():
  while True:
    users.load()
    # Read data from card reader
    data = mifare.try_read()
    if data:
      user = users.auth(data[0:16])
      if user:
        ascii_user = user.encode('ascii', 'replace').decode('ascii')
        logging.info('Card reader read card for %s' % ascii_user)
        mqtt(door_topic, user)
      else:
        logging.debug('User not found: %s' % data[0:16])
      # Avoid spewing messages every single ms while a card is in front of the reader
      time.sleep(door_timeout)

if __name__ == "__main__":
  main()


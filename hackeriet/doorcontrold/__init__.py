#!/usr/bin/env python
from hackeriet.mqtt import MQTT
from hackeriet.door import Doors
import threading, os, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(message)s')

piface = False

# Determine if piface is used on the Pi
if "PIFACE" in os.environ:
  piface = True
  logging.info('Using piface configuration')

# Be backwards compatible with old env variable name
gpio_pin = int(os.getenv("DOOR_GPIO_PIN", os.getenv("DOOR_PIN", 0)))

# How many seconds should the door lock remain open
timeout = int(os.getenv("DOOR_TIMEOUT", 2))

door = Doors(piface=piface,pin=gpio_pin,timeout=timeout)

def on_message(mosq, obj, msg):
  door.open()
  logging.info('Door opened: %s' % msg.payload)

door_name = os.getenv("DOOR_NAME", 'hackeriet')
door_topic = "hackeriet/door/%s/open" % door_name

mqtt = MQTT(on_message)
mqtt.subscribe(door_topic, 0)

# Block forever
def main():
  for t in threading.enumerate():
    if t is threading.currentThread():
      continue
    t.join()

if __name__ == "__main__":
  main()


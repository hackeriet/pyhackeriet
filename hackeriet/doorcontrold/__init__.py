#!/usr/bin/env python
import threading, os, logging
import argparse

def connect_to_mqtt(door):
  logging.warn("Using MQTT for signaling. Never do this in production; use local HTTP instead.")

  from hackeriet.mqtt import MQTT

  door_name = os.getenv("DOOR_NAME", 'hackeriet')
  door_topic = "hackeriet/door/%s/open" % door_name

  def on_message(mosq, obj, msg):
    door.open()
    logging.info('Door opened: %s' % msg.payload)

  mqtt = MQTT(on_message)
  mqtt.subscribe(door_topic, 0)

  for t in threading.enumerate():
    if t is threading.currentThread():
      continue
    t.join()

def listen_to_socket(door):
  from flask import Flask
  app = Flask(__name__)

  @app.route("/open")
  def opendoor():
      door.open()
      return "opened"
  app.run(host='localhost', port=1234)

def setup(use_simulated_door, use_mqtt):
  from hackeriet.door import Doors, SimulatedDoor

  logging.basicConfig(level=logging.DEBUG)

  piface = False

  # Determine if piface is used on the Pi
  if "PIFACE" in os.environ:
    piface = True
    logging.info('Using piface configuration')

  # Be backwards compatible with old env variable name
  gpio_pin = int(os.getenv("DOOR_GPIO_PIN", os.getenv("DOOR_PIN", 0)))

  # How many seconds should the door lock remain open
  timeout = int(os.getenv("DOOR_TIMEOUT", 2))

  if use_simulated_door:
    door = SimulatedDoor()
  else:
    door = Doors(piface=piface,pin=gpio_pin,timeout=timeout)

  if use_mqtt:
    connect_to_mqtt(door)
  else:
    listen_to_socket(door)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--simulated', action='store_true')
  parser.add_argument('--experiment-with-mqtt', action='store_true')
  args = parser.parse_args()

  setup(args.simulated, args.experiment_with_mqtt)

if __name__ == "__main__":
  main()


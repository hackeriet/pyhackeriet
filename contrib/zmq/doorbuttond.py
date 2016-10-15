import zmqclient
import zmq
import pifacedigitalio
import time
from syslog import syslog

pub = zmqclient.pub()
pifacedigital = pifacedigitalio.PiFaceDigital()

space_status_led_pin = 7
door_sensor_pin = 3
door_button_pin = 0
humla_status = ""
door_status = 0

space_status_led = pifacedigital.output_pins[space_status_led_pin]
door_button = pifacedigital.input_pins[door_button_pin]
door_sensor = pifacedigital.input_pins[door_sensor_pin]

def send_event(name, value):
    print("Event {}: {}".format(name, value))
    pub.send(name.encode("ascii"), zmq.SNDMORE)
    pub.send_string(value)

def set_humla_status(s):
    humla_status = s
    send_event("HUMLA", s)

def humla_button(event):
    value = door_button.value
    if value != 0:
        set_humla_status("OPEN")
        space_status_led.turn_on()
    else:
        set_humla_status("closed")
        space_status_led.turn_off()

def door_event(event):
    global door_status
    state = door_sensor.value
    if state != door_status:
        door_status = state
        send_event("DOOR_SENSOR", "open" if state == 0 else "closed")

listener = pifacedigitalio.InputEventListener(chip=pifacedigital)
listener.register(door_sensor_pin, pifacedigitalio.IODIR_FALLING_EDGE, door_event)
listener.register(door_sensor_pin, pifacedigitalio.IODIR_RISING_EDGE, door_event)
listener.register(door_button_pin, pifacedigitalio.IODIR_FALLING_EDGE, humla_button)
listener.register(door_button_pin, pifacedigitalio.IODIR_RISING_EDGE, humla_button)
listener.activate()
print("ok")


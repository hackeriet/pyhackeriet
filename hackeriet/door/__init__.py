import time
import atexit
import logging

class Doors():
  def __init__(self, piface=False, pin=5, timeout=1):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM) # Broadcom PIN numbering
    self.timeout = timeout
    if piface:
      import pifacedigitalio
      self.piface = pifacedigitalio.PiFaceDigital()
    else:
      self.piface = False
      self.pin = pin
      GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

  #@atexit.register
  def cleanup(self):
    if not self.piface:
      GPIO.cleanup()

  def open(self):
    if self.piface:
      self.piface.output_pins[0].turn_on()
      time.sleep(self.timeout)
      self.piface.output_pins[0].turn_off()
    else:
      GPIO.output(self.pin, GPIO.HIGH)
      time.sleep(self.timeout)
      GPIO.output(self.pin, GPIO.LOW)

class SimulatedDoor():
  def __init__(self):
      logging.info("Using simulated door")
  def open(self):
      logging.info("Door opened")
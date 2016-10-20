import RPi.GPIO as GPIO
import time
import atexit
import logging
from hackeriet.vending import motor

GPIO.setmode(GPIO.BCM) # Broadcom PIN numbering

selection_timeout_s = 10
motor_off_timeout_s = 30
motor_pin = 21
outputs = [5,  6, 13, 19, 26]
inputs  = [4, 27, 17, 22, 23]
ready_LED = 20
select_LED = 16
funds_LED = 12

# Set up GPIO ports
for output in outputs:
    GPIO.setup(output, GPIO.OUT, initial=GPIO.HIGH)
for inpt in inputs:
    GPIO.setup(inpt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(ready_LED, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(select_LED, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(funds_LED, GPIO.OUT, initial=GPIO.LOW)

vend_motor = motor.Motor(motor_pin, motor_off_timeout_s)
vend_motor.start()


@atexit.register
def cleanup():
    """Release resources and reset GPIO settings
    """
    GPIO.cleanup()

def ready():
    GPIO.output(ready_LED, GPIO.HIGH) 

def not_ready():
    GPIO.output(ready_LED, GPIO.LOW) 

def insufficent_funds():
    GPIO.output(funds_LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(funds_LED, GPIO.LOW)

def select_product():
    """Block waiting for user to push a selection button
    """
    GPIO.output(select_LED, GPIO.HIGH) 
    selection = -1
    selection_started = time.time()
    while selection < 0:
        for inpt in inputs:
            if GPIO.input(inpt) == GPIO.LOW:
                selection = inputs.index(inpt)
                break
        if time.time() - selection_started > selection_timeout_s:
            logging.info("Selection timed out.")
            break
    GPIO.output(select_LED, GPIO.LOW) 
    return selection

def vend_product(o):
    """Vend product
    """
    vend_motor.on()
    GPIO.output(outputs[o], GPIO.LOW)
    time.sleep(1)
    GPIO.output(outputs[o], GPIO.HIGH)
    # Noise from the engine stopping sometimes trigger unwanted keypress(?) or bounce?
    # Wait a bit before returning control
    time.sleep(3)



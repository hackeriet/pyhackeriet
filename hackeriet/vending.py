import RPi.GPIO as GPIO
import time
import atexit
import motor

GPIO.setmode(GPIO.BCM) # Broadcom PIN numbering

selection_timeout_s = 60
motor_off_timeout_s = 120
motor_pin = 21
outputs = [5,  6, 13, 19, 26]
inputs  = [4, 27, 17, 22, 23]

# Set up GPIO ports
for output in outputs:
    GPIO.setup(output, GPIO.OUT, initial=GPIO.HIGH)
for inpt in inputs:
    GPIO.setup(inpt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

motor = Motor(motor_pin, motor_off_timeout_s, GPIO)
motor.start()

@atexit.register
def cleanup():
    """Release resources and reset GPIO settings
    """
    GPIO.cleanup()

def select_product():
    """Block waiting for user to push a selection button
    """
    selection = -1
    selection_started = time.time()
    while selection < 0:
        for inpt in inputs:
            if GPIO.input(inpt) == GPIO.LOW:
                selection = inputs.index(inpt)
                break
            if time.time() - selection_started > selection_timeout_s:
                break
    return selection

def vend_product(o):
    """Vend product
    """
    motor.on()
    GPIO.output(outputs[o], GPIO.LOW)
    time.sleep(1)
    GPIO.output(outputs[o], GPIO.HIGH)
    # Noise from the engine stopping sometimes trigger unwanted keypress(?) or bounce?
    # Wait a bit before returning control
    time.sleep(2)



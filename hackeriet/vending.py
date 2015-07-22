import RPi.GPIO as GPIO
import time
import atexit

GPIO.setmode(GPIO.BCM)

outputs = [5,  6, 13, 19, 26, 21]
inputs  = [4, 27, 17, 22, 23]

for output in outputs:
    GPIO.setup(output, GPIO.OUT, initial=GPIO.HIGH)
for inpt in inputs:
    GPIO.setup(inpt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

@atexit.register
def cleanup():
    GPIO.cleanup()

def select_product():
    selection = -1
    while selection < 0:
        for inpt in inputs:
            if GPIO.input(inpt) == GPIO.LOW:
                selection = inputs.index(inpt)
                break
    return selection

def vend_product(o):
    GPIO.output(outputs[o], GPIO.LOW)
    time.sleep(1)
    GPIO.output(outputs[o], GPIO.HIGH)
    time.sleep(10)


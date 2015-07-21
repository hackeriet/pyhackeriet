import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

outputs = [5, 6, 13, 19, 26, 21]
inputs = [4, 27, 17, 22, 23]

for output in outputs:
    GPIO.setup(output, GPIO.OUT, initial=GPIO.HIGH)

for inpt in inputs:
    GPIO.setup(inpt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def select_product_fjas():
    selection = False
    for inpt in inputs:
        GPIO.add_event_detect(inpt, GPIO.RISING)
    while selection == False:
        for inpt in inputs:
            if GPIO.event_detected(inpt):
                selection = inputs.index(inpt)
    for inpt in inputs:
        GPIO.remove_event_detect(inpt)
    return selection

def select_product():
    selection = -1
    while selection < 0:
        for inpt in inputs:
            if GPIO.input(inpt) == GPIO.LOW:
                selection = inputs.index(inpt)
    print(selection)
    return selection

def vend_product(o):
    GPIO.output(outputs[o], GPIO.LOW)
    time.sleep(1)
    GPIO.output(outputs[o], GPIO.HIGH)
    time.sleep(10)

while True:
    input("Dra kort: ")
    print("Velg produkt")
    s = select_product()
    print("%d valgt" % s)
    vend_product(s)

GPIO.cleanup()


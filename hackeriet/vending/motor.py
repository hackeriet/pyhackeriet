import threading
import RPi.GPIO as GPIO
import time
import logging

class Motor(threading.Thread):
    motor_started = 0

    def __init__(self, motor, motor_off_timeout_s):
        super().__init__()
        GPIO.setup(motor, GPIO.OUT, initial=GPIO.HIGH)
        self.motor = motor
        self.motor_off_timeout_s = motor_off_timeout_s

    def on(self):
        logging.debug("Motor on requested.")
        self.motor_started = time.time()
        if not self.status():
            logging.info("Turning motor on ... ")
            GPIO.output(self.motor, GPIO.LOW)
            time.sleep(1)

    def off(self):
        logging.info("Turning motor off ... ")
        GPIO.output(self.motor, GPIO.HIGH)

    def status(self):
        if GPIO.input(self.motor) == GPIO.LOW:
            return True
        return False

    def run(self):
        while True:
            if self.status() and time.time()-self.motor_started > self.motor_off_timeout_s:
                self.off()
            time.sleep(1)


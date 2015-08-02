import threading
class Motor(threading.Thread):
    motor_started = 0

    def __init__(self, motor, motor_off_timeout_s, GPIO):
        GPIO.setup(motor, GPIO.OUT, initial=GPIO.HIGH)
        self.motor = motor
        self.motor_off_timeout_s = motor_off_timeout_s
        self.GPIO = GPIO

    def on(self):
        self.motor_started = time.time()
        if not status():
            GPIO.output(self.motor, GPIO.LOW)
            time.sleep(1)

    def off(self):
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


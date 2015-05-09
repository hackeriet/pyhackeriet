import time
import pifacedigitalio

piface = pifacedigitalio.PiFaceDigital() 

def open():
    piface.output_pins[1].turn_on()
    time.sleep(0.5)
    piface.output_pins[1].turn_off()


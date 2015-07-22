import time
import pifacedigitalio

piface = pifacedigitalio.PiFaceDigital() 

def open():
    piface.output_pins[0].turn_on()
    time.sleep(1)
    piface.output_pins[0].turn_off()


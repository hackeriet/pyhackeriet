import zmqclient
import zmq
import pifacedigitalio
import time

pub = zmqclient.pub()
pifacedigital = pifacedigitalio.PiFaceDigital()

value = ""

def send(s):
    print(s)
    pub.send(b"HUMLA", zmq.SNDMORE)
    pub.send_string(s)

while True:
    n = pifacedigital.input_pins[0].value
    if n != value:
        value = n
        if n == 0:
            send("OPEN")
            pifacedigital.output_pins[2].turn_on()
        else:
            send("closed")
            pifacedigital.output_pins[2].turn_off()
    time.sleep(1)

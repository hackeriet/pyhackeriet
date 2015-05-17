#!/usr/bin/env python
import zmqclient
import zmq
import pifacedigitalio
import time

piface = pifacedigitalio.PiFaceDigital() 

sub = zmqclient.sub()
sub.setsockopt(zmq.SUBSCRIBE, b"DING")

def ringBell():
    print("ding")
    piface.output_pins[1].turn_on()
    time.sleep(0.5)
    piface.output_pins[1].turn_off()

while True:
    try:
        msg = sub.recv_multipart()
        ringBell()        
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            break
        else:
            raise

ctx.term()


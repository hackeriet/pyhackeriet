import zmqclient
import zmq
import sys
import time

pub = zmqclient.pub()

def send(s):
    time.sleep(5)
    pub.send(b"HUMLA", zmq.SNDMORE)
    pub.send_string(s)
    time.sleep(5)

send(sys.argv[1])


import logging
import zmqclient
import zmq

level=logging.DEBUG
logging.basicConfig(level=level, format="[%(levelname)s] %(message)s")

pub = zmqclient.pub()
import time
time.sleep(3)

pub.send(b"DING", zmq.SNDMORE)
pub.send_string("Hello tut fjas")



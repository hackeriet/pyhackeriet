#!/usr/bin/env python
import zmqclient
import zmq

sub = zmqclient.sub()
sub.setsockopt(zmq.SUBSCRIBE, b"")

while True:
    print("tut")
    try:
        msg = sub.recv_multipart()
        print(msg)
    except zmq.ZMQError as e:
        if e.errno == zmq.ETERM:
            break
        else:
            raise

ctx.term()


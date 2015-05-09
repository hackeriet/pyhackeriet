#!/usr/bin/env python3

import sys
sys.path.append('..')

import zmq
import zmqclient

from flask import Flask, render_template, request
app = Flask(__name__)

pub = zmqclient.pub()
global humla
humla = "unknown"

from threading import Thread
def zmq_listener():
    sub = zmqclient.sub()
    sub.setsockopt(zmq.SUBSCRIBE, b"HUMLA")
    while True:
        print("ding")
        s, msg = sub.recv_multipart()
        global humla
        humla = msg.decode('utf-8')
        print(humla)

t = Thread(target=zmq_listener)
t.start()

@app.route("/humla")
def tut():
    return humla

@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == 'POST':
        if request.form['person']:
            person = request.form['person']
        else:
            person = '<anonymous>'

        addr = request.remote_addr
        try:
            if addr == "::1" or addr == "localhost" or addr == "127.0.0.1" and request.headers['x-forwarded-for']:
                addr = request.headers['x-forwarded-for']
        except KeyError:
            ""

        pub.send(b"DING", zmq.SNDMORE)
        pub.send_string("%s <%s>" % (person, addr))

        return render_template('knocked.html')

    else:
        return render_template('index.html', humla=humla)


if __name__ == "__main__":
    app.run(port=5001)

#!/usr/bin/env python3

import sys
sys.path.append('..')

import random

import zmq
import zmqclient

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

pub = zmqclient.pub()
global humla
humla = "unknown"
global topic
topic = "_"

from threading import Thread
def zmq_listener():
    sub = zmqclient.sub()
    sub.setsockopt(zmq.SUBSCRIBE, b"HUMLA")
    sub.setsockopt(zmq.SUBSCRIBE, b"TOPIC")
    while True:
        s, msg = sub.recv_multipart()
        print(s)
        print(msg)
        if s == b"TOPIC":
            global topic
            topic = msg.decode('utf-8')
        else:
            global humla
            humla = msg.decode('utf-8')
        print(humla)

t = Thread(target=zmq_listener)
t.start()

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.max_age = 0
    return response

@app.route("/hackeriet.gif")
def gif():
    n = random.choice([1,2,3,4,5,6])
    if humla == "OPEN":
        return redirect("/static/img/open/" + str(n) + ".gif")
    else:
        return redirect("/static/img/closed/" + str(n) + ".gif")

@app.route("/humla")
def tut():
    return humla

@app.route("/topic.jsonp")
def topictut():
    t = "hackerietTopic(\"" + topic + "\")"
    return t, 200, {'Content-Type': 'application/javascript'}

@app.route("/", methods=["GET", "POST"])
def hello():
    addr = request.remote_addr
    if addr == "::1" or addr == "localhost" or addr == "127.0.0.1" and 'X-Forwarded-For' in request.headers:
        addr = request.headers['X-Forwarded-For']

    if request.method == 'POST':
        if request.form['person']:
            person = request.form['person']
        else:
            person = ''

        
        pub.send(b"DING", zmq.SNDMORE)
        pub.send_string("%s <%s>" % (person, addr))

        return render_template('knocked.html')

    else:
        return render_template('index.html', humla=humla)


if __name__ == "__main__":
    app.debug = True
    app.run(port=5001)

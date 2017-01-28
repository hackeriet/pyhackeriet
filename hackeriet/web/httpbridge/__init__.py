#!/usr/bin/env python3

import sys
import random, time
from hackeriet.mqtt import MQTT

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

global humla
humla = "unknown"
global topic
topic = "_"
lastupdate = int(time.time())

def space_state(mosq, obj, msg):
    global humla
    lastupdate = int(time.time())
    humla = msg.payload.decode()

mqtt = MQTT(space_state)
mqtt.subscribe("hackeriet/space_state", 0)
#mqtt.subscribe("hackeriet/topic", 0)



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

@app.route("/door.json")
def door_json():
    t = "{ \"status\": \"%s\" }" % humla
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

        mqtt("hackeriet/ding", "%s <%s>" % (person, addr))

        return render_template('knocked.html')
    else:
        return render_template('index.html', humla=humla)

@app.route("/spaceapi.json")
def spaceapi():
  open="true" if humla is "OPEN" else "false"
  return render_template('spaceapi.json', humla=humla, open=open, lastupdate=lastupdate)

def main():
    #app.debug = True
    app.run(port=5001)

if __name__ == "__main__":
    main()

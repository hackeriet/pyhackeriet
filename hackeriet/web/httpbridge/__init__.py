#!/usr/bin/env python3

import sys
import random, time
from hackeriet.mqtt import MQTT
import nacl, base64
from nacl.public import PublicKey, SealedBox
import json

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

# TODO: change data type for `humla` so it doesn't depend on being global
# maybe make a class?
# also, pick a more descriptive name such as `space_state`
global humla
humla = "unknown"
global topic
topic = "_"
lastupdate = int(time.time())

# TODO: please don't hardcode encryption keys in a public repo
# TODO: put this in a .env file not included in the repository
def encrypt(s, pk_b64="AH1Es2z7G5q0S0wKPdKnGbie8ueeB8hfZzU6aQqyuBw="): # hackerpass ding-ip-secret-key
    box = SealedBox(PublicKey(base64.b64decode(pk_b64)))
    enc = box.encrypt(s)
    return(base64.urlsafe_b64encode(enc).decode('ascii'))


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

# these gifs are just 1x1 pictures of nothing
# what is the point of this?
@app.route("/hackeriet.gif")
def gif():
    n = random.choice([1,2,3,4,5,6])
    if humla == "OPEN":
        return redirect(f"/static/img/open/{n}.gif")
    else:
        return redirect(f"/static/img/closed/{n}.gif")

@app.route("/humla")
def tut():
    return humla

@app.route("/topic.jsonp")
def topictut():
    t = f'hackerietTopic("{topic}")'
    return t, 200, {'Content-Type': 'application/javascript'}

@app.route("/door.json")
def door_json():
    body = {"status":humla.lower(), "is_open":humla=="OPEN"}
    t = json.dumps(body)
    return t, 200, {'Content-Type': 'application/javascript'}

@app.route("/", methods=["GET", "POST"])
def hello():
    addr = request.remote_addr

    if addr in ("::1", "localhost", "127.0.0.1") and 'X-Forwarded-For' in request.headers:
        addr = request.headers['X-Forwarded-For']
    
    timeout = 60*30 # 30 minutes old pages will be ignored
    time = int(request.form['time'] or 0)

    if request.method == 'POST' and time > time.time() - timeout:
        person = request.form['person'] or ''
        mqtt("hackeriet/ding", "%s <%s>" % (person, encrypt(bytes(addr,"ascii"))))
        return render_template('knocked.html')
    else:
        response = render_template('index.html', humla=humla, time=int(time.time()))
        response.headers['Refresh'] = timeout
        return response

# this endpoint stopped updating in april of 2025?
# TODO: fix this
@app.route("/spaceapi.json")
def spaceapi():
  is_open = ["false","true"][humla == "OPEN"]
  return render_template('spaceapi.json', humla=humla, open=is_open, lastupdate=lastupdate)

def main():
    #app.debug = True
    app.run(port=5001)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import sys
import random, time
from hackeriet.mqtt import MQTT
import nacl, base64
from nacl.public import PublicKey, SealedBox
import json
import os

from flask import Flask, render_template, request, redirect, Response
app = Flask(__name__)

from .spacestate import SpaceState

space_state = SpaceState()

# TODO: please don't hardcode encryption keys in a public repo
# TODO: put this in a .env file not included in the repository
def encrypt(s, pk_b64="AH1Es2z7G5q0S0wKPdKnGbie8ueeB8hfZzU6aQqyuBw="): # hackerpass ding-ip-secret-key
    box = SealedBox(PublicKey(base64.b64decode(pk_b64)))
    enc = box.encrypt(s)
    return(base64.urlsafe_b64encode(enc).decode('ascii'))

mqtt = MQTT(space_state.mqtt_listener)
mqtt.subscribe("hackeriet/space_state", 0)
#mqtt.subscribe("hackeriet/topic", 0)



@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.max_age = 0
    return response

# TODO: make some proper error handing where the assert-statements are
@app.route("/hackeriet.gif")
def gif():
    gif_path = f"/static/img/{str(space_state).lower()}/"
    assert os.path.exists('.'+gif_path), f"Path '{gif_path}' does not exist"

    # finds all files in the directory that ends with .gif
    gifs = [*filter(
        lambda filename:not filename.endswith('.gif'),
        os.listdir('.'+gif_path)
    )]
    assert len(gifs) > 0, f"path '{gif_path}' needs at least one .gif file"
    return redirect(gif_path + random.choice(gifs))

@app.route("/humla")
def humla():
    return space_state.get_state(), 200, {'Content-Type': 'text/plain'}

@app.route("/topic.jsonp")
def topictut():
    t = f'hackerietTopic("{space_state.get_topic()}")'
    return t, 200, {'Content-Type': 'application/javascript'}

@app.route("/door.json")
def door_json():
    body = {
        "status": space_state.get_state(),
        "is_open":space_state.is_open()
    }
    t = json.dumps(body)
    return t, 200, {'Content-Type': 'application/javascript'}

@app.route("/", methods=["GET", "POST"])
def hello():
    addr = request.remote_addr

    if addr in ("::1", "localhost", "127.0.0.1") and 'X-Forwarded-For' in request.headers:
        addr = request.headers['X-Forwarded-For']
    
    timeout = 60*30 # 30 minutes old pages will be ignored

    knocker = request.args.get('p', default="", type=str)

    if request.method == 'POST':
        timestamp = int(request.form['timestamp'] or 0)
        if timestamp < time.time() - timeout:
            return redirect('/timeout', code=303)
        person = request.form['person'] or knocker
        mqtt("hackeriet/ding", "%s" % (person))
        return redirect('/knocked', code=303)
    else:
        response = Response(render_template('index.html', space_state=space_state.get_state(), time=int(time.time())))
        response.headers['Refresh'] = timeout
        return response

@app.route("/knocked", methods=["GET"])
def knocked():
    return render_template('knocked.html')

@app.route("/timeout", methods=["GET"])
def timeout():
    return render_template('timeout.html')


@app.route("/spaceapi.json")
def spaceapi():
    """ just render whole spaceapi here, return dict that automagically is json"""
    state = space_state.get_state()
    is_open = True if space_state.is_open() else False
    lastupdate = space_state.get_lastupdate_time()
    api = {
           "space" : "Hackeriet",
           "contact" : {
              "mastodon" : "@hackeriet@chaos.social",
              "email" : "styret@__SOPPELPOST__hackeriet.no",
              "irc" : "irc://irc.libera.chat/#oslohackerspace"
           },
           "logo" : "https://hackeriet.no/comotion-sjn-transparent-1.2.svg",
           "url" : "https://hackeriet.no",
           "state" : {
              "message" : f"The space is {state}.",
              "open" : is_open,
              "lastchange" : lastupdate
           },
           "location" : {
              "lat" : 59.919293,
              "lon" : 10.753475,
              "address" : "Hausmania, Hausmannsgate 34, 0182 Oslo, Norway",
              "timezone" : "Europe/Oslo",
              "country_code" : "NO",
              "hint" : "Go in main hausmania door, ring our doorbell at https://door.hackeriet.no/"
           },
           "api_compatibility" : ["14","15"],
           "feeds" : {
              "blog" : {
                 "type" : "rss",
                 "url" : "http://blog.hackeriet.no/feed.xml"
              }
           }
        }
    return api


def main():
    #app.debug = True
    app.run(port=5001)

if __name__ == "__main__":
    main()

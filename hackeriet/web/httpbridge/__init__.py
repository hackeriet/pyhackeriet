#!/usr/bin/env python3

import sys
import random, time
from hackeriet.mqtt import MQTT
import nacl, base64
from nacl.public import PublicKey, SealedBox
import json

from flask import Flask, render_template, request, redirect
app = Flask(__name__)

from spacestate import SpaceState

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

    if request.method == 'POST':
        timestamp = int(request.form['timestamp'] or 0)
        if timestamp < time.time() - timeout:
            return redirect('/timeout', code=303)
        person = request.form['person'] or ''
        mqtt("hackeriet/ding", "%s <%s>" % (person, encrypt(bytes(addr,"ascii"))))
        return redirect('/knocked', code=303)
    else:
        response = render_template('index.html', space_state=space_state.get_state(), time=int(time.time()))
        response.headers['Refresh'] = timeout
        return response

@app.route("/knocked", methods=["GET"])
def knocked():
    return render_template('knocked.html')

@app.route("/timeout", methods=["GET"])
def knocked():
    return render_template('timeout.html')

# this endpoint stopped updating in april of 2025?
# TODO: fix this

@app.route("/spaceapi.json")
def spaceapi():
  return render_template(
    'spaceapi.json',
    space_state=space_state.get_state(),
    is_open=space_state.is_open(),
    lastupdate=space_state.get_lastupdate_time())

def main():
    #app.debug = True
    app.run(port=5001)

if __name__ == "__main__":
    main()

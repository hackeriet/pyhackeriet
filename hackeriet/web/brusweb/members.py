from os import getenv
import json, urllib
from base64 import b64encode
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import hashlib
from .brusdb import get_all_usernames as get_all_brus_usernames
from .brusdb import create_new_user as create_new_brus_user

users = {}

def load():
    global users
    url_str = getenv("MEMBERS_URL", "https://foo:bar@hackeriet.no/hula/member/all_members.json")
    url = urlparse(url_str)

    req = Request(url.scheme + "://" + url.hostname + url.path)
    req.add_header('Authorization', 'Basic {}'.format(
        b64encode((url.username + ":" + url.password).encode()).decode()))
    users = json.loads(urlopen(req).read().decode())

    # Create a brus user for all hackeriet members who doesn't have one
    # TODO: Auto-refresh while running, to avoid having to restart process to reload
    brus_usernames = get_all_brus_usernames()
    for user in [ u for u in users if u["username"] not in brus_usernames ]:
        create_new_brus_user(username=user["username"], email=user["email"])
        print("Created new brus user for %s" % user["username"])


def hash_password(p, salt, iters):
    return b64encode(hashlib.pbkdf2_hmac('sha256', p.encode(),
                                         salt.encode(), iters)).decode()

def authenticate(username, password):
    for u in users:
        if u['username'] == username:
            method, iters, salt, phash = u['password'].split("$", 4)
            if phash == hash_password(password, salt, int(iters)):
                return True
    return False


def authenticate_admin(username, password):
    return authenticate(username, password) and username == "krav"

def username_from_card(card):
    for u in users:
        if u['access_card'] == card:
            return u['username']
    return ''

def get_email(user):
    for u in users:
        if u['username'] == user:
            return u['email']
    return ""

def list_users():
    s = []
    for u in users:
        s.append(u['username'])
    return s


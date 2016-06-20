#!/usr/bin/env python3

import logging, re, sys, signal, getopt
import zmq, zmqclient
import json, http.client
from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError


try:
    opts, args = getopt.getopt(sys.argv[1:], "u:p:g:d", ["user=", "pass=", "github="])
except getopt.GetoptError as err:
    print(err)

loglvl = logging.INFO
MATRIX_USER = None
MATRIX_PASS = None
GITHUB_TOKEN = ""

for o, a in opts:
    if o == "-d":
        loglvl = logging.DEBUG
    elif o in ("-u", "--user="):
        MATRIX_USER = a
    elif o in ("-p", "--pass="):
        MATRIX_PASS = a
    elif o in ("-g", "--github="):
        GITHUB_TOKEN = a

assert MATRIX_USER, "Username required"
assert MATRIX_PASS, "Password required"

MATRIX_URL = "https://matrix.hackeriet.no:8448"
MATRIX_ROOM = "#hackeriet:hackeriet.no"
MSG_MAX_AGE = 30000

def sigint_handler(signal, frame):
    print('Interrupted')
    sys.exit(0)
signal.signal(signal.SIGINT, sigint_handler)

logger = logging.getLogger('matrixbridge')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

sub = zmqclient.sub()
pub = zmqclient.pub()
zmq_poller = zmq.Poller()

commands={}
events={}


def zmq_setup():
    sub.setsockopt(zmq.SUBSCRIBE, b"")
    zmq_poller.register(sub, zmq.POLLIN)

def matrix_setup():
    global client, room
    client = MatrixClient(MATRIX_URL)
    token = client.login_with_password(username=MATRIX_USER,password=MATRIX_PASS)
    room = client.join_room(MATRIX_ROOM)
    room.add_listener(msg_handler)

def zmq_listen():
    evts = dict(zmq_poller.poll(1000))
    for e in evts:
        s, msg = e.recv_multipart() # FIXME check for non-multipart messages
        s = s.decode('utf-8')
        msg = msg.decode('utf-8')
        logger.info('ZMQ: {} {}'.format(s, msg))
        if s in events:
            events[s](msg)

def run():
    zmq_setup()
    matrix_setup()
    while True:
        zmq_listen()
        try:
            client.listen_for_events(1000)
        except MatrixRequestError as e:
            print(e)

def get_command(msg):
    m = re.search('^!(\w*) ?(.*)?', msg)
    if m:
        return m.groups()
    return ('', '')

def msg_handler(c):
    logger.debug(c)
    if 'content' in c and 'msgtype' in c['content'] and c['content']['msgtype'] == 'm.text':
        if c['age'] > MSG_MAX_AGE:
            return
        sender = c['sender']
        body = c['content']['body']
        logger.info('{}: {}'.format(sender, body))
        cmd, content = get_command(body)
        if cmd and cmd in commands:
            commands[cmd](sender, content, c)

def add_command(trigger, func):
    commands.update({trigger: func})

def add_event(trigger, func):
    events.update({trigger: func})

def notice(msg):
    room.send_notice(msg)

# Matrix handler helpers

def create_github_issue(token, title, owner="hackeriet", repo="nfcd", assignee=""):
  target = "/repos/{}/{}/issues".format(owner, repo)
  msg = {"title": title, "assignee": assignee}
  headers = {"User-Agent": "Matrixbot",
             "Authorization": "token {}".format(token)}

  github = http.client.HTTPSConnection("api.github.com")
  github.request("POST", target, body=json.dumps(msg), headers=headers)
  resp = github.getresponse()
  result = json.loads(resp.read().decode('utf8'))

  if resp.code == 201:
    return "Issue #{} created: {}".format(result['number'], result['html_url'])
  else:
    return "Error: {}".format(result['message'])

# Matrix handlers
def github_handler(sender, content, c):
    owner = "hackeriet"
    if not " " in content:
        return
    repo, title = content.split(" ", 1)
    if "/" in repo:
        owner, repo = repo.split("/", 1)
    notice(create_github_issue(GITHUB_TOKEN, title, owner, repo))

def zmq_handler(sender, content, c):
    if len(content) < 1:
        return
    if not " " in content:
        content += " "
    cmd, rest = content.split(" ", 1)
    print("zmq send: {} / {} ".format(cmd, rest))
    pub.send(bytes(cmd, "utf-8"), zmq.SNDMORE)
    pub.send_string(rest)

add_command('zmq', zmq_handler)
add_command('0mq', zmq_handler)
add_command('zomg', zmq_handler)
add_command('github', github_handler)
add_command('g', github_handler)

# ZMQ handlers
def ding_event(msg):
    if msg:
        notice("DING DONG from {}".format(msg))
    else:
        notice("DING DONG")

def humla_event(msg):
    room.update_room_topic()
    print("Topic: " + room.topic)
    if room.topic is None:
        room.topic = ""
    new_topic = re.sub(r'(The space is:) \w*\. \| (.*)', '\g<1> ' + msg + '. | \g<2>', room.topic)
    print("New Topic: " + new_topic)
    if new_topic != room.topic:
        print("update")
    room.topic = new_topic
    client.api.send_state_event(room.room_id, "m.room.topic", {"topic": new_topic})

add_event('DING', ding_event)
add_event('HUMLA', humla_event)

run()

#!/usr/bin/env python

import bottom
import asyncio
import zmq
import zmqclient
import re

bottom.unpack._2812_synonyms['TOPIC'] = 'RPL_MYINFO'

NICK = 'club_mate'
CHANNEL = '#oslohackerspace'

bot = bottom.Client('irc.freenode.net', 6697)

pub = zmqclient.pub()
topic = ""

@bot.on('CLIENT_DISCONNECT')
def disco():
     yield from bot.connect()
     
@bot.on('CLIENT_CONNECT')
def connect():
    bot.send('NICK', nick=NICK)
    bot.send('USER', user=NICK, realname='Bot using bottom.py')
    bot.send('JOIN', channel=CHANNEL)

@bot.on('PING')
def keepalive(message):
    bot.send('PONG', message=message)

@bot.on('PRIVMSG')
def message(nick, target, message):
    if nick == NICK:
        return
    print(nick, target, message)

@bot.on("RPL_TOPIC")
def test(channel, message):
    global topic
    topic = message
    pub.send(b"TOPIC", zmq.SNDMORE)
    pub.send_string(topic)

@bot.on("RPL_MYINFO")
def fjas(message, info):
    bot.send('TOPIC', channel=CHANNEL)

@bot.on('client_disconnect')
def reconnect():
    # Wait a few seconds
    yield from asyncio.sleep(3)
    yield from bot.connect()

def flip_topic(status):
    return re.sub(r'(The space is:) \w*\. \| (.*)', '\g<1> ' + status + '. | \g<2>', topic)

# TODO use async io
from threading import Thread
def run_zmq():
    sub = zmqclient.sub()
    sub.setsockopt(zmq.SUBSCRIBE, b"DING")
    sub.setsockopt(zmq.SUBSCRIBE, b"HUMLA")
    while True:
        s, msg = sub.recv_multipart()
        print(s, msg)
        if s == b"DING":
            if msg == b"":
                bot.send('NOTICE', target=CHANNEL, message="DING DONG")
            else:
                bot.send('NOTICE', target=CHANNEL, message="DING DONG from " + msg.decode('utf-8'))
        elif s == b"HUMLA":
            t = flip_topic(msg.decode('utf-8'))
            print(t)
            if t != topic:
                bot.send('TOPIC', channel=CHANNEL, message=t)

t = Thread(target=run_zmq)
t.start()

asyncio.get_event_loop().run_until_complete(bot.run())




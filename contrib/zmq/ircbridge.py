#!/usr/bin/env python

import bottom
import asyncio
import zmq
import zmqclient
import re
import socket
from threading import Thread
import os

bottom.unpack._2812_synonyms['TOPIC'] = 'RPL_MYINFO'

NICK = 'club_mate'
CHANNEL = '#oslohackerspace'

bot = bottom.Client('irc.freenode.net', 6697)

pub = zmqclient.pub()
topic = ""

@bot.on('CLIENT_DISCONNECT')
def disco():
    os._exit(1)
    # yield from bot.connect()
     
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
                m = msg.decode('utf-8')
                bot.send('NOTICE', target=CHANNEL, message="DING DONG from " + m)

                ip = bytes(" -v " + re.sub('.*<([^>]*)>', '\g<1>', m) + "\n", 'utf-8')
                sock = socket.create_connection( ("whois.cymru.com",43), 10)
                sock.sendall(ip)
                r = sock.recv(4096).decode('utf-8')
                sock.close()
                lines = r.splitlines()

                if len(lines) > 1:
                    asn, ip, prefix, cc, registry, allocated, as_name = lines[1].strip().split('|')
                    bot.send('NOTICE', target=CHANNEL, message="This ding brought to you by " + as_name)

        elif s == b"HUMLA":
            t = flip_topic(msg.decode('utf-8'))
            print(t)
            if t != topic:
                bot.send('TOPIC', channel=CHANNEL, message=t)

t = Thread(target=run_zmq)
t.start()

asyncio.get_event_loop().run_until_complete(bot.run())




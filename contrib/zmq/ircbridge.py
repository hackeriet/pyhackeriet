#!/usr/bin/env python

import bottom
import asyncio
import zmq
import zmqclient

NICK = 'club2mate'
CHANNEL = '#oslohackerspacetest'

bot = bottom.Client('irc.freenode.net', 6697)

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
    print(nick, target, message)

from threading import Thread
def run_zmq():
    import zmqclient
    sub = zmqclient.sub()
    sub.setsockopt(zmq.SUBSCRIBE, b"DING")
    while True:
        s, msg = sub.recv_multipart()
        print(s)
        bot.send('NOTICE', target=CHANNEL, message="DING DONG from " + msg.decode('utf-8'))

t = Thread(target=run_zmq)
t.start()

asyncio.get_event_loop().run_until_complete(bot.run())




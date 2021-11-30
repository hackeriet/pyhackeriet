"""
MQTT wrapper for hackeriet

Uses MQTT_URL environment variable or default test channel

Start subscribe, with QoS level 0
>>> mqtt.subscribe("hello/world", 0)

Act on messages by setting a on_message callback.

Publish
>>> mqtt("hello/world", "alarm!!!")
"""

import paho.mqtt.client as paho
from urllib.parse import urlparse
import os, socket, sys, ssl


class MQTT(object):
    subscriptions = []
    def __init__(self, on_message=False):
        """
        """
        self.mqttc = paho.Client()
        # Assign event callbacks
        self.mqttc.on_message = on_message or MQTT.on_message
        self.mqttc.on_connect = MQTT.on_connect
        self.mqttc.on_publish = MQTT.on_publish
        self.mqttc.on_subscribe = MQTT.on_subscribe

        # Uncomment to enable debug messages
        #mqttc.on_log = on_log

        # Parse CLOUDMQTT_URL (or fallback to localhost)
        url_str = os.environ.get('MQTT_URL', 'mqtt://rfujhjpb:AxJyUNkkQrxv@m20.cloudmqtt.com:15014')
        url = urlparse(url_str)

        # Connect
        self.mqttc.username_pw_set(url.username, url.password)
        self.mqttc.tls_set("/etc/ssl/certs/ca-certificates.crt", tls_version=ssl.PROTOCOL_TLSv1_2) 
        self.mqttc.connect(url.hostname, url.port)
        self.mqttc.loop_start()

        # Publish a message
        self.mqttc.publish("hello/world", "Started {} on {}".format(sys.argv[0], socket.gethostname()))

    def __call__(self,*a):
        self.publish(*a)

    def publish(self, *a):
        self.mqttc.publish(*a)

    def subscribe(self,*a):
        self.mqttc.subscribe(a)
        MQTT.subscriptions.append(a)

    # Define default event callbacks
    # HACK: Do not know what the last param is supposed to be
    def on_connect(mosq, obj, rc, bogus):
        print("MQTT connected ({})".format(rc))

        # Renew on reconnection
        for t in MQTT.subscriptions:
            mosq.subscribe(t)

    def on_message(mosq, obj, msg):
        print("MQTT {} ({}): {}".format(msg.topic, msg.qos, msg.payload))

    def on_publish(mosq, obj, mid):
        print("MQTT Published message #{}".format(mid))

    def on_subscribe(mosq, obj, mid, granted_qos):
        print("MQTT Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(mosq, obj, level, string):
        print(string)


if __name__ == '__main__':
    mqtt = MQTT(lambda mosq, obj, msg: print(msg.payload.decode()))
    mqtt.subscribe("hello/world", 0)
    mqtt("hello/world", "piss")
    import time
    while True:
        time.sleep(1)

import time

"""
This class is a utility to make us not have to rely on a global string value
to determine the state of the space in the logic of the doorbell.

The class contains string and boolean representation of the state of the space, as
well as last update time as an integer, and a string for the topic

This class is a bit of a sausage factory, but I tried to provide commentary
to make it easy to understand.
"""
class SpaceState:
    # enums
    OPEN = "OPEN"
    CLOSED = "closed"
    UNKOWN = "unknown"
    def __init__(self, initial_state="unknown", topic="_"):
        self._state = initial_state
        self._lastupdate = int(time.time())
        self.update_isopen()
        self._topic = topic
    
    # method to be called through MQTT
    def mqtt_listener(self, mosq, obj, msg):
        message = msg.payload.decode()
        self.set_state(message)
    
    # methods for updating the internal states
    def update_isopen(self):
        self._is_open = self._state == self.OPEN
    def update_lastupdate_time(self):
        self._lastupdate = int(time.time())
    def set_state(self, new_state):
        self._state = new_state
        self.update_isopen()
        self.update_lastupdate_time()
    def set_topic(self):
        return self._topic
    
    # methods for getting the internal states
    def get_state(self):
        return self._state
    def is_open(self):
        return self._is_open
    def get_lastupdate_time(self):
        return self._lastupdate
    def get_topic(self):
        return self._topic
    
    # allows you to toggle between the space being opened and closed
    def toggle(self):
        [self.open,self.close][self._is_open]()
    
    # functions for opening and closing the space
    def open(self):
        self.set_state(self.OPEN)
    def close(self):
        self.set_state(self.CLOSED)
    def __repr__(self):
        return f'SpaceState(state={self._state}, lastupdate={self._lastupdate}, topic={self._topic})'
    
    # these makes it possible to cast the object as string and boolean types
    def __str__(self):
        return self._state
    def __bool__(self):
        return self._is_open

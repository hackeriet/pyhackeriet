import os
import uuid
import zmq
import zmq.auth

base_dir = os.path.dirname(__file__)
keys_dir = os.path.join(base_dir, '..', '..', 'keys/')
#basename = os.path.basename(__file__) + "_" + str(uuid.getnode())
basename = str(uuid.getnode())
private_key = os.path.join(keys_dir, basename + ".key_secret")

if not (os.path.exists(private_key)):
    if not (os.path.exists(keys_dir)):
        os.makedirs(keys_dir)
    zmq.auth.create_certificates(keys_dir, basename)

ctx = zmq.Context()

server_key = os.path.join(keys_dir, "server.key")
curve_publickey, curve_secretkey = zmq.auth.load_certificate(private_key)
curve_serverkey, _ = zmq.auth.load_certificate(server_key)

def sub():
    s = ctx.socket(zmq.SUB)
    s.curve_publickey = curve_publickey
    s.curve_secretkey = curve_secretkey
    s.curve_serverkey = curve_serverkey
    s.connect("tcp://mccarthy.microdisko.no:5566")
    return s

def pub():
    s = ctx.socket(zmq.PUB)
    s.curve_publickey = curve_publickey
    s.curve_secretkey = curve_secretkey
    s.curve_serverkey = curve_serverkey
    s.connect("tcp://mccarthy.microdisko.no:5555")
    return s


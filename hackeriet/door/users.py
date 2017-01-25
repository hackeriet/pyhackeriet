import hashlib, json

tokens = {}
dooraccess = "/etc/dooraccess"

def load():
  global tokens
  a = json.loads(open(dooraccess).read())
  tokens = {v['access_token']: v for v in a}

def auth(data):
  token = sha256hash(data)
  if token in tokens:
    return tokens[token]['contactinfo']

def sha256hash(string):
  if type(string) is str:
    s = string.encode()
  else:
    s = string
  return hashlib.sha256(s).hexdigest()



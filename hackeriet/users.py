import hashlib, json

tokens = {}
dooraccess = "/opt/nfcd/dooraccess"

def load():
  global tokens
  a = json.loads(open(dooraccess).read())
  tokens = {v['access_token']: v for v in a}

def auth(data):
  token = sha256hash(data)
  if tokens[token]:
    return tokens[token]['contactinfo']

def sha256hash(string):
  if type(string) is str:
    s = string.encode()
  else:
    s = string
  return hashlib.sha256(s).hexdigest()



import os.path, time, urllib, hashlib

def sha256hash(self, string):
  if type(string) is str:
    s = string.encode()
    else:
      s = string
    return hashlib.sha256(s).hexdigest()


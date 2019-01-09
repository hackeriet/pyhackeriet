#!/usr/bin/env python3

import sys, nacl, base64
from nacl.public import PublicKey, PrivateKey, SealedBox

# Usage:
#   hackerpass show ding-ip-secret-key | ./decrypt-ip.py <encrypted-ip>

def decrypt(s_b64, sk_b64):
    box = SealedBox(PrivateKey(base64.b64decode(sk_b64)))
    dec = box.decrypt(base64.urlsafe_b64decode(s_b64))
    return(dec)


sk = None 
for line in sys.stdin: 
        sk = line.rstrip()

d = decrypt(sys.argv[1], sk)
print(d)

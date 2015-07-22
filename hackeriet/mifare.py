#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nfc
import atexit

MC_AUTH_A = 0x60
MC_AUTH_B = 0x61
MC_READ = 0x30
MC_WRITE = 0xA0
MC_TRANSFER = 0xB0
MC_DECREMENT = 0xC0
MC_INCREMENT = 0xC1
MC_STORE = 0xC2

defaultKeys = [
    bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    bytearray([0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
]

keyA = bytearray([0xf0, 0x0f, 0x00, 0xf0, 0x0f, 0x00])
keyB = bytearray([0xac, 0xab, 0xac, 0xab, 0xac, 0xab])

# Access conditions
#    3210
c1=0b0111
c2=0b1111
c3=0b1000

def compute_access_bits(c1, c2, c3):
    byte6=((~c2 & 0xf) << 4)+(~c1 & 0xf)
    byte7=(c1 << 4)+(~c3 & 0xf)
    byte8=(c3 << 4)+(c2)
    return bytearray([byte6, byte7, byte8, 0b1101001])

def is_trailer_block(block):
    if block < 128:
        return (block + 1) % 4 == 0
    else:
        return (block + 1) % 16 == 0

def is_first_block(block):
    if block < 128:
        return (block) % 4 == 0
    else:
        return (block) % 16 == 0

def nfc_initiator_mifare_cmd(pnd, mc, block_idx, mp):
    if mc in [MC_READ, MC_STORE]:
        sz_len = 0
    elif mc in [MC_AUTH_A, MC_AUTH_B]:
        sz_len = 10 # sizeof(mifare_param_auth)
    elif mc is MC_WRITE:
        sz_len = 16
    elif mc in [MC_DECREMENT, MC_INCREMENT, MC_TRANSFER]:
        raise BaseException("?")
    else:
        raise BaseException("no such command")

    if nfc.device_set_property_bool(pnd, nfc.NP_EASY_FRAMING, True) < 0:
        raise BaseException(nfc.strerror(pnd))

    abt_rx = 256
    abt_cmd = bytearray(abt_rx)
    abt_cmd[0] = mc
    abt_cmd[1] = block_idx
    for i, v in zip(range(2, 256), mp):
        abt_cmd[i] = v
    (ret, data) = nfc.initiator_transceive_bytes(pnd, abt_cmd, 2 + sz_len, abt_rx, -1)
    if ret < 0:
        print("tx failed: %s" % (nfc.strerror(pnd)))
        return (False, [])

    if mc == MC_READ:
        if ret == 16:
            return (True, data[0:16])
        else:
            return (False, [])

    return (True, [])

# Try different keys, for writing
def try_authenticate(block):
  keys = [(MC_AUTH_B, keyB)] + \
         [(MC_AUTH_A,k) for k in defaultKeys] + [(MC_AUTH_B,k) for k in defaultKeys] + [(MC_AUTH_A, keyA)]

  for key, key_data in keys:
    res = authenticate(block, key, key_data)
    if res:
        break
    else:
        ret = nfc.initiator_select_passive_target(pnd, nmMifare, 0, 0, nt)
        print(ret)
        print("reopen")

def authenticate(block_num, key, key_data):
    uid = nt.nti.nai.abtUid[0:nt.nti.nai.szUidLen]
    data = key_data + uid
    (res, data) = nfc_initiator_mifare_cmd(pnd, key, block_num, data)
    if res:
        return res
    print(nfc.strerror(pnd))
    return res

def read_sector(sector):
    # sectors > 15 are larger
    s=((sector+1)*4)-1
    res = []
    for block in range(s, s-4, -1):
        mp = bytearray(0)
        if is_trailer_block(block):
            authenticate(block, MC_AUTH_B, keyB)
        else:
            ret, data = nfc_initiator_mifare_cmd(pnd, MC_READ, block, mp)
            if ret:
                res.insert(0, data)
    return b"".join(res)

def write_sector(data, sector=7, key_b=False):
    n=0
    for block in range(sector*4, sector*4+4):
      if (is_first_block(block)):
        try_authenticate(block)

      if (is_trailer_block(block)):
        mp = (keyA + accessBits + keyB)
        nfc_initiator_mifare_cmd(pnd, MC_WRITE, block, mp)
      else:
        if (block != 0):
            mp = data[n:n+16]
            n=n+17
            nfc_initiator_mifare_cmd(pnd, MC_WRITE, block, mp)

def wait_card():
    while True:
        ret = nfc.initiator_select_passive_target(pnd, nmMifare, 0, 0, nt)
        if ret > -1:
            return ret

def wait_read():
    wait_card()
    return(read_sector(7))

def try_read():
    if nfc.initiator_select_passive_target(pnd, nmMifare, 0, 0, nt) > -1:
        return read_sector(7)
    
@atexit.register
def close():
  nfc.close(pnd)
  nfc.exit(context)

accessBits = compute_access_bits(c1, c2, c3)

context = nfc.init()
pnd = nfc.open(context)

if pnd is None:
    raise Exception('ERROR: Unable to open NFC device.')

if nfc.initiator_init(pnd) < 0:
    nfc.perror(pnd, "nfc_initiator_init")
    raise Exception('ERROR: Unable to init NFC device.')

print('NFC reader: %s opened' % nfc.device_get_name(pnd))

nmMifare = nfc.modulation()
nmMifare.nmt = nfc.NMT_ISO14443A
nmMifare.nbr = nfc.NBR_106

nt = nfc.target()



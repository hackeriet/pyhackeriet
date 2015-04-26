#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import nfc

MC_AUTH_A = 0x60
MC_AUTH_B = 0x61
MC_READ = 0x30
MC_WRITE = 0xA0
MC_TRANSFER = 0xB0
MC_DECREMENT = 0xC0
MC_INCREMENT = 0xC1
MC_STORE = 0xC2

print('Version: ', nfc.__version__)

keyA = bytearray([0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
keyB = bytearray([0, 0, 0, 0, 0, 0])

def is_trailer_block(block):
    if block < 128:
        return (block + 1) % 4 == 0
    else:
        return (block + 1) % 16 == 0

def nfc_initiator_mifare_cmd(pnd, mc, block_idx, mp):
    if mc in [MC_READ, MC_STORE]:
        sz_len = 0
    elif mc in [MC_AUTH_A, MC_AUTH_B]:
        sz_len = 10 # sizeof(mifare_param_auth)
    elif mc is MC_WRITE:
        raise BaseException("?")
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
        raise BaseException("tx failed: %s" % (nfc.strerror(pnd)))

    if mc == MC_READ and ret == 16:
        print(data[0:16])
        return (True, data[0:16])
    else:
        return (False, [])

def authenticate(pnd, block_num, nt):
    print(nt.nti.nai.abtUid, nt.nti.nai.szUidLen)
    key = bytearray([0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    uid = nt.nti.nai.abtUid[0:4]
    data = key + uid
    print("auth attempt", data)
    (res, data) = nfc_initiator_mifare_cmd(pnd, MC_AUTH_A, block_num, data)
    print((res, data))
    if res < 0:
        print(nfc.strerror(pnd))
    return data

def read_card(ui_block_num, pnd, nm_mifare, nt):
    mp = bytearray(0)
    previous_failure = False
    res = []
    for block in range(ui_block_num, -1, -1):
        print(block)
        if is_trailer_block(block):
            if previous_failure:
                nfc.initiator_select_passive_target(pnd, nm_mifare, 0, 0, nt)
                previous_failure = False
            authenticate(pnd, block, nt)
            ret, data = nfc_initiator_mifare_cmd(pnd, MC_READ, block, mp)
            if ret:
                res.insert(0, keyA + data[6:10] + keyB)
        else:
            if not previous_failure:
                ret, data = nfc_initiator_mifare_cmd(pnd, MC_READ, block, mp)
                if ret:
                    res.insert(0, data)
    return b"".join(res)


context = nfc.init()
pnd = nfc.open(context)
if pnd is None:
    print('ERROR: Unable to open NFC device.')
    exit()

if nfc.initiator_init(pnd) < 0:
    nfc.perror(pnd, "nfc_initiator_init")
    print('ERROR: Unable to init NFC device.')
    exit()

print('NFC reader: %s opened' % nfc.device_get_name(pnd))

nmMifare = nfc.modulation()
nmMifare.nmt = nfc.NMT_ISO14443A
nmMifare.nbr = nfc.NBR_106

nt = nfc.target()
ret = nfc.initiator_select_passive_target(pnd, nmMifare, 0, 0, nt)

print('The following (NFC) ISO14443A tag was found:')
print('    ATQA (SENS_RES): ', end='')
nfc.print_hex(nt.nti.nai.abtAtqa, 2)
id = 1
if nt.nti.nai.abtUid[0] == 8:
    id = 3
print('       UID (NFCID%d): ' % id , end='')
nfc.print_hex(nt.nti.nai.abtUid, nt.nti.nai.szUidLen)
print('      SAK (SEL_RES): ', end='')
print(nt.nti.nai.btSak)
if nt.nti.nai.szAtsLen:
    print('          ATS (ATR): ', end='')
    nfc.print_hex(nt.nti.nai.abtAts, nt.nti.nai.szAtsLen)

print("ready to read")

ui_block_num = 0x3f
ret = read_card(ui_block_num, pnd, nmMifare, nt)

with open("dump.bin", "wb") as ous:
    ous.write(ret)

nfc.close(pnd)
nfc.exit(context)

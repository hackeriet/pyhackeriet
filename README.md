# Yet Another Door Control Project Repository 

This package contains tools to open doors and dispense sodas at Hackeriet (and much more).

# Installing

    pip3 install git+https://github.com/hackeriet/pyhackeriet.git --upgrade

When upgrading an existing install already made from VCS, either force the upgrade or uninstall `pyhackeriet` prior.

Environment variables required for running are detailed in the systemd service files.

## Card reader prerequisites 

pcscd, libnfc and python bindings located in source/nfc-bindings.

# Creating a new user
## Create user in hula

https://hackeriet.no/hula

## Create a card

On the machine with the card reader put a blank card on the reader and, as root, run:

```
# MIFARE_KEY_A=<secret1> MIFARE_KEY_B=<secret2> write_card

NFC reader: ACS/ACR122U PICC Interface opened
Waiting for card
Writing card ...
Hash: <SHA256 hash>
Wrote: <some bytes>
Read: <the same bytes>
```

## Update hula

Copy the card hash to the "Access card" field.

## Update databases

The door into hackeriet will automatically download new card data every minute.
The other doors (don't really know) will automatically download card data every 60 minutes.

For brus, see the psql log on brus.hackeriet.no -- or fix the integration.

# Troubleshooting

## Card Reader not working

  * Check if it works with libnfc tools (nfc-list, nfc-mfclassic)
  * Check that it has enough power (use a USB hub)
  * On RPi make sure the firmware is current (rpi-update)
  * Try reseating it, it will fail intermittently on many rapid open attempts(?)

# Overview

![That's right](doc/overview.png)


# Yet Another Door Control Project Repository 

This package contains tools to open doors and dispense sodas at Hackeriet.


# Creating a new user
## Create user in hula
## Create a card

On the machine with the card reader put a blank card on the reader and, as root, run:

```bash
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

The doors automatically downloads card data every <never> minutes.

For brus, see the psql log on brus.hackeriet.no -- or fix the integration.
 

# TODO
  * Migrate user management and authentication to hackerhula


#!/usr/bin/env python3

from bluepy.btle import Scanner

# Direccion Bluetooth de los Arduino
scanner = Scanner()
dev = scanner.scan(10)
for d in dev:
    print("* Found: {:s} - {:s}\n".format(d.addr, d.getValueText(9)))

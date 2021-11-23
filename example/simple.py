#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import wappstoiot

network = wappstoiot.Network()
device = network.createDevice()
value = device.createValue()
value.report(5)

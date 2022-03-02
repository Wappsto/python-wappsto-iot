#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import wappstoiot

network = wappstoiot.createNetwork("TheNetwork")
device = network.createDevice("TheDevice")
value = device.createValue("TheValue", value_template=wappstoiot.ValueTemplate.STRING)
value.report(5)

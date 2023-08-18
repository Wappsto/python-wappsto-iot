#! /bin/env python3
"""
This is a working code example on the most simple device.

This Device, connects to wappsto, create a value named: `TheValue`,
set the report to be of value 5 and closes.

This code is based on the assumption that there have been
created a 'certificate files' in the 'IoT Certificate Manager' wapp.
The certificates, have then been downloaded
unpack and saved into the config-folder of you project.
"""

import wappstoiot

network = wappstoiot.createNetwork("TheNetwork")
device = network.createDevice("TheDevice")
value = device.createValue(
    "TheValue",
    permission=wappstoiot.PermissionType.READ,
    value_template=wappstoiot.ValueTemplate.STRING
)
value.report(5)

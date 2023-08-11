#! /usr/bin/env python3

"""
This code is based on the assumption that there have been
created a user on wappsto, and that it have been used to
download a certificate for a IoT unit.
AND that it is executed on a raspberry pi.

Downloading of the certificate can be done with:
'python3 -m wappstoiot --path config'
where it will promt you to login with your wappsto account.
"""
import time

import wappstoiot

from grove.grove_relay import GroveRelay


def main():
    relay_pin = 5

    relay = GroveRelay(relay_pin)
    relay_state = {
        0: relay.off,
        1: relay.on,
    }

    wappstoiot.config(
        config_folder="config"
    )

    network = wappstoiot.createNetwork(
        name="ControlPi",
    )

    device = network.createDevice(
        name="Relay"
    )

    value = device.createValue(
        name="State",
        permission=wappstoiot.PermissionType.READWRITE,
        value_template=wappstoiot.ValueTemplate.BOOLEAN_ONOFF
    )

    def relay_control(obj, new_value):
        relay_state[new_value]()
        value.report(new_value)

    value.onControl(
        callback=relay_control
    )

    value.onRefresh(
        callback=lambda obj: obj.report(obj.getReportData())
    )

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        wappstoiot.close()


if __name__ == "__main__":
    main()

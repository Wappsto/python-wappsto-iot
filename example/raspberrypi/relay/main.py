#! /usr/bin/env python3

"""
This code is based on the assumption that there have been
created a user on wappsto, and that it have been used to
download a certificate for a IoT unit.
AND that it is executed on a raspberry pi.

Downloading of the certificate can be done with the
'IoT Certificate Manager' wapp.
Download the certificates with target: 'certificate files',
then unpack and saved into the config-folder of you project.
"""
import time

import wappstoiot

from RPi import GPIO


def main():
    """."""
    relay_pin = 5

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin, GPIO.OUT)

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
        GPIO.output(relay_pin, new_value)
        value.report(GPIO.input(relay_pin))

    value.onControl(
        callback=relay_control
    )

    value.onRefresh(
        callback=lambda obj: value.report(GPIO.input(relay_pin))
    )

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        wappstoiot.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()

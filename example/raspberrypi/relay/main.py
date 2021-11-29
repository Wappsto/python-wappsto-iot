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

from RPi import GPIO


def main():
    relay_pin = 5

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin, GPIO.OUT)

    network = wappstoiot.Network(
        name="ControlPi",
        configFolder="config"
    )

    device = network.createDevice(
        name="Relay"
    )

    value = device.createValue(
        name="State",
        value_type=wappstoiot.ValueType.BOOLEAN
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
        network.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()

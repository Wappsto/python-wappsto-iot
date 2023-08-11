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
    bnt_pin = 6
    led_pin = 5

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.setup(bnt_pin, GPIO.IN)

    wappstoiot.config(
        config_folder="config"
    )

    network = wappstoiot.createNetwork(
        name="ControlPi",
    )

    device = network.createDevice(
        name="Red Led Button"
    )

    led = device.createValue(
        name="LED",
        type="Light",
        value_template=wappstoiot.ValueTemplate.BOOLEAN_ONOFF,
        permission=wappstoiot.PermissionType.WRITE,
    )

    led.onControl(
        callback=lambda obj, new_value: GPIO.output(led_pin, int(new_value))
    )

    bnt = device.createValue(
        name="Button",
        value_template=wappstoiot.ValueTemplate.BOOLEAN_ONOFF,
        permission=wappstoiot.PermissionType.READ,
    )

    bnt.onRefresh(
        callback=lambda obj: bnt.report(GPIO.input(bnt_pin))
    )

    cb_last_active = time.time()

    def bnt__callback(self, *args, **kwargs):
        # TODO: keep track for both up and down.
        nonlocal cb_last_active
        if (cb_last_active + 0.2) < time.time():
            cb_last_active = time.time()
            bnt.report(GPIO.input(bnt_pin))

    GPIO.add_event_detect(
        bnt_pin,
        GPIO.BOTH,
        callback=bnt__callback
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

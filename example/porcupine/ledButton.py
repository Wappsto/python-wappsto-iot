#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import time

from porcupineIO import GPIO

import wappstoiot


def main():

    wappstoiot.config(
        config_folder="ledButton",
        offline_storage=True
    )

    network = wappstoiot.createNetwork(
        name="ledButton",
    )

    # Setting up the LED and events handling.
    led = network.createDevice("led")
    ledValue = led.createValue(
        "on/off",
        permission=wappstoiot.PermissionType.WRITE,
        value_template=wappstoiot.ValueTemplate.BOOLEAN_ONOFF
    )
    PQPI_led = GPIO(chip=0, pin=16, state=GPIO.OUTPUT)
    ledValue.onControl(lambda obj, value: PQPI_led.write(value))

    # Setting up the Button and events handling.
    bnt = network.createDevice("button")
    bntValue = bnt.createValue(
        name="pushed",
        permission=wappstoiot.PermissionType.READ,
        value_template=wappstoiot.ValueTemplate.BOOLEAN_TRUEFALSE
    )
    PQPI_bnt = GPIO(
        chip=0,
        pin=15,
        state=GPIO.BOTH_EDGE,
        callback=lambda chip, pin, edge: bntValue.report(
            1 if edge is GPIO.FALLING_EDGE else 0
        ),
    )
    bntValue.onRefresh(callback=PQPI_bnt.read())

    while network.connectionStatus is network.connection.Status.CONNECTED:
        time.sleep(0.5)

    PQPI_bnt.close()
    PQPI_led.close()
    wappstoiot.close()


if __name__ == "__main__":
    main()

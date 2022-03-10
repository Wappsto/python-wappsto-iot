#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import time
import threading
import signal

from porcupineIO import PWM
from porcupineIO import IioControl

import wappstoiot


def main():

    killed = threading.Event()
    signal.signal(signal.SIGINT, killed.set)
    signal.signal(signal.SIGTERM, killed.set)

    period_ns = 400000

    wappstoiot.config(
        config_folder="sensors",
        offline_storage=True
    )

    network = wappstoiot.createNetwork(
        "RadiatorController"
    )

    rediator = network.createDevice("radiator")
    temperature = rediator.createValue(
        "temperature",
        value_template=wappstoiot.ValueTemplate.TEMPERATURE,
        permission=wappstoiot.PermissionType.READWRITE,
        period=98723
    )

    def temp2pwm(temp):
        return period_ns*(temp/100)  # TODO: This should be rewriten!

    tempPWM = PWM(chip=0, pwm=0)
    tempPWM.start(period_ns, temp2pwm(temperature.getControlData()))

    temperature.onControl(
        lambda obj, value: tempPWM.write(temp2pwm(value))
    )

    temperature.onRefresh(callback=temperature.report(IioControl.read_raw(0)))

    # NOTE: Should be a option in wappstoiot.Network as Period=wappstoiot.Period.PERIODIC_REFRESH
    def period_read():
        if not killed.is_set():
            threading.Timer(temperature.period, period_read).start()
        temperature.report(IioControl.read_raw(0))
    period_read()

    try:
        while not killed.is_set():
            time.sleep(0.01)
            value = IioControl.read_raw(0)
            if abs(value - temperature.data) > temperature.delta:
                temperature.report(value)
    finally:
        tempPWM.close()
        wappstoiot.close()


if __name__ == "__main__":
    main()

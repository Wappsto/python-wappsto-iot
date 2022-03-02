#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import os
import signal
import threading

from typing import Union
from typing import Tuple

from porcupineIO import IioControl
from porcupineIO import PWM
import wappstoiot


def requestGPS(timeout: int = 60) -> Tuple[Union[int, None], Union[int, None]]:
    ...


def sleep(sec: int) -> None:
    if sec < 3600:  # Hour.
        os.system(f"rtcwake -m mem -s {sec}")  # Suspend
    else:
        os.system(f"rtcwake -m disk -s {sec}")  # Hibernation


def main():

    killed = threading.Event()
    signal.signal(signal.SIGINT, killed.set)
    signal.signal(signal.SIGTERM, killed.set)

    period_ns = 400000

    wappstoiot.config(
        config_folder="sensors",
        offline_storage=True,
        connect_sync=True,  # TODO: !
    )

    network = wappstoiot.createNetwork(
        "MyNetwork"
    )

    gps = network.createDevice("GPS")

    latitude = gps.createValue(
        "latitude",
        permission=wappstoiot.PermissionType.READ,
        value_template=wappstoiot.ValueTemplate.LATITUDE,
    )

    longitude = gps.createValue(
        "longitude",
        permission=wappstoiot.PermissionType.READ,
        value_template=wappstoiot.ValueTemplate.LONGITUDE,
    )

    sensors = network.createDevice("sensors")
    temperature = sensors.createValue(
        "temperature",
        value_template=wappstoiot.ValueTemplate.TEMPERATURE,
        permission=wappstoiot.PermissionType.READWRITE,
        # UNSURE: Should we be able to set the init value for Control & Report?
    )

    def temp2pwm(temp):
        return period_ns*(temp/100)  # TODO: This should be rewriten!

    tempPWM = PWM(chip=0, pwm=0)
    tempPWM.start(period_ns, temp2pwm(temperature.state.control.data))

    temperature.onControl(  # Should Never be activited since it sleeps. 99%
        lambda obj, value: tempPWM.write(temp2pwm(value))
    )

    try:
        while not killed.is_set():
            network.connect()
            temperature.report(IioControl.read_raw(0))
            tempPWM.write(temp2pwm(
                temperature.getControlData()
            ))
            lati, longi = requestGPS()
            latitude.report(lati)
            longitude.report(longi)
            network.disconnect()
            sleep(temperature.period)
    finally:
        wappstoiot.close()


if __name__ == "__main__":
    main()

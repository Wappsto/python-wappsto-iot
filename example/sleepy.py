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
import WappstoIoT


def requestGPS(timeout: int = 60) -> Tuple[Union[int, None], Union[int, None]]:
    ...


def sleep(sec: int) -> None:
    if sec < 3600:  # Hour.
        os.system(f"rtcwake -m mem -s {sec}")
    else:
        os.system(f"rtcwake -m disk -s {sec}")


def main():

    killed = threading.Event()
    signal.signal(signal.SIGINT, killed.set)
    signal.signal(signal.SIGTERM, killed.set)

    period_ns = 400000

    WappstoIoT.config(
        configFolder="sensors",
        storeQueue=True,
        connectSync=True,
    )

    gps = WappstoIoT.createDevice("GPS")

    latitude = gps.createValue(
        value_type=WappstoIoT.ValueType.LATITUDE,
    )

    longitude = gps.createValue(
        value_type=WappstoIoT.ValueType.LONGITUDE,
    )

    sensors = WappstoIoT.createDevice("sensors")
    temperature = sensors.createValue(
        value_type=WappstoIoT.ValueType.TEMPERATURE,
        permission=WappstoIoT.PermissionType.READWRITE,
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
            WappstoIoT.connect()
            temperature.report(IioControl.read_raw(0))
            tempPWM.write(temp2pwm(
                temperature.state.control.data
            ))
            lati, longi = requestGPS()
            latitude.report(lati)
            longitude.report(longi)
            WappstoIoT.disconnect()
            sleep(temperature.period)
    finally:
        WappstoIoT.close()


if __name__ == "__main__":
    main()

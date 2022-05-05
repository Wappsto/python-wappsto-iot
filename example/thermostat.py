#! /usr/bin/env python3
"""
Thermostate Example code.

An example on how to make a thermostat program,
that are connected to Wappsto with WappstoIoT.
"""
import math
import time

from typing import Union

import wappstoiot

UPDATE_INTERVAL: int = 1


# ##############################
# Simulated Thermostat Start
# ##############################
temperature_reading: int = 18
temperature_target: int = 20


def get_temperature() -> int:
    return temperature_reading


def set_target_temperature(target: int):
    global temperature_target
    temperature_target = target


def update_temperature() -> bool:
    global temperature_reading
    diff: int = temperature_target - temperature_reading
    if diff:
        temperature_reading += math.ceil(diff/3) or -1
        return True
    return False
# ##############################
# Simulated Thermostat End
# ##############################


def createThermostat() -> wappstoiot.Value:

    network = wappstoiot.createNetwork(
        name="Home",
        description="Thermostat Simulator"
    )

    thermostat_device = network.createDevice(
        name="Thermostat",
        description='Thermostat Simulator',
        product='Thermostat',
        version='1.0.0',
        manufacturer='ME',
    )

    temperature_value = thermostat_device.createValue(
        name="Temperature",
        permission=wappstoiot.PermissionType.READWRITE,
        value_template=wappstoiot.ValueTemplate.TEMPERATURE_CELSIUS
    )

    temperature_value.report(
        get_temperature()
    )

    temp = temperature_value.getControlData()
    if isinstance(temp, float):
        set_target_temperature(int(temp))

    @temperature_value.onControl
    def control_temp(obj: wappstoiot.Value, data: Union[float, str, None]):
        if isinstance(data, float):
            set_target_temperature(int(data))

    @temperature_value.onRefresh
    def refresh_temp(obj: wappstoiot.Value):
        obj.report(get_temperature())

    return temperature_value


def main():
    wappstoiot.config(
        config_folder="config"
    )
    temperature_value = createThermostat()

    try:
        while True:
            time.sleep(UPDATE_INTERVAL)
            if update_temperature():
                temperature_value.report(
                    get_temperature()
                )
    except KeyboardInterrupt:
        pass
    finally:
        wappstoiot.close()


if __name__ == "__main__":
    main()

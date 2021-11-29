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

from scd30_drv import SCD30


def main():
    sensor = SCD30(1, 5, 1, None)

    def read():
        while not sensor.data_ready():
            time.sleep(0.01)
        return sensor.get_scd30_measurements()

    network = wappstoiot.Network(
        name="Co2 Unit",
        configFolder="./config"
    )

    device = network.createDevice(
        name="SCD30"
    )

    co2_value = device.createValue(
        name="Co2",
        value_type=wappstoiot.ValueType.NUMBER,
        permission=wappstoiot.PermissionType.READ
    )

    temp_value = device.createValue(
        name="Temperature",
        value_type=wappstoiot.ValueType.NUMBER,
        permission=wappstoiot.PermissionType.READ
    )

    humi_value = device.createValue(
        name="Humidity",
        value_type=wappstoiot.ValueType.NUMBER,
        permission=wappstoiot.PermissionType.READ
    )

    co2_value.onRefresh(
        callback=lambda obj: obj.report(read().CO2)
    )

    temp_value.onRefresh(
        callback=lambda obj: obj.report(read().temperature)
    )

    humi_value.onRefresh(
        callback=lambda obj: obj.report(read().humidity)
    )

    def update_all_values():
        data = read()
        co2_value.report(data.CO2)
        temp_value.report(data.temperature)
        humi_value.report(data.humidity)

    while True:
        try:
            update_all_values()
            time.sleep(60*30)  # 1/2 hour sleep
        except KeyboardInterrupt:
            break
    network.close()


if __name__ == "__main__":
    main()

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

from scd30_drv import SCD30


def main():
    sensor = SCD30(1, 5, 1, None)

    def read():
        while not sensor.data_ready():
            time.sleep(0.01)
        return sensor.get_scd30_measurements()

    wappstoiot.config(
        config_folder="./config"
    )

    network = wappstoiot.createNetwork(
        name="Co2 Unit",
    )

    device = network.createDevice(
        name="SCD30"
    )

    co2_value = device.createValue(
        name="Co2",
        value_template=wappstoiot.ValueTemplate.NUMBER,
        permission=wappstoiot.PermissionType.READ
    )

    temp_value = device.createValue(
        name="Temperature",
        value_template=wappstoiot.ValueTemplate.TEMPERATURECELCIUS,
        permission=wappstoiot.PermissionType.READ
    )

    humi_value = device.createValue(
        name="Humidity",
        value_template=wappstoiot.ValueTemplate.NUMBER,
        permission=wappstoiot.PermissionType.READ
    )

    co2_value.onRefresh(
        callback=lambda obj: obj.report(read().CO2_PPM)
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
    wappstoiot.close()


if __name__ == "__main__":
    main()

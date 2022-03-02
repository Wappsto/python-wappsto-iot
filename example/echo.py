#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import time

import wappstoiot


def main():
    wappstoiot.config(
        config_folder="echo"
    )

    network = wappstoiot.createNetwork(
        name="echo",
    )

    device = network.createDevice(
        name="EchoDevice"
    )

    value = device.createValue(
        name="Moeller",
        permission=wappstoiot.PermissionType.READWRITE,
        value_template=wappstoiot.ValueTemplate.STRING
    )

    value.onControl(
        callback=lambda obj, new_value: obj.report(new_value)
    )

    value.onRefresh(
        callback=lambda obj: obj.report(f"{obj.getReportData()} Refreshed!")
    )
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        wappstoiot.close()


if __name__ == "__main__":
    main()

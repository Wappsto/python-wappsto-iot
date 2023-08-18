#! /bin/env python3
"""
This is a working code example on how to make a echo device.

This device receives and string from wappsto, add `Refreshed!` on the end,
and send it back to wappsto.

This code is based on the assumption that there have been
created a 'certificate files' in the 'IoT Certificate Manager' wapp.
The certificates, have then been downloaded
unpack and saved into the config-folder of you project.
"""

import time

import wappstoiot


def main():
    """."""
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

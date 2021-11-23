#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import time

import wappstoiot


def main():
    network = wappstoiot.Network(
        name="echo",
        configFolder="echo"
    )

    device = network.createDevice(
        name="EchoDevice"
    )

    value = device.createValue(
        name="Moeller",
        value_type=wappstoiot.ValueType.STRING
    )

    value.onControl(
        callback=lambda obj, new_value: obj.report(new_value)
    )

    value.onRefresh(
        callback=lambda obj: obj.report(f"{obj.data} Refreshed!")
    )
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        network.close()


if __name__ == "__main__":
    main()

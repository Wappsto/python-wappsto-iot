#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import time

import WappstoIoT


def main():
    network = WappstoIoT.Config(
        name="echo",
        configFolder="echo"
    )

    device = network.createDevice("EchoDevice")

    value = device.createValue(
        name="Moeller",
        value_type=WappstoIoT.ValueType.STRING
    )

    value.onControl(
        callback=lambda obj, new_value: value.report(new_value)
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

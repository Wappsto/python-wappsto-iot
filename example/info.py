#! /bin/env python3

# This code is based on the assumption that there have been
# created a 'black (custom)' in the 'IoT Rapid Prototyping' wapp.
# The certificates, have then been downloaded
# unpack and saved into the config-folder of you project.

import WappstoIoT


def main():
    network = WappstoIoT.Wappsto(
        name="info",
        configFolder="info"
    )

    network.onStatusChange(
        StatusID=WappstoIoT.StatusID.CONNECTION,
        callback=lambda StatusID, newStatus: print(f"New status: {newStatus}")
    )
    network.onDelete(
        callback=lambda obj: print("Network received a: Delete")
    )

    device = network.createDevice()

    value = device.createValue(
        "StringInfo",
        value_type=WappstoIoT.ValueType.STRING
    )

    def valueRefresh(obj: WappstoIoT.Value) -> None:
        newValue = f"{obj.data} Refreshed!"
        print(f"Refreshing the {obj.name} to: '{newValue}'")
        obj.report(newValue)

    value.onRefresh(
        callback=valueRefresh
    )

    value.onControl(
        callback=lambda obj, new_value: print(f"Control value have Change to: {new_value}")
    )

    while True:
        data = input("Enter a Message: ")

        if data in ["exit", "x", "quit", "q"]:
            network.close()
            print("Manuel closing Wappsto.")
            break
        value.report(data)


if __name__ == "__main__":
    main()

#! /bin/env python3

# This code is based on the assumption that The certificates,
# have then been downloaded unpack and saved into the config-folder
# of you project, in this case the info-folder.

import wappstoiot


def main():
    network = wappstoiot.Network(
        name="info",
        configFolder="info"
    )

    # network.onStatusChange(
    #     StatusID=wappstoiot.StatusID.CONNECTION,
    #     callback=lambda StatusID, newStatus: print(f"New status: {newStatus}")
    # )

    # network.onDelete(
    #     callback=lambda obj: print("Network received a: Delete")
    # )

    device = network.createDevice()

    value = device.createValue(
        "StringInfo",
        value_type=wappstoiot.ValueType.STRING
    )

    def valueRefresh(obj):
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

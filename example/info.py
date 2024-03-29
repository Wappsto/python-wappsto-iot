#! /bin/env python3
"""
This is a working example on how to make a chat-like interaction with wappsto.

This code is based on the assumption that there have been
created a 'certificate files' in the 'IoT Certificate Manager' wapp.
The certificates, have then been downloaded
unpack and saved into the config-folder of you project.
"""

import wappstoiot


def main():
    """."""
    def statusChange(StatusID, data):
        """."""
        print(f"New status: {StatusID}")

    wappstoiot.onStatusChange(
        StatusID=wappstoiot.connection.StatusID.CONNECTED,
        callback=statusChange
    )

    wappstoiot.onStatusChange(
        StatusID=wappstoiot.service.StatusID.ERROR,
        callback=statusChange
    )

    wappstoiot.config(
        config_folder="info",
    )

    network = wappstoiot.createNetwork(
        name="info",
    )

    network.onDelete(
        callback=lambda obj: print("Network received a: Delete")
    )

    device = network.createDevice("Human")

    value = device.createValue(
        "StringInfo",
        permission=wappstoiot.PermissionType.READWRITE,
        value_template=wappstoiot.ValueTemplate.STRING,
    )

    def valueRefresh(obj):
        newValue = f"{obj.getReportData()} Refreshed!"
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
            wappstoiot.close()
            print("Manuel closing Wappsto.")
            break
        value.report(data)


if __name__ == "__main__":
    main()

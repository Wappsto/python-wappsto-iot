#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pathlib
import uuid
import getpass

import requests  # TODO: Remove dependencies.


debug = False

wappstoEnv = [
    "dev",
    "qa",
    "stagning",
    "prod",
]


wappstoPort = {
    "dev": 52005,
    "qa": 53005,
    "stagning": 54005,
    "prod": 443
}

wappstoUrl = {
    "dev": "https://dev.wappsto.com",
    "qa": "https://qa.wappsto.com",
    "staging": "https://stagning.wappsto.com",
    "prod": "https://wappsto.com",
}


def _log_request_error(rq):
    if debug:
        print("Sendt data    :")
        print(" - URL         : {}".format(rq.request.url))
        print(" - Headers     : {}".format(rq.request.headers))
        print(" - Request Body: {}".format(
            json.dumps(rq.request.body, indent=4, sort_keys=True))
        )

        print("")
        print("")

        print("Received data :")
        print(" - URL         : {}".format(rq.url))
        print(" - Headers     : {}".format(rq.headers))
        print(" - Status code : {}".format(rq.status_code))
        try:
            print(" - Request Body: {}".format(
                json.dumps(json.loads(rq.text), indent=4, sort_keys=True))
            )
        except (AttributeError, json.JSONDecodeError):

            print(" - Request Body: {}".format(rq.text))
    rjson = json.loads(rq.text)
    print(f"[bold red]{rjson['message']}")
    exit(-2)


def start_session(base_url, username, password):
    session_json = {
        "username": username,
        "password": password,
        "remember_me": False
    }

    url = f"{base_url}/services/session"

    rdata = requests.post(
        url=url,
        headers={"Content-type": "application/json"},
        data=json.dumps(session_json)
    )

    rjson = json.loads(rdata.text)

    if not rdata.ok:
        _log_request_error(rdata)

    return rjson["meta"]["id"]


def create_network(
    session,
    base_url,
    # network_uuid=None,
    product=None,
    test_mode=False,
    reset_manufacturer=False,
    manufacturer_as_owner=True
):
    # Should take use of the more general functions.
    request = {
    }
    # if network_uuid:
    #     request["network"] = {"id": uuid}
    if product:
        request["product"] = product

    if test_mode:
        request["test_mode"] = True

    if reset_manufacturer:
        request["factory_reset"] = {"reset_manufacturer": True}

    request['manufacturer_as_owner'] = manufacturer_as_owner

    url = f"{base_url}/services/2.1/creator"
    header = {
        "Content-type": "application/json",
        "X-session": str(session)
    }

    rdata = requests.post(
        url=url,
        headers=header,
        data=json.dumps(request)
    )

    rjson = json.loads(rdata.text)

    if not rdata.ok:
        _log_request_error(rdata)
    return rjson


def get_network(session, base_url, network_uuid):
    f_url = f"{base_url}/services/2.1/creator?this_network.id={network_uuid}"
    header = {
        "Content-type": "application/json",
        "X-session": str(session)
    }

    fdata = requests.get(
        url=f_url,
        headers=header,
    )

    data = json.loads(fdata.text)

    if not fdata.ok:
        _log_request_error(fdata)

    if len(data['id']) == 0:
        print(f"{data['message']}")
        exit(-3)
    creator_id = data['id'][0]
    url = f"{base_url}/services/2.1/creator/{creator_id}"

    rdata = requests.get(
        url=url,
        headers=header
    )

    if not rdata.ok:
        _log_request_error(rdata)

    return json.loads(rdata.text)


def create_certificaties_files(location, creator, args):
    creator["ca"], creator["certificate"], creator["private_key"]
    with open(location / "ca.crt", "w") as file:
        file.write(creator["ca"])
    with open(location / "client.crt", "w") as file:
        file.write(creator["certificate"])
    with open(location / "client.key", "w") as file:
        file.write(creator["private_key"])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        choices=wappstoEnv,
        default="prod",
        help="Wappsto environment."
    )
    parser.add_argument(
        "--token",
        type=uuid.UUID,
        help="The Session Token. If not given, you are prompted to login."
    )
    parser.add_argument(
        "--path",
        type=pathlib.Path,
        default=".",
        help="The location to which the config files are saved."
    )
    parser.add_argument(
        "--recreate",
        type=uuid.UUID,
        help="Recreate Config file, for given network UUID. (Overwrites existent)"
    )
    parser.add_argument(
        "--debug",
        action='store_true',
        help="Make the operation more talkative",
    )

    args = parser.parse_args()

    debug = args.debug if args.debug else False

    if not args.token:
        session = start_session(
            base_url=wappstoUrl[args.env],
            username=input("Wappsto Username: "),
            password=getpass.getpass(prompt="Wappsto Password: "),
        )
    else:
        session = args.token
    if not args.recreate:
        creator = create_network(session=session, base_url=wappstoUrl[args.env])
    else:
        creator = get_network(
            session=session,
            base_url=wappstoUrl[args.env],
            network_uuid=args.recreate,
        )

    args.path.mkdir(exist_ok=True)

    create_certificaties_files(args.path, creator, args)

    print(f"\nNew network: {creator['network']['id']}")
    print(f"Settings saved at: {args.path}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import getpass
import json
import pathlib
import sys
import uuid

import requests


debug = False


wappstoUrl = {
    "dev": "dev.wappsto.com",
    "qa": "qa.wappsto.com",
    "staging": "staging.wappsto.com",
    "prod": "wappsto.com",
}


def _log_request_error(data):
    if debug:
        print("Sent data     :")
        print(" - URL         : {}".format(data.request.url))
        print(" - Headers     : {}".format(data.request.headers))
        print(" - Request Body: {}".format(
            json.dumps(data.request.body, indent=4, sort_keys=True))
        )

        print("")
        print("")

        print("Received data :")
        print(" - URL         : {}".format(data.url))
        print(" - Headers     : {}".format(data.headers))
        print(" - Status code : {}".format(data.status_code))
        try:
            print(" - Request Body: {}".format(
                json.dumps(json.loads(data.text), indent=4, sort_keys=True))
            )
        except (AttributeError, json.JSONDecodeError):
            pass
    try:
        err = json.loads(data.text)
    except Exception:
        err = data.text
    else:
        err = err.get('message', f"Unknown Error: http error: {data.status_code}")
    print(f"\t{err}")
    sys.exit(-2)


def start_session(base_url, username, password):
    session_json = {
        "username": username,
        "password": password,
        "remember_me": False
    }

    url = f"https://{base_url}/services/session"
    headers = {"Content-type": "application/json"}
    data = json.dumps(session_json)

    rdata = requests.post(
        url=url,
        headers=headers,
        data=data
    )
    if rdata.status_code >= 300:
        print("\nAn error occurred during login:")
        _log_request_error(rdata)

    rjson = json.loads(rdata.text)

    return rjson["meta"]["id"]


def create_network(
    session,
    base_url,
    # network_uuid=None,
    product=None,
    test_mode=False,
    reset_manufacturer=False,
    dry_run=False
):
    # Should take use of the more general functions.
    request = {}

    url = f"https://{base_url}/services/2.1/creator"
    headers = {
        "Content-type": "application/json",
        "X-session": str(session)
    }

    data = json.dumps(request)

    if not dry_run:
        rdata = requests.post(
            url=url,
            headers=headers,
            data=data
        )

        if rdata.status_code >= 300:
            print("\nAn error occurred during Certificate retrieval:")
            _log_request_error(rdata)

        rjson = json.loads(rdata.text)
    else:
        rjson = {
            'network': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
            'ca': "NOTHING",
            'certificate': "NOTHING",
            'private_key': "NOTHING",
            'meta': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
        }
        print("\nDry-run: Fake Certificates created!")

    print(f"\nCertificate generated for new network:\t{rjson['network']['id']}")

    return rjson


def claim_network(session, base_url, network_uuid, dry_run=False):
    url = f"https://{base_url}/services/2.0/network/{network_uuid}"

    headers = {
        "Content-type": "application/json",
        "X-session": str(session)
    }

    if not dry_run:
        rdata = requests.post(
            url=url,
            headers=headers,
            data="{}"
        )

        if rdata.status_code >= 300:
            print("\nAn error occurred during claiming the network:")
            _log_request_error(rdata)
        rjson = json.loads(rdata.text)
    else:
        rjson = {
            'device': [],
            'meta': {
                'id': network_uuid,
                'type': 'network',
                'version': '2.0'
            }
        }
        print("\nFake Claiming the Network.")

    print(f"\nNetwork: {network_uuid} have been claimed.")
    return rjson


def get_network(session, base_url, network_uuid):
    url = f"https://{base_url}/services/2.1/creator?this_network.id={network_uuid}"
    headers = {
        "Content-type": "application/json",
        "X-session": str(session)
    }

    rdata = requests.get(
        url=url,
        headers=headers
    )

    if rdata.status_code >= 300:
        print("\nAn error occurred during Certificate retrieval:")
        _log_request_error(rdata)
    data = json.loads(rdata.text)

    if not data['id']:
        print(f"{data['message']}")
        sys.exit(-3)
    creator_id = data['id'][0]
    url = f"https://{base_url}/services/2.1/creator/{creator_id}"

    rdata = requests.get(
        url=url,
        headers=headers
    )

    if rdata.status_code >= 300:
        print("\nAn error occurred during Certificate retrieval:")
        _log_request_error(rdata)

    rjson = json.loads(rdata.text)

    print(f"\nCertificate retrieved for network:\t{rjson['network']['id']}")

    return rjson


def create_certificaties_files(location, creator, args):
    creator["ca"], creator["certificate"], creator["private_key"]

    if not args.dry_run:
        location.mkdir(exist_ok=True)
        try:
            with open(location / "ca.crt", "w") as file:
                file.write(creator["ca"])
            with open(location / "client.crt", "w") as file:
                file.write(creator["certificate"])
            with open(location / "client.key", "w") as file:
                file.write(creator["private_key"])
        except Exception as err:
            print("\nAn error occurred while saving Certificates:")
            print(f"\t{err}")
            print("\nWhen fixed you can recreate the certificate file with the --recreate option.")
            sys.exit(-3)
    else:
        print("\nDry-run: Fake Save done!")
    print(f"\nLocation of generated certificates:\t{location.absolute()}")


def main():
    global debug

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        action='store_true',
        help="Run the Script, without making the files & folders.",
    )
    parser.add_argument(
        "--env",
        type=str,
        choices=list(wappstoUrl.keys()),
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

    args = parser.parse_args(sys.argv[1:])

    debug = args.debug if args.debug else False

    base_url = wappstoUrl[args.env]

    if not args.token:
        session = start_session(
            base_url=base_url,
            username=input("Wappsto Username: "),
            password=getpass.getpass(prompt="Wappsto Password: "),
        )
    else:
        session = args.token
    if not args.recreate:
        creator = create_network(
            session=session,
            base_url=base_url,
            dry_run=args.dry_run
        )
        claim_network(
            session=session,
            base_url=base_url,
            network_uuid=creator.get('network', {}).get('id'),
            dry_run=args.dry_run
        )
    else:
        creator = get_network(
            session=session,
            base_url=base_url,
            network_uuid=args.recreate,
        )

    args.path.mkdir(exist_ok=True)

    create_certificaties_files(args.path, creator, args)

    print("\nEnjoy...")
    sys.exit(0)


if __name__ == "__main__":
    main()

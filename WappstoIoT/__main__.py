import getpass
import json
import pathlib
import uuid

import requests

from WappstoIoT.Modules.Template import _ConfigFile, _Config


from rich import traceback

traceback.install(show_locals=True)


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
    "prod": 51005
}

wappstoUrl = {
    "dev": "https://dev.wappsto.com",
    "qa": "https://qa.wappsto.com",
    "stagning": "https://stagningwappsto.com",
    "prod": "https://wappsto.com",
}


def _log_request_error(rq):
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

    if not rdata.ok:
        _log_request_error(rdata)
        raise
    rjson = json.loads(rdata.text)
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

    url = f"{base_url}/services/2.1/creator"
    header = {"Content-type": "application/json", "X-session": str(session)}

    rdata = requests.post(
        url=url,
        headers=header,
        data=json.dumps(request)
    )

    if not rdata.ok:
        _log_request_error(rdata)
        raise
    return json.loads(rdata.text)


def get_network(session, base_url, network_uuid):
    f_url = f"{base_url}/services/2.1/creator?this_network.id={network_uuid}"
    header = {"Content-type": "application/json", "X-session": str(session)}

    fdata = requests.get(
        url=f_url,
        headers=header,
    )
    if not fdata.ok:
        _log_request_error(fdata)
        raise
    data = json.loads(fdata.text)
    if len(data['id']) == 0:
        raise
    creator_id = data['id'][0]
    url = f"{base_url}/services/2.1/creator/{creator_id}"

    rdata = requests.get(
        url=url,
        headers=header
    )

    if not rdata.ok:
        _log_request_error(rdata)
        raise

    return json.loads(rdata.text)


def create_IoT_config_file(location, creator, args):
    creator["ca"], creator["certificate"], creator["private_key"]
    configs = _ConfigFile(
        configs=_Config(
            network_uuid=creator['network']['id'],
            network_name=args.name,
            port=wappstoPort[args.env],
            end_point=wappstoUrl[args.env],
        ),
        units={}
    )

    with open(location/"config.json", "w") as file:
        file.write(configs.json())
    with open(location/"ca.crt", "w") as file:
        file.write(creator["ca"])
    with open(location/"client.crt", "w") as file:
        file.write(creator["certificate"])
    with open(location/"client.key", "w") as file:
        file.write(creator["private_key"])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        type=str,
        choices=wappstoEnv,
        default="prod",
        help="Wappsto enviroment."
    )
    parser.add_argument(
        "--token",
        type=uuid.UUID,
        help="The Session Token. If not given, you are prompted to login."
    )
    parser.add_argument(
        "--path",
        type=pathlib.Path,
        default="./config/",
        help="The location to which the config files are saved."
    )
    parser.add_argument(
        "--recreate",
        type=uuid.UUID,
        help="Recreate Config file, for given network UUID."
    )
    parser.add_argument(
        "name",
        type=str,
        default="TheNetwork",
        help="The Name of the newly created Wappsto Network."
    )

    args = parser.parse_args()

    if not args.token:
        session = start_session(
            base_url=wappstoUrl[args.env],
            username=input("Wappsto Username:"),
            password=getpass.getpass(prompt="Wappsto Password:"),
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

    create_IoT_config_file(args.path, creator, args)

    print(f"New network: {creator['network']['id']}")
    print(f"Settings saved at: {args.path}")

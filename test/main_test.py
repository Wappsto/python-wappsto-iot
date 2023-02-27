# https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
# https://stackoverflow.com/questions/57663308/how-to-mock-requests-using-pytest
# import mock
import json
import pathlib
import pytest

import rich

import wappstoiot.__main__


class TestCLI:

    def test_help(self, mocker):
        mock_output = mocker.patch("wappstoiot.__main__.argparse.ArgumentParser._print_message")
        mock__main__sys = mocker.patch("wappstoiot.__main__.sys")
        mock__main__sys.argv = ["/patch/wappstoiot", "--help"]

        try:
            wappstoiot.__main__.main()
        except SystemExit:
            pass

        print_out = mock_output.call_args[0][0]
        # file_out = mock_output.call_args[0][1]

        rich.print(f"{print_out}")

        # UNSURE: How should I test the print_out output?
        assert "usage: " in print_out
        assert "-h, --help" in print_out

    @pytest.mark.parametrize(
        "debug",
        [
            True,
            False
        ]
    )
    def test_login_error(self, mocker, requests_mock, debug):
        mock_output = mocker.patch("wappstoiot.__main__.print")
        mock__main__sys = mocker.patch("wappstoiot.__main__.sys")

        mock__main__sys.argv = ["/patch/wappstoiot"]
        if debug:
            mock__main__sys.argv.append("--debug")
        base_url = wappstoiot.__main__.wappstoUrl['prod']  # TODO: Make this a parametrize

        # #### Login setup. ####
        username = "test@testmail.you"
        password = "the_password_you_do_not_know"
        mocker.patch(
            target="wappstoiot.__main__.input",
            return_value=username,
        )
        mocker.patch(
            target="wappstoiot.__main__.getpass.getpass",
            return_value=password,
        )
        posted_session = {
            "username": username,
            "password": password,
            "remember_me": False
        }
        reply_Session = json.dumps({
              "meta": {
                "type": "httpresponse",
                "version": "2.0"
              },
              "message": "Authorization is not valid",
              "data": {
                "wrong_header": "Authentication"
              },
              "code": 9900025,
              "service": "session"
        })

        requests_mock.post(
            f"https://{base_url}/services/session",
            text=reply_Session,
            status_code=401,
        )

        try:
            wappstoiot.__main__.main()
        except SystemExit:
            pass

        session_request = requests_mock.request_history[0]

        assert session_request.text == json.dumps(posted_session)
        assert "Authorization is not valid" in mock_output.call_args[0][0]

    @pytest.mark.parametrize(
        "dry_run",
        [
            True,
            False
        ]
    )
    @pytest.mark.parametrize(
        "token",
        [
            'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            '5bdaa36a-104a-44a6-b968-fab816db957f'
        ]
    )
    def test_create(self, mocker, requests_mock, dry_run, token):
        # mock_output = mocker.patch("wappstoiot.__main__.print")
        mock__main__sys = mocker.patch("wappstoiot.__main__.sys")

        location = pathlib.Path(".")

        mock__main__sys.argv = ["/patch/wappstoiot"]
        base_url = wappstoiot.__main__.wappstoUrl['prod']  # TODO: Make this a parametrize

        if dry_run:
            mock__main__sys.argv.append("--dry_run")

        if token != 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx':
            mock__main__sys.argv.append("--token")
            mock__main__sys.argv.append(token)
        else:
            # #### Login setup. ####
            username = "test@testmail.you"
            password = "the_password_you_do_not_know"
            mocker.patch(
                target="wappstoiot.__main__.input",
                return_value=username,
            )
            mocker.patch(
                target="wappstoiot.__main__.getpass.getpass",
                return_value=password,
            )
            posted_session = {
                "username": username,
                "password": password,
                "remember_me": False
            }

            reply_Session = json.dumps({
                'remember_me': False,
                'system': 'python-requests/2.27.0',
                'type': 'user',
                'provider': 'email',
                'meta': {
                    'deprecated': True,
                    'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                    'type': 'session',
                    'version': '2.0'
                },
                'to_upgrade': False,
                'upgrade': True
            })

            requests_mock.post(
                f"https://{base_url}/services/session",
                text=reply_Session
            )

        # #### Create Setup ####

        reply_data = json.dumps({
            'network': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
            'ca': "NOTHING",
            'certificate': "NOTHING",
            'private_key': "NOTHING",
            'meta': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
        })
        requests_mock.post(
            f"https://{base_url}/services/2.1/creator",
            text=reply_data
        )

        # #### Claim Setup ####

        reply_data = json.dumps({
            'device': [],
            'meta': {
                'type': 'network',
                'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
            }
        })
        requests_mock.post(
            f"https://{base_url}/services/2.0/network/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            text=reply_data
        )

        ca_file = (location / "ca.crt")
        crt_file = (location / "client.crt")
        key_file = (location / "client.key")

        #######################

        try:
            wappstoiot.__main__.main()
        except SystemExit:
            pass

        if token == 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx':
            session_request = requests_mock.request_history.pop(0)
            rich.print(f"Header: {session_request.headers}")
            assert session_request.text == json.dumps(posted_session)

        if not dry_run:
            create_request = requests_mock.request_history.pop(0)
            claim_request = requests_mock.request_history.pop(0)

            assert create_request.text == json.dumps({})
            assert create_request.headers["X-session"] == token
            assert claim_request.text == json.dumps({})
            assert claim_request.headers["X-session"] == token

        assert ca_file.exists() != dry_run
        if ca_file.exists():
            ca_file.unlink()

        assert crt_file.exists() != dry_run
        if crt_file.exists():
            crt_file.unlink()

        assert key_file.exists() != dry_run
        if key_file.exists():
            key_file.unlink()

    def test_network(self, mocker, requests_mock):
        # mock_output = mocker.patch("wappstoiot.__main__.print")
        mock__main__sys = mocker.patch("wappstoiot.__main__.sys")
        network_uuid = "bc43077b-835e-4cd6-99d0-32895e08fab1"

        location = pathlib.Path(".")

        mock__main__sys.argv = ["/patch/wappstoiot", "--recreate", network_uuid]

        # #### Login setup. ####
        username = "test@testmail.you"
        password = "the_password_you_do_not_know"
        mocker.patch(
            target="wappstoiot.__main__.input",
            return_value=username,
        )
        mocker.patch(
            target="wappstoiot.__main__.getpass.getpass",
            return_value=password,
        )
        posted_session = {
            "username": username,
            "password": password,
            "remember_me": False
        }

        reply_Session = json.dumps({
            'remember_me': False,
            'system': 'python-requests/2.27.0',
            'type': 'user',
            'provider': 'email',
            'meta': {
                'deprecated': True,
                'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
                'type': 'session',
                'version': '2.0'
            },
            'to_upgrade': False,
            'upgrade': True
        })

        base_url = wappstoiot.__main__.wappstoUrl['prod']  # TODO: Make this a parametrize
        requests_mock.post(
            f"https://{base_url}/services/session",
            text=reply_Session
        )

        # #### Network Request ####
        reply_idlist = json.dumps({
            'child': {
                'type': 'network',
                'version': '2.0'
            },
            'id': [
                'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
            ],
            'more': False,
            'limit': 1,
            'count': 1,
            'meta': {
                'type': 'idlist'
            },
        })
        requests_mock.get(
            f"https://{base_url}/services/2.1/creator?this_network.id={network_uuid}",
            text=reply_idlist
        )

        # #### Create Setup ####

        reply_data = json.dumps({
            'network': {'id': network_uuid},
            'ca': "NOTHING",
            'certificate': "NOTHING",
            'private_key': "NOTHING",
            'meta': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
        })
        requests_mock.get(
            f"https://{base_url}/services/2.1/creator/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            text=reply_data
        )

        ca_file = (location / "ca.crt")
        crt_file = (location / "client.crt")
        key_file = (location / "client.key")

        #######################

        try:
            wappstoiot.__main__.main()
        except SystemExit:
            pass

        # print_out = mock_output.call_args[0][0]

        session_request = requests_mock.request_history[0]
        rich.print("-------------------Session----------------------")
        rich.print(f"Url   : {session_request.url}")
        rich.print(f"Method: {session_request.method}")
        rich.print(f"text  : {session_request.text}")

        assert session_request.text == json.dumps(posted_session)

        network_request = requests_mock.request_history[1]
        rich.print("-------------------Create-----------------------")
        rich.print(f"Url   : {network_request.url}")
        rich.print(f"Method: {network_request.method}")
        rich.print(f"text  : {network_request.text}")

        creator_request = requests_mock.request_history[2]
        rich.print("--------------------Claim-----------------------")
        rich.print(f"Url   : {creator_request.url}")
        rich.print(f"Method: {creator_request.method}")
        rich.print(f"text  : {creator_request.text}")

        # assert network_request.text == json.dumps({})
        # assert creator_request.text == json.dumps({})

        assert ca_file.exists()
        if ca_file.exists():
            ca_file.unlink()

        assert crt_file.exists()
        if crt_file.exists():
            crt_file.unlink()

        assert key_file.exists()
        if key_file.exists():
            key_file.unlink()

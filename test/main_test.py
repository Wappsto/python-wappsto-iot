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
        assert "optional arguments:" in print_out
        assert "-h, --help" in print_out

    @pytest.mark.parametrize(
        "dry_run",
        [
            True,
            False
        ]
    )
    def test_create_dry_run(self, mocker, requests_mock, dry_run):
        # mock_output = mocker.patch("wappstoiot.__main__.print")
        mock__main__sys = mocker.patch("wappstoiot.__main__.sys")

        location = pathlib.Path(".")

        mock__main__sys.argv = ["/patch/wappstoiot"]

        if dry_run:
            mock__main__sys.argv.append("--dry_run")

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

        base_url = wappstoiot.__main__.wappstoUrl['prod']
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

        # print_out = mock_output.call_args[0][0]

        rich.print("-------------------Session----------------------")
        session_request = requests_mock.request_history[0]
        rich.print(f"Url   : {session_request.url}")
        rich.print(f"Method: {session_request.method}")
        rich.print(f"text  : {session_request.text}")

        rich.print("-------------------Create-----------------------")
        create_request = requests_mock.request_history[1]
        rich.print(f"Url   : {create_request.url}")
        rich.print(f"Method: {create_request.method}")
        rich.print(f"text  : {create_request.text}")

        rich.print("--------------------Claim-----------------------")
        claim_request = requests_mock.request_history[2]
        rich.print(f"Url   : {claim_request.url}")
        rich.print(f"Method: {claim_request.method}")
        rich.print(f"text  : {claim_request.text}")

        assert session_request.text == json.dumps(posted_session)

        if not dry_run:
            assert create_request.text == json.dumps({})
            assert claim_request.text == json.dumps({})

        assert ca_file.exists() != dry_run
        if ca_file.exists():
            ca_file.unlink()
        assert crt_file.exists() != dry_run
        if crt_file.exists():
            crt_file.unlink()
        assert key_file.exists() != dry_run
        if key_file.exists():
            key_file.unlink()


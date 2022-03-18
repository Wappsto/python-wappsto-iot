# https://medium.com/opsops/how-to-test-if-name-main-1928367290cb
# https://stackoverflow.com/questions/57663308/how-to-mock-requests-using-pytest
# import mock
import json
# import pytest

import rich

import wappstoiot.__main__


class TestCLI:

    # @pytest.fixture
    # def mock__main__sys(self, mocker):
    #     mock_sys = mocker.patch("wappstoiot.__main__.argparse._sys")

    #     return mock_sys

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

        rich.print(print_out)

        # UNSURE: How should I test the print_out output?
        # assert False

    def test_create(self, mocker, requests_mock):
        # mock_output = mocker.patch("wappstoiot.__main__.print")
        mock__main__sys = mocker.patch("wappstoiot.__main__.sys")

        mock__main__sys.argv = ["/patch/wappstoiot", "--dry_run"]
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
        reply_data = json.dumps({
            'network': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
            'ca': "NOTHING",
            'certificate': "NOTHING",
            'private_key': "NOTHING",
            'meta': {'id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
        })

        posted_data = {
            "username": username,
            "password": password,
            "remember_me": False
        }

        base_url = wappstoiot.__main__.wappstoUrl['prod']
        requests_mock.post(
            f"https://{base_url}/services/session",
            text=reply_data
        )
        try:
            wappstoiot.__main__.main()
        except SystemExit:
            pass

        # print_out = mock_output.call_args[0][0]
        # rich.print("-"*50)
        # rich.print(print_out)
        # rich.print("-"*50)

        rich.print(requests_mock.last_request.text)

        assert requests_mock.last_request.text == json.dumps(posted_data)
        # Test the created files.

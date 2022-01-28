#! /usr/bin/env python3

import shutil

from pathlib import Path
from unittest import mock

import pytest

from utils.generators import certifi_gen

import wappstoiot


class TestConnection:
    """
    TestJsonLoadClass instance.

    Tests loading json files in wappsto.

    """

    temp = Path(__file__).parent.parent / Path('temp')

    @classmethod
    def setup_class(self):
        """
        Sets up the class.

        Sets locations to be used in test.

        """
        shutil.rmtree(self.temp, ignore_errors=True)
        self.temp.mkdir(exist_ok=True, parents=True)

    def generate_certificates(self, name: str):
        """Generate & save certificates."""
        certi = certifi_gen(name=name)
        for name, data in zip(["ca.crt", "client.key", "client.crt"], certi):
            path = self.temp / name
            with path.open("w") as file:
                file.write(data)

    @mock.patch(
        target='wappstoiot.connections.sslsocket.ssl.SSLContext',
        autospec=True
    )
    @pytest.mark.parametrize(
        "url, port",
        [
            ('wappsto.com', 443),
            ('qa.wappsto.com', 53005),
            ('dev.wappsto.com', 52005),
            ('staging.wappsto.com', 54005),
        ]
    )
    def test_connection(self, mock_socket, url, port):
        self.generate_certificates(name=url)

        wappstoiot.config(
            config_folder=Path(self.temp),
        )

        mock_socket.connect.assert_called_with((f"collector.{url}", port))

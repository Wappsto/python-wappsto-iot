#! /usr/bin/env python3

import shutil
import datetime
from pathlib import Path
# from pytest import mock

import pytest
import uuid

from utils.generators import client_certifi_gen
from utils.package_smithing import get_success_pkg
import wappstoiot

import rich


class TestConnection:
    """
    TestJsonLoadClass instance.

    Tests loading json files in wappsto.

    """

    temp = Path(__file__).parent.parent / Path('temp')

    def generate_certificates(self, name: str, network_uuid: uuid.UUID):
        """Generate & save certificates."""
        certi = client_certifi_gen(name=name, uid=network_uuid)
        for name, data in zip(["ca.crt", "client.key", "client.crt"], certi):
            path = self.temp / name
            with path.open("w") as file:
                file.write(data)

    @pytest.fixture
    def mock_socket(self, mocker):
        socket = mocker.patch(
            target='wappstoiot.connections.sslsocket.ssl.SSLContext.wrap_socket',
            autospec=True
        )

        return socket

    @classmethod
    def setup_class(self):
        """
        Sets up the class.

        Sets locations to be used in test.

        """
        shutil.rmtree(self.temp, ignore_errors=True)
        self.temp.mkdir(exist_ok=True, parents=True)

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
        self.generate_certificates(name=url, network_uuid=uuid.uuid4())
        # rich.print(dir(mock_socket))
        mock_socket.return_value.recv.return_value = get_success_pkg(
            id="lkjghtrfty",
            timestamp=datetime.datetime.utcnow(),
        )
        try:
            wappstoiot.config(
                config_folder=Path(self.temp),
            )
        finally:
            wappstoiot.close()

        if url == 'wappsto.com':
            url = f"collector.{url}"

        mock_socket.return_value.connect.assert_called_with((f"{url}", port))

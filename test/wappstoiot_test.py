#! /usr/bin/env python3

import uuid
import shutil
import datetime
from pathlib import Path

import pytest

from utils.generators import client_certifi_gen
from utils import package_smithing as smithing

import wappstoiot


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
    def mock_ssl_socket(self, mocker):
        socket = mocker.patch(
            target='wappstoiot.connections.sslsocket.ssl.SSLContext.wrap_socket',
            autospec=True
        )

        return socket

    @pytest.fixture
    def mock_rw_socket(self, mocker):
        socket = mocker.patch(
            target='wappstoiot.connections.sslsocket.socket.socket',
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

    @classmethod
    def cleanup_class(self):
        """
        Sets up the class.

        Sets locations to be used in test.

        """
        shutil.rmtree(self.temp, ignore_errors=True)

    @pytest.mark.parametrize(
        "url, port",
        [
            ('wappsto.com', 443),
            ('qa.wappsto.com', 53005),
            ('dev.wappsto.com', 52005),
            ('staging.wappsto.com', 54005),
        ]
    )
    def test_connection(self, mock_rw_socket, mock_ssl_socket, url: str, port: int):
        self.generate_certificates(name=url, network_uuid=uuid.uuid4())
        mock_ssl_socket.return_value.recv.return_value = smithing.get_success_pkg(
            pkg_id="lkjghtrfty",
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

        mock_ssl_socket.return_value.connect.assert_called_with((f"{url}", port))

    def test_network_creation(self, mock_rw_socket, mock_ssl_socket):
        network_uuid = uuid.uuid4()
        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        cycle = smithing.get_network_create_cycle(
            network_uuid=network_uuid,
            changed=True
        )

        smithing.socket_generator(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket,
            cycle_list=cycle
        )

        try:
            wappstoiot.config(
                config_folder=Path(self.temp),
            )
            network = wappstoiot.createNetwork()
        finally:
            wappstoiot.close()

        smithing.fail_check()

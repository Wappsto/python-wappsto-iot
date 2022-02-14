#! /usr/bin/env python3

import uuid
import shutil
import datetime
from pathlib import Path

import pytest

from utils.generators import client_certifi_gen
from utils import package_smithing as smithing

import wappstoiot

# import logging
# from rich import traceback
# from rich.logging import RichHandler

# traceback.install(show_locals=True)

# logging.basicConfig(
#     level=logging.WARNING,
#     format="%(asctime)s - %(name)s - %(message)s",
#     handlers=[RichHandler()],
# )


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

        wappstoiot.config(
            config_folder=Path(self.temp),
        )
        network = wappstoiot.createNetwork()
        wappstoiot.close()

        smithing.fail_check()

    def test_device_creation(self, mock_rw_socket, mock_ssl_socket):
        network_uuid = uuid.uuid4()
        device_uuid = uuid.uuid4()
        device_name = "test"
        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        cycle = smithing.get_network_create_cycle(
            network_uuid=network_uuid,
            changed=True
        )
        cycle2 = smithing.get_device_create_cycle(
            network_uuid=network_uuid,
            empty=True,  # NOTE: parametrize options?
            changed=True,  # NOTE: parametrize options?
            device_uuid=device_uuid,
            device_name=device_name
        )
        cycle.extend(cycle2)

        smithing.socket_generator(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket,
            cycle_list=cycle
        )

        wappstoiot.config(
            config_folder=Path(self.temp),
        )
        network = wappstoiot.createNetwork()

        device = network.createDevice(name=device_name)

        wappstoiot.close()

        smithing.fail_check()

    @pytest.mark.parametrize(
        "permission",
        [
            wappstoiot.PermissionType.READWRITE,
            # wappstoiot.PermissionType.READ,
            # wappstoiot.PermissionType.WRITE,
            # wappstoiot.PermissionType.NONE
        ]
    )
    @pytest.mark.parametrize(
        "value_type",
        [
            (wappstoiot.ValueType.NUMBER),
            (wappstoiot.ValueType.STRING),
            # (wappstoiot.ValueType.BLOB),
            # (wappstoiot.ValueType.XML),
        ]
    )
    def test_value_creation(self, mock_rw_socket, mock_ssl_socket, value_type, permission):
        network_uuid = uuid.uuid4()
        device_uuid = uuid.uuid4()
        value_uuid = uuid.uuid4()
        device_name = "test"
        value_name = "moeller"
        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        cycle = smithing.get_network_create_cycle(
            network_uuid=network_uuid,
            changed=True
        )
        cycle2 = smithing.get_device_create_cycle(
            network_uuid=network_uuid,
            empty=True,
            changed=True,
            device_uuid=device_uuid,
            device_name=device_name,
            value_list=[value_uuid]
        )
        cycle.extend(cycle2)

        cycle3 = smithing.get_value_create_cycle(
            device_uuid=device_uuid,
            empty=True,    # NOTE: parametrize options?
            changed=True,  # NOTE: parametrize options?
            value_type=value_type,  # Make this needed?
            value_uuid=value_uuid,
            value_name=value_name,
            permission=permission
        )
        cycle.extend(cycle3)

        smithing.socket_generator(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket,
            cycle_list=cycle
        )

        wappstoiot.config(
            config_folder=Path(self.temp),
        )
        network = wappstoiot.createNetwork()

        device = network.createDevice(name=device_name)

        try:
            device.createValue(
                name=value_name,
                permission=permission,
                value_type=value_type
            )
        finally:
            wappstoiot.close()

        smithing.fail_check()

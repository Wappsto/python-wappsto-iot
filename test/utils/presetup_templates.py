import pathlib
import uuid
import shutil

import pytest

from typing import Any
from typing import Dict

from utils.generators import client_certifi_gen
from utils.wappstoserver import SimuServer
from utils import server_utils

import wappstoiot


class BaseConnection:

    temp = pathlib.Path(__file__).parent.parent / pathlib.Path('temp')

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
    def setup_class(cls):
        """
        Sets up the class.

        Sets locations to be used in test.

        """
        shutil.rmtree(cls.temp, ignore_errors=True)
        cls.temp.mkdir(exist_ok=True, parents=True)

    @classmethod
    def teardown_class(cls):
        """
        Sets up the class.

        Sets locations to be used in test.

        """
        shutil.rmtree(cls.temp, ignore_errors=True)


class BaseNetwork(BaseConnection):

    @pytest.fixture
    def mock_network_server(self, mock_rw_socket, mock_ssl_socket):
        network_uuid = uuid.uuid4()
        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        server = SimuServer(
            network_uuid=network_uuid,
            name="the_network"
        )
        server.get_socket(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket
        )
        return server


class BaseDevice(BaseNetwork):
    @pytest.fixture
    def mock_device_server(self, mock_network_server):
        device_uuid = uuid.uuid4()
        device_name = "the_device"

        mock_network_server.add_object(
            this_uuid=device_uuid,
            this_type='device',
            this_name=device_name,
            parent_uuid=mock_network_server.network_uuid
        )
        return mock_network_server

    @pytest.fixture
    def mock_value_rw_nr_server(self, mock_device_server):
        device_obj = mock_device_server.get_obj(name="the_device")

        value_uuid = uuid.uuid4()
        value_name = "the_value"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=wappstoiot.ValueTemplate.NUMBER,
            permission=wappstoiot.PermissionType.READWRITE
        )

        mock_device_server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_obj.uuid,
            extra_info=extra_info
        )
        return mock_device_server

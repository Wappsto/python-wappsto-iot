#! /usr/bin/env python3

import uuid
import shutil
import datetime
import time

from pathlib import Path
from typing import Any
from typing import Dict
from typing import Union

import pytest

from utils.generators import client_certifi_gen
from utils import pkg_smithing as smithing

from utils.wappstoserver import SimuServer
from utils import server_utils

import rich

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
        mock_ssl_socket.return_value.recv.return_value = smithing.success_pkg(
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

        server = SimuServer(
            network_uuid=network_uuid,
            name=""
        )
        server.get_socket(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket
        )

        wappstoiot.config(
            config_folder=Path(self.temp),
            fast_send=True  # NOTE: parametrize options.
        )
        try:
            wappstoiot.createNetwork("TestNetwork")
        finally:
            wappstoiot.close()

        server.fail_check()

    @pytest.mark.parametrize(
        "device_exist",
        [True, False]
    )
    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_device_creation(
        self,
        mock_rw_socket,
        mock_ssl_socket,
        device_exist: bool,
        fast_send: bool,
        differ: bool = False  # TODO:
    ):
        # TODO: try with filling out the extra data.
        # TODO: Have to be able to test if it make POSTs that it should not do.
        network_name = "TestNetwork"  # Test without this.
        network_uuid = uuid.uuid4()
        device_uuid = uuid.uuid4()
        device_name = "test"
        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        server = SimuServer(
            network_uuid=network_uuid,
            name=network_name
        )
        server.get_socket(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket
        )

        if device_exist:
            server.add_object(
                this_uuid=device_uuid,
                this_type='device',
                this_name=device_name,
                parent_uuid=network_uuid
            )

        wappstoiot.config(
            config_folder=Path(self.temp),
            fast_send=fast_send
        )
        network = wappstoiot.createNetwork(name=network_name)

        try:
            network.createDevice(name=device_name)
        finally:
            wappstoiot.close()

        server.fail_check()

        assert len(server.data_in) == 3 if device_exist else 3

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
        "value_template",
        [
            # *wappstoiot.ValueTemplate
            (wappstoiot.ValueTemplate.NUMBER),
            # (wappstoiot.ValueTemplate.STRING),
            # (wappstoiot.ValueTemplate.BLOB),
            # (wappstoiot.ValueTemplate.XML),
        ]
    )
    @pytest.mark.parametrize(
        "value_exist",
        [
            True,
            False
        ]
    )
    @pytest.mark.parametrize(
        "fast_send",
        [
            True,
            False
        ]
    )
    def test_value_creation(
        self,
        mock_rw_socket,
        mock_ssl_socket,
        value_template: wappstoiot.ValueTemplate,
        permission: wappstoiot.PermissionType,
        fast_send: bool,
        value_exist: bool,
    ):
        # Should also be able to set what existed of states before this creation.
        network_uuid = uuid.uuid4()
        device_uuid = uuid.uuid4()
        if value_exist:
            value_uuid = uuid.uuid4()
        network_name = "TestNetwork"
        device_name = "test"
        value_name = "moeller"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=value_template,
            permission=permission
        )

        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        server = SimuServer(
            network_uuid=network_uuid,
            name=network_name
        )
        server.get_socket(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket
        )

        server.add_object(
            this_uuid=device_uuid,
            this_type='device',
            this_name=device_name,
            parent_uuid=network_uuid
        )

        if value_exist:
            # TODO: Test with Children & extra_info Permission set, & w/ conflict. (RW + 1 child)
            server.add_object(
                this_uuid=value_uuid,
                this_type='value',
                this_name=value_name,
                parent_uuid=device_uuid,
                extra_info=extra_info
            )
            # TODO: Add states.

        wappstoiot.config(
            config_folder=Path(self.temp),
            fast_send=fast_send
        )

        network = wappstoiot.createNetwork(name=network_name)

        device = network.createDevice(name=device_name)

        try:
            value = device.createValue(
                name=value_name,
                permission=permission,
                value_template=value_template
            )
        finally:
            wappstoiot.close()

        server.fail_check()

        state_count = len(server.objects.get(value.uuid, {}).children)

        expected = 5 if value_exist else 5

        if permission in [wappstoiot.PermissionType.READWRITE, wappstoiot.PermissionType.WRITEREAD]:
            assert state_count == 2, "The number of states should be 2, when it is a read/write."
            # NOTE: if value_exist will be one less after the just-in-time retrieve.
            expected += 2

        elif permission in [wappstoiot.PermissionType.READ, wappstoiot.PermissionType.WRITE]:
            assert state_count == 1, "The number of states should be 1."
            expected += 1

        elif permission == wappstoiot.PermissionType.NONE:
            assert state_count == 0, "No state for a virtual Value!"

        msg = f"Package received count Failed. should be {expected}, was: {len(server.data_in)}"
        assert len(server.data_in) == expected, msg

        # assert False

    # def test_state_creation(
    #     self,
    #     mock_rw_socket,
    #     mock_ssl_socket,
    #     value_template: wappstoiot.ValueTemplate,
    #     permission: wappstoiot.PermissionType,
    #     fast_send: bool,
    #     state_exist: bool,
    # ):
    #     pass

    # def test_custom_number_creation(
    #     self,
    #     mock_rw_socket,
    #     mock_ssl_socket,
    #     value_template: wappstoiot.ValueTemplate,
    #     permission: wappstoiot.PermissionType,
    #     fast_send: bool,
    #     value_exist: bool,
    # ):
    #     pass

    # def test_custom_string_creation(
    #     self,
    #     mock_rw_socket,
    #     mock_ssl_socket,
    #     value_template: wappstoiot.ValueTemplate,
    #     permission: wappstoiot.PermissionType,
    #     fast_send: bool,
    #     value_exist: bool,
    # ):
    #     pass

    # def test_custom_blob_creation(
    #     self,
    #     mock_rw_socket,
    #     mock_ssl_socket,
    #     value_template: wappstoiot.ValueTemplate,
    #     permission: wappstoiot.PermissionType,
    #     fast_send: bool,
    #     value_exist: bool,
    # ):
    #     pass

    # def test_custom_xml_creation(
    #     self,
    #     mock_rw_socket,
    #     mock_ssl_socket,
    #     value_template: wappstoiot.ValueTemplate,
    #     permission: wappstoiot.PermissionType,
    #     fast_send: bool,
    #     value_exist: bool,
    # ):
    #     pass

    # @pytest.mark.parametrize(
    #     "permission",
    #     [
    #         wappstoiot.PermissionType.READWRITE,
    #         # wappstoiot.PermissionType.READ,
    #         # wappstoiot.PermissionType.WRITE,
    #         # wappstoiot.PermissionType.NONE
    #     ]
    # )
    # @pytest.mark.parametrize(
    #     "min,max,step",
    #     [
    #         (0, 1, 1),
    #     ]
    # )
    # @pytest.mark.parametrize(
    #     "value_exist",
    #     [True, False]
    # )
    # @pytest.mark.parametrize(
    #     "fast_send",
    #     [True, False]
    # )
    # def test_number_value(
    #     self,
    #     mock_rw_socket,
    #     mock_ssl_socket,
    #     permission: wappstoiot.PermissionType,
    #     fast_send: bool,
    #     value_exist: bool,
    #     min: int,
    #     max: int,
    #     step: int,
    # ):
    #     value_template = wappstoiot.ValueTemplate.NUMBER
    #     pass

    @pytest.mark.parametrize(
        "permission",
        [
            wappstoiot.PermissionType.READWRITE,
            wappstoiot.PermissionType.READ,
            # wappstoiot.PermissionType.WRITE,
            # wappstoiot.PermissionType.NONE
        ]
    )
    @pytest.mark.parametrize(
        "value_template",
        [
            (wappstoiot.ValueTemplate.NUMBER),
            (wappstoiot.ValueTemplate.STRING),
            # (wappstoiot.ValueTemplate.BLOB),
            # (wappstoiot.ValueTemplate.XML),
        ]
    )
    @pytest.mark.parametrize(
        "fast_send",
        [
            True,
            False
        ]
    )
    @pytest.mark.parametrize(
        "data_value",
        [
            0,
            # float("nan"),
            # "hej"
            # "æøå"
        ]
    )
    def test_report_changes(
        self,
        mock_rw_socket,
        mock_ssl_socket,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):
        # Should also be able to set what existed of states before this creation.
        network_uuid = uuid.uuid4()
        device_uuid = uuid.uuid4()
        value_uuid = uuid.uuid4()
        network_name = "TestNetwork"
        device_name = "test"
        value_name = "moeller"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=value_template,
            permission=permission
        )

        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        server = SimuServer(
            network_uuid=network_uuid,
            name=network_name
        )
        server.get_socket(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket
        )

        server.add_object(
            this_uuid=device_uuid,
            this_type='device',
            this_name=device_name,
            parent_uuid=network_uuid
        )

        server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_uuid,
            extra_info=extra_info
        )

        wappstoiot.config(
            config_folder=Path(self.temp),
            fast_send=fast_send
        )

        network = wappstoiot.createNetwork(name=network_name)

        device = network.createDevice(name=device_name)

        value = device.createValue(
            name=value_name,
            permission=permission,
            value_template=value_template
        )
        try:
            value.report(data_value)
        finally:
            wappstoiot.close()

        server.fail_check()
        state = server_utils.get_state_obj(
            server=server,
            value_uuid=value_uuid,
            state_type="Report"
        )
        data_value = str(data_value) if value_template != wappstoiot.ValueTemplate.NUMBER else data_value
        assert value.getReportData() == data_value, "'getReportData' did not return expected data."
        assert state.extra_info.get('data') == str(data_value), "The server did not have the expected data."

    @pytest.mark.parametrize(
        "permission",
        [
            wappstoiot.PermissionType.READWRITE,
            # wappstoiot.PermissionType.READ,
            wappstoiot.PermissionType.WRITE,
            # wappstoiot.PermissionType.NONE
        ]
    )
    @pytest.mark.parametrize(
        "value_template",
        [
            (wappstoiot.ValueTemplate.NUMBER),
            # (wappstoiot.ValueTemplate.STRING),
            # (wappstoiot.ValueTemplate.BLOB),
            # (wappstoiot.ValueTemplate.XML),
        ]
    )
    @pytest.mark.parametrize(
        "fast_send",
        [
            # True,
            False
        ]
    )
    @pytest.mark.parametrize(
        "data_value",
        [
            0,
            # float("nan"),
            # "hej",
            # "æøå",
        ]
    )
    def test_control_changes(
        self,
        mock_rw_socket,
        mock_ssl_socket,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):
        # Should also be able to set what existed of states before this creation.
        network_uuid = uuid.uuid4()
        device_uuid = uuid.uuid4()
        value_uuid = uuid.uuid4()
        network_name = "TestNetwork"
        device_name = "test"
        value_name = "moeller"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=value_template,
            permission=permission
        )

        url = "wappsto.com"
        self.generate_certificates(name=url, network_uuid=network_uuid)

        server = SimuServer(
            network_uuid=network_uuid,
            name=network_name
        )
        server.get_socket(
            mock_rw_socket=mock_rw_socket,
            mock_ssl_socket=mock_ssl_socket
        )

        server.add_object(
            this_uuid=device_uuid,
            this_type='device',
            this_name=device_name,
            parent_uuid=network_uuid
        )

        server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_uuid,
            extra_info=extra_info
        )

        wappstoiot.config(
            config_folder=Path(self.temp),
            fast_send=fast_send
        )

        network = wappstoiot.createNetwork(name=network_name)

        device = network.createDevice(name=device_name)

        value = device.createValue(
            name=value_name,
            permission=permission,
            value_template=value_template
        )

        the_control_value = None
        timestamp = datetime.datetime.utcnow()

        @value.onControl
        def control_test(obj, value):
            nonlocal the_control_value
            the_control_value = value
            print(f"OnControl: {value}")

        state = server_utils.get_state_obj(
            server=server,
            value_uuid=value_uuid,
            state_type="Control"
        )

        try:
            server.send_control(
                obj_uuid=state.self_uuid,
                data=data_value,
                timestamp=timestamp,
            )
            time.sleep(1)
        finally:
            wappstoiot.close()

        server.fail_check()

        # print(f"{state}")

        data_value = str(data_value) if value_template != wappstoiot.ValueTemplate.NUMBER else data_value
        assert the_control_value == data_value  # , "Did not receive the expected data."
        assert state.extra_info.get('data') == data_value  # , "The server did not have the expected data."
        assert value.getControlData() == data_value  # , "'getControlData' did not return expected data."

    # def test_send_delete_value(self):
    #     pass

    # def test_send_delete_device(self):
    #     pass

    # def test_send_delete_network(self):
    #     pass

    # def test_receive_delete_value(self):
    #     pass

    # def test_receive_delete_device(self):
    #     pass

    # def test_receive_delete_network(self):
    #     pass

    # def test_examples(self, mock_rw_socket, mock_ssl_socket):
    #     # TODO:!!!!!!!!
    #     pass

    # def test_replays_w_errors(self,):
    #     pass

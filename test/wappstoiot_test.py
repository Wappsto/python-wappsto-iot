#! /usr/bin/env python3

import uuid
import datetime
import time

from typing import Any
from typing import Dict
from typing import Union

import pytest

from utils import pkg_smithing as smithing

from utils.wappstoserver import SimuServer
from utils import server_utils

from utils.presetup_templates import BaseConnection
from utils.presetup_templates import BaseNetwork
from utils.presetup_templates import BaseDevice

import rich

import wappstoiot

# import logging
# from rich import traceback
# from rich.logging import RichHandler

# traceback.install(show_locals=True)

# logging.basicConfig(
#     level=logging.WARNING,
#     format="%(asctime)s - %(name)s - %(message)s",
#     handlers=[RichHandler()],and
# )


class TestConnection(BaseConnection):
    """
    TestJsonLoadClass instance.

    Tests loading json files in wappsto.

    """
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
                config_folder=self.temp,
            )
        finally:
            wappstoiot.close()

        if url == 'wappsto.com':
            url = f"collector.{url}"

        mock_ssl_socket.return_value.connect.assert_called_with((f"{url}", port))


class TestNetwork(BaseConnection):

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    @pytest.mark.parametrize(
        "network_name",
        [
            "the_network",  # The Preexisting name
            "lkjskhbdf"
        ]
    )
    def test_network_creation(
        self,
        mock_rw_socket,
        mock_ssl_socket,
        fast_send: bool,
        network_name: str
    ):
        network_uuid = uuid.uuid4()
        name_mismatch = network_name != "the_network"
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

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )
        try:
            wappstoiot.createNetwork(network_name)
        finally:
            wappstoiot.close()

        server.fail_check()

        network_obj = server.get_network_obj()

        assert len(server.data_in) == 2 if name_mismatch else 1

        assert network_obj.name == network_name
        assert network_obj.uuid == network_uuid
        # UNSURE: Description set test?


class TestDevice(BaseNetwork):

    @pytest.mark.parametrize(
        "device_exist",
        [True, False]
    )
    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    @pytest.mark.parametrize(
        "device_name",
        [
            "the_device",  # The Preexisting name
            "lkjskhbdf"
        ]
    )
    def test_device_creation(
        self,
        mock_network_server,
        device_exist: bool,
        fast_send: bool,
        device_name: str,
        data_mismatch: bool = False  # TODO:
    ):
        # TODO: try with filling out the extra data.
        device_uuid = uuid.uuid4()

        if device_exist:
            mock_network_server.add_object(
                this_uuid=device_uuid,
                this_type='device',
                this_name='the_device',
                parent_uuid=mock_network_server.network_uuid
            )

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )
        network = wappstoiot.createNetwork(name=mock_network_server.network_name)

        try:
            network.createDevice(name=device_name)
        finally:
            wappstoiot.close()

        mock_network_server.fail_check()

        expected_pkg = 2 + 1  # +1 until expand=0 implemented.
        if data_mismatch and device_exist:
            expected_pkg += 1
        # if not device_exist:
        #     expected_pkg += 1

        assert len(mock_network_server.data_in) == expected_pkg
        # TODO: More tests. like the test of name, uuid & description are right.


class TestValue(BaseDevice):

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
        mock_device_server,
        value_template: wappstoiot.ValueTemplate,
        permission: wappstoiot.PermissionType,
        fast_send: bool,
        value_exist: bool,
    ):
        # Should also be able to set what existed of states before this creation.
        device_obj = mock_device_server.get_obj(name="the_device")

        if value_exist:
            value_uuid = uuid.uuid4()
        value_name = "moeller"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=value_template,
            permission=permission
        )

        if value_exist:
            # TODO: Test with Children & extra_info Permission set, & w/ conflict. (RW + 1 child)
            mock_device_server.add_object(
                this_uuid=value_uuid,
                this_type='value',
                this_name=value_name,
                parent_uuid=device_obj.uuid,
                extra_info=extra_info
            )
            # TODO: Add states.

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )

        network = wappstoiot.createNetwork(name=mock_device_server.network_name)

        device = network.createDevice(name=device_obj.name)

        try:
            value = device.createValue(
                name=value_name,
                permission=permission,
                value_template=value_template
            )
        finally:
            wappstoiot.close()

        mock_device_server.fail_check()

        state_count = len(mock_device_server.objects.get(value.uuid, {}).children)

        expected = 5 if value_exist else 5

        if value_exist:
            assert value.uuid == value_uuid
        assert value.name == value_name

        if permission in [wappstoiot.PermissionType.READWRITE, wappstoiot.PermissionType.WRITEREAD]:
            assert state_count == 2, "The number of states should be 2, when it is a read/write."
            # NOTE: if value_exist will be one less after the just-in-time retrieve.
            expected += 2

        elif permission in [wappstoiot.PermissionType.READ, wappstoiot.PermissionType.WRITE]:
            assert state_count == 1, "The number of states should be 1."
            expected += 1

        elif permission == wappstoiot.PermissionType.NONE:
            assert state_count == 0, "No state for a virtual Value!"

        msg = f"Package received count Failed. should be {expected}, was: {len(mock_device_server.data_in)}"
        assert len(mock_device_server.data_in) == expected, msg

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
            # *wappstoiot.ValueTemplate,
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
            float("nan"),
            "NA",
        ]
    )
    def test_report_changes(
        self,
        mock_device_server,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):
        # Should also be able to set what existed of states before this creation.
        device_obj = mock_device_server.get_obj(name="the_device")

        value_uuid = uuid.uuid4()
        value_name = "moeller"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=value_template,
            permission=permission
        )

        mock_device_server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_obj.uuid,
            extra_info=extra_info
        )

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )

        network = wappstoiot.createNetwork(name=mock_device_server.network_name)

        device = network.createDevice(name=device_obj.name)

        value = device.createValue(
            name=value_name,
            permission=permission,
            value_template=value_template
        )

        timestamp = datetime.datetime.utcnow()

        try:
            value.report(data_value, timestamp)
            print(value.report_state)
        finally:
            wappstoiot.close()

        mock_device_server.fail_check()
        state = server_utils.get_state_obj(
            server=mock_device_server,
            value_uuid=value_uuid,
            state_type="Report"
        )
        is_number_type = wappstoiot.modules.template.valueSettings[value_template].value_type == wappstoiot.modules.template.ValueBaseType.NUMBER
        if not is_number_type:
            data_value = str(data_value)

        assert state.extra_info.get('data') == str(data_value)  # , "The server did not have the expected data."
        if data_value != data_value:
            temp_control_value = value.getReportData()
            assert temp_control_value != temp_control_value
        else:
            if data_value == 'NA' and is_number_type:
                data_value = None
            assert value.getReportData() == data_value  # , "'getControlData' did not return expected data."

        # str_timestamp = smithing.convert_timestamp(timestamp)
        assert state.extra_info.get('timestamp') == timestamp
        assert value.getReportTimestamp() == timestamp

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
            # *wappstoiot.ValueTemplate,
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
            float("nan"),
            "NA",
        ]
    )
    def test_control_changes(
        self,
        mock_device_server,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):
        # Should also be able to set what existed of states before this creation.
        device_obj = mock_device_server.get_obj(name="the_device")

        value_uuid = uuid.uuid4()
        value_name = "moeller"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=value_template,
            permission=permission
        )

        mock_device_server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_obj.uuid,
            extra_info=extra_info
        )

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )

        network = wappstoiot.createNetwork(name=mock_device_server.network_name)

        device = network.createDevice(name=device_obj.name)

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
            server=mock_device_server,
            value_uuid=value_uuid,
            state_type="Control"
        )

        try:
            mock_device_server.send_control(
                obj_uuid=state.uuid,
                data=data_value,
                timestamp=timestamp,
            )
            start = time.time() + 1
            while the_control_value is None:
                if start <= time.time():
                    break
                time.sleep(0.1)
            # control_date = value.getControlData()
            print(value.control_state)
        finally:
            wappstoiot.close()

        mock_device_server.fail_check()

        # print(f"{state}")
        is_number_type = wappstoiot.modules.template.valueSettings[value_template].value_type == wappstoiot.modules.template.ValueBaseType.NUMBER
        if not is_number_type:
            data_value = str(data_value)

        assert state.extra_info.get('data') == str(data_value)  # , "The server did not have the expected data."
        if data_value != data_value:
            assert the_control_value != the_control_value
            # assert the_control_value == data_value  # , "Did not receive the expected data."
            # assert value.getControlData() == data_value  # , "'getControlData' did not return expected data."
            temp_control_value = value.getControlData()
            assert temp_control_value != temp_control_value
        else:
            assert the_control_value == data_value  # , "Did not receive the expected data."
            # assert state.extra_info.get('data') == str(data_value)  # , "The server did not have the expected data."
            if data_value == 'NA' and is_number_type:
                data_value = None
            assert value.getControlData() == data_value  # , "'getControlData' did not return expected data."

        # str_timestamp = smithing.convert_timestamp(timestamp)
        assert state.extra_info.get('timestamp') == timestamp
        assert value.getControlTimestamp() == timestamp

    # def test_receive_report_value(self):
    #     pass

    # def test_send_control_value(self):
    #     pass

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

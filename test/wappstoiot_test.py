#! /usr/bin/env python3

import datetime
import json
import time
import uuid

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
from utils.presetup_templates import BaseValue

import wappstoiot


class TestConnection(BaseConnection):
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


class TestNetwork(BaseNetwork):

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
    def test_creation(
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
        server_utils.fast_send_check(
            pkg_list=server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_on_delete(
        self,
        mock_network_server,
        fast_send: bool,
    ):
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(mock_network_server.network_name)

            network_deleted: bool = False

            @network.onDelete
            def network_rm(obj):
                nonlocal network_deleted
                network_deleted = True

            mock_network_server.send_delete(
                obj_uuid=mock_network_server.network_uuid,
                obj_type="network"
            )
            start = time.time() + 1
            while network_deleted is False:
                if start <= time.time():
                    break
                time.sleep(0.1)
        finally:
            wappstoiot.close()

        mock_network_server.fail_check()

        assert len(mock_network_server.data_in) == 2
        assert network_deleted, "Didn't receive a Delete"
        server_utils.fast_send_check(
            pkg_list=mock_network_server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_delete(
        self,
        mock_network_server,
        fast_send: bool,
    ):
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(mock_network_server.network_name)
            network.delete()
        finally:
            wappstoiot.close()

        mock_network_server.fail_check()

        assert len(mock_network_server.data_in) == 2

        del_pkg = json.loads(mock_network_server.data_in[-1])
        assert del_pkg.get('method') == 'DELETE'
        assert del_pkg.get('params', {}).get('url') == f'/network/{mock_network_server.network_uuid}'

        server_utils.fast_send_check(
            pkg_list=mock_network_server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_ping(
        self,
        mock_network_server,
        fast_send: bool,
    ):
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send,
                ping_pong_period_sec=1
            )
            wappstoiot.createNetwork(mock_network_server.network_name)
            start = time.time() + 2
            while len(mock_network_server.data_in) < 2:
                if start <= time.time():
                    break
                time.sleep(0.01)
        finally:
            wappstoiot.close()

        mock_network_server.fail_check()

        last_pkg = json.loads(mock_network_server.data_in[-1])

        print(mock_network_server.data_in)

        assert last_pkg.get('method') == 'HEAD'
        assert last_pkg.get('params', {}).get('url') == '/network'
        server_utils.fast_send_check(
            pkg_list=mock_network_server.data_in,
            fast_send=fast_send
        )


class TestDevice(BaseDevice):

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
    def test_creation(
        self,
        mock_network_server,
        device_exist: bool,
        fast_send: bool,
        device_name: str,
        data_mismatch: bool = False  # TODO:
    ):
        # TODO: try with filling out the extra data.
        # TODO: Test with device change Permission and/or ValueTemplate.
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
        server_utils.fast_send_check(
            pkg_list=mock_network_server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_on_delete(
        self,
        mock_device_server,
        fast_send: bool,
        data_mismatch: bool = False  # TODO:
    ):
        # TODO: try with filling out the extra data.
        device_obj = mock_device_server.get_obj(name="the_device")

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )
        network = wappstoiot.createNetwork(name=mock_device_server.network_name)
        device = network.createDevice(name=device_obj.name)
        device_deleted = False

        @device.onDelete
        def device_rm(obj):
            nonlocal device_deleted
            device_deleted = True
        try:
            mock_device_server.send_delete(
                obj_uuid=device_obj.uuid,
                obj_type="device"
            )
            start = time.time() + 1
            while device_deleted is False:
                if start <= time.time():
                    break
                time.sleep(0.1)
        finally:
            wappstoiot.close()

        mock_device_server.fail_check()
        assert device_deleted, "Didn't receive a Delete"

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_delete(
        self,
        mock_device_server,
        fast_send: bool,
        data_mismatch: bool = False  # TODO:
    ):
        # TODO: try with filling out the extra data.
        device_obj = mock_device_server.get_obj(name="the_device")

        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name="the_device")
            device.delete()
        finally:
            wappstoiot.close()

        mock_device_server.fail_check()

        del_pkg = json.loads(mock_device_server.data_in[-1])

        assert del_pkg.get('method') == 'DELETE'
        assert del_pkg.get('params', {}).get('url') == f'/device/{device_obj.uuid}'
        
        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )


class TestValue(BaseValue):

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
    def test_creation(
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

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [
            True,
            False
        ]
    )
    def test_on_delete(
        self,
        mock_value_rw_nr_server,
        fast_send: bool,
    ):
        device_obj = mock_value_rw_nr_server.get_obj(name="the_device")
        value_obj = mock_value_rw_nr_server.get_obj(name="the_value")

        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_value_rw_nr_server.network_name)
            device = network.createDevice(name=device_obj.name)
            value = device.createValue(
                name=value_obj.name,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=wappstoiot.ValueTemplate.NUMBER
            )
            device_deleted = False

            @value.onDelete
            def value_delete(obj):
                nonlocal device_deleted
                device_deleted = True
            mock_value_rw_nr_server.send_delete(
                obj_uuid=value_obj.uuid,
                obj_type="value"
            )
            start = time.time() + 1
            while device_deleted is False:
                if start <= time.time():
                    break
                time.sleep(0.1)
        finally:
            wappstoiot.close()

        mock_value_rw_nr_server.fail_check()
        assert device_deleted, "Didn't receive a Delete"

        server_utils.fast_send_check(
            pkg_list=mock_value_rw_nr_server.data_in,
            fast_send=fast_send
        )

    @pytest.mark.parametrize(
        "fast_send",
        [
            True,
            False
        ]
    )
    def test_delete(
        self,
        mock_value_rw_nr_server,
        fast_send: bool,
    ):
        device_obj = mock_value_rw_nr_server.get_obj(name="the_device")
        value_obj = mock_value_rw_nr_server.get_obj(name="the_value")

        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_value_rw_nr_server.network_name)
            device = network.createDevice(name=device_obj.name)
            value = device.createValue(
                name=value_obj.name,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=wappstoiot.ValueTemplate.NUMBER
            )

            value.delete()
        finally:
            wappstoiot.close()

        mock_value_rw_nr_server.fail_check()
        del_pkg = json.loads(mock_value_rw_nr_server.data_in[-1])

        assert del_pkg.get('method') == 'DELETE'
        assert del_pkg.get('params', {}).get('url') == f'/value/{value_obj.uuid}'

        server_utils.fast_send_check(
            pkg_list=mock_value_rw_nr_server.data_in,
            fast_send=fast_send
        )

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
    def test_report(
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

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

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
    def test_on_control(
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

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

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

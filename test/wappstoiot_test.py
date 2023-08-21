#!/usr/bin/env python3

import datetime
import json
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
        self.remove_temps()


class TestOfflineStorage(BaseNetwork):

    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_active(
        self,
        mock_network_server,
        fast_send: bool,
    ):
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send,
                offline_storage=True
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
            server_utils.wait_until_or(lambda: network_deleted, 1)
        finally:
            wappstoiot.close()

        mock_network_server.fail_check()

        assert len(mock_network_server.data_in) == 2
        assert network_deleted, "Didn't receive a Delete"
        server_utils.fast_send_check(
            pkg_list=mock_network_server.data_in,
            fast_send=fast_send
        )
        self.remove_temps()

    @pytest.mark.skip("WIP!")
    @pytest.mark.parametrize(
        "fast_send",
        [True, False]
    )
    def test_old_storage(
        self,
        mock_network_server,
        fast_send: bool,
    ):
        """
        Test with already saved data in the storage.

        The result should be it sends the data, and removes it afterward.
        """
        server_utils.generate_storage()

        pass

        self.remove_temps()


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
    @pytest.mark.parametrize(
        "description",
        [
            "The Description",
        ]
    )
    def test_creation(
        self,
        mock_rw_socket,
        mock_ssl_socket,
        fast_send: bool,
        network_name: str,
        description: str
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
            network = wappstoiot.createNetwork(
                name=network_name,
                description=description
            )
        finally:
            wappstoiot.close()

        server.fail_check()

        network_obj = server.get_network_obj()

        assert len(server.data_in) == 2 if name_mismatch else 1

        assert network_obj.name == network_name == network.name
        assert network_obj.uuid == network_uuid == network.uuid
        assert description == network_obj.extra_info.get('description') == network.element.description

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
            server_utils.wait_until_or(lambda: network_deleted, 1)
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
            server_utils.wait_until_or(
                lambda: len(mock_network_server.data_in) >= 2,
                2
            )
        finally:
            wappstoiot.close()

        # To ensure that the Ping thread have closed, so the next test do not fail.
        server_utils.wait_until_or(
            lambda: len(mock_network_server.data_in) >= 3,
            2
        )

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
    @pytest.mark.parametrize(
        "description",
        [
            "",
            "Some Description"
        ]
    )
    def test_creation(
        self,
        mock_network_server,
        device_exist: bool,
        fast_send: bool,
        device_name: str,
        description: str,
        # manufacturer: str,
        # product: str,
        # version: str,
        # protocol: str,
        # communication: str,
        # serial: str,
        # data_mismatch: bool = False  # TODO:
    ):
        # TODO: try with filling out the extra data.
        # TODO: Test with device change Permission and/or ValueTemplate.
        device_uuid = uuid.uuid4()

        if device_exist:
            mock_network_server.add_object(
                this_uuid=device_uuid,
                this_type='device',
                this_name=device_name,
                parent_uuid=mock_network_server.network_uuid
            )

        wappstoiot.config(
            config_folder=self.temp,
            fast_send=fast_send
        )
        network = wappstoiot.createNetwork(name=mock_network_server.network_name)

        try:
            device = network.createDevice(
                name=device_name,
                description=description
            )
        finally:
            wappstoiot.close()

        mock_network_server.fail_check()
        device_obj = mock_network_server.get_obj(name=device_name)

        data_mismatch = description != ''

        expected_pkg = 2 + 1  # +1 until expand=0 implemented.
        if data_mismatch and device_exist:
            expected_pkg += 1

        assert len(mock_network_server.data_in) == expected_pkg

        # TODO: More tests. like the test of name, uuid & description are right.
        if 'the_device' == device_name and device_exist:
            assert device_uuid == device.uuid
        assert device_name == device_obj.name
        assert device_name == device.name
        assert description == device_obj.extra_info.get("description", '')
        assert description == device.element.description

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
            server_utils.wait_until_or(lambda: device_deleted, 1)
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
        [True, False]
    )
    @pytest.mark.parametrize(
        "value_template",
        [
            *wappstoiot.ValueTemplate
        ]
    )
    def test_creation_of_templates(
        self,
        mock_device_server,
        fast_send: bool,
        value_template: wappstoiot.ValueTemplate,
    ):
        value_name = "the_value"
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name="the_device")
            value = device.createValue(
                name=value_name,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=value_template
            )

        finally:
            wappstoiot.close()

        value_obj = mock_device_server.get_obj(name=value_name)

        mock_device_server.fail_check()

        # TODO: Make LOTS of TESTs!!!

        server_utils.is_base_type(value_obj, value_template)

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )
        # assert False

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
        "fast_send",
        [True, False]
    )
    @pytest.mark.parametrize(
        "value_name",
        [
            "the_value",
            "lkjskhbdf"
        ]
    )
    @pytest.mark.parametrize(
        "vtype,vmin,vmax,step,unit,description,si_conversion,period,delta,mapping,meaningful_zero,ordered_mapping",
        [
            ["Test_Number", 0, 10, 1, "tal", "TestingDescription.", "km/km", 74, 42, {"1": "First", "2": "Others"}, False, False],
        ]
    )
    def test_createNumberValue(
        self,
        mock_device_server,
        fast_send: bool,
        value_name: str,
        permission: wappstoiot.PermissionType,
        vtype: str,
        vmin: Union[int, float],
        vmax: Union[int, float],
        step: Union[int, float],
        unit: str,
        description: str,
        si_conversion: str,
        period: int,  # in Sec
        delta: Union[int, float],
        mapping: Dict[str, str],
        meaningful_zero: bool,
        ordered_mapping: bool,
    ):
        # TODO: Test Illegal Names!
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name="the_device")
            value = device.createNumberValue(
                name=value_name,
                permission=permission,
                type=vtype,
                min=vmin,
                max=vmax,
                step=step,
                unit=unit,
                description=description,
                si_conversion=si_conversion,
                period=period,
                delta=delta,
                mapping=mapping,
                meaningful_zero=meaningful_zero,
                ordered_mapping=ordered_mapping,
            )

        finally:
            wappstoiot.close()

        value_obj = mock_device_server.get_obj(name=value_name)

        mock_device_server.fail_check()

        print(value_obj)

        assert value_name == value_obj.name == value.name
        assert value_obj.uuid == value.uuid
        assert vtype == value_obj.extra_info.get("type") == value.element.type
        assert vmin == value_obj.extra_info.get('number', {}).get("min") == value.element.number.min
        assert vmax == value_obj.extra_info.get('number', {}).get("max") == value.element.number.max
        assert step == value_obj.extra_info.get('number', {}).get("step") == value.element.number.step
        assert unit == value_obj.extra_info.get('number', {}).get("unit") == value.element.number.unit
        assert description == value_obj.extra_info.get("description") == value.element.description
        assert si_conversion == value_obj.extra_info.get('number', {}).get("si_conversion") == value.element.number.si_conversion
        assert str(period) == value_obj.extra_info.get("period") == value.element.period
        assert mapping.items() == value_obj.extra_info.get('number', {}).get("mapping").items() == value.element.number.mapping.items()
        assert meaningful_zero == value_obj.extra_info.get('number', {}).get("meaningful_zero") == value.element.number.meaningful_zero
        assert ordered_mapping == value_obj.extra_info.get('number', {}).get("ordered_mapping") == value.element.number.ordered_mapping

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

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
        "fast_send",
        [True, False]
    )
    @pytest.mark.parametrize(
        "value_name",
        [
            "the_value",
            "lkjskhbdf"
        ]
    )
    @pytest.mark.parametrize(
        "vtype,vmax,encoding,description,period",
        [
            ["Test_String", 10, "UTF-8", "TestingDescription.", 74],
        ]
    )
    def test_createStringValue(
        self,
        mock_device_server,
        fast_send: bool,
        value_name: str,
        permission: wappstoiot.PermissionType,
        vtype: str,
        vmax: Union[int, float],
        encoding: str,
        description: str,
        period: int,  # in Sec  # UNSURE: How to test this in a short time period?
    ):
        # TODO: Test Illegal Names!
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name="the_device")
            value = device.createStringValue(
                name=value_name,
                permission=permission,
                type=vtype,
                max=vmax,
                encoding=encoding,
                description=description,
                period=period
            )

        finally:
            wappstoiot.close()

        value_obj = mock_device_server.get_obj(name=value_name)

        mock_device_server.fail_check()

        print(value_obj)

        assert value_name == value_obj.name == value.name
        assert value_obj.uuid == value.uuid
        assert encoding == value_obj.extra_info.get('string', {}).get("encoding") == value.element.string.encoding
        assert description == value_obj.extra_info.get("description") == value.element.description
        assert str(period) == value_obj.extra_info.get("period") == value.element.period
        assert vtype == value_obj.extra_info.get("type") == value.element.type
        assert vmax == value_obj.extra_info.get('string', {}).get("max") == value.element.string.max

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

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
        "fast_send",
        [True, False]
    )
    @pytest.mark.parametrize(
        "value_name",
        [
            "the_value",
            "lkjskhbdf"
        ]
    )
    @pytest.mark.parametrize(
        "vtype,vmax,encoding,description,period",
        [
            ["Test_Blob", 10, "Base64", "TestingDescription.", 74],
        ]
    )
    def test_createBlobValue(
        self,
        mock_device_server,
        fast_send: bool,
        value_name: str,
        permission: wappstoiot.PermissionType,
        vtype: str,
        vmax: Union[int, float],
        encoding: str,
        description: str,
        period: int,  # in Sec  # UNSURE: How to test this in a short time period?
    ):
        # TODO: Test Illegal Names!
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name="the_device")
            value = device.createBlobValue(
                name=value_name,
                permission=permission,
                type=vtype,
                max=vmax,
                encoding=encoding,
                description=description,
                period=period
            )

        finally:
            wappstoiot.close()

        value_obj = mock_device_server.get_obj(name=value_name)

        mock_device_server.fail_check()

        print(value_obj)

        assert value_name == value_obj.name == value.name
        assert value_obj.uuid == value.uuid
        assert encoding == value_obj.extra_info.get('blob', {}).get("encoding") == value.element.blob.encoding
        assert description == value_obj.extra_info.get("description") == value.element.description
        assert str(period) == value_obj.extra_info.get("period") == value.element.period
        assert vtype == value_obj.extra_info.get("type") == value.element.type
        assert vmax == value_obj.extra_info.get('blob', {}).get("max") == value.element.blob.max

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

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
        "fast_send",
        [True, False]
    )
    @pytest.mark.parametrize(
        "value_name",
        [
            "the_value",
            "lkjskhbdf"
        ]
    )
    @pytest.mark.parametrize(
        "vtype,xsd,namespace,description,period",
        [
            ["Test_Xml", "<test></test>", "First", "TestingDescription.", 74],
        ]
    )
    def test_createXmlValue(
        self,
        mock_device_server,
        fast_send: bool,
        value_name: str,
        permission: wappstoiot.PermissionType,
        vtype: str,
        xsd: str,
        namespace: str,
        description: str,
        period: int,  # in Sec  # UNSURE: How to test this in a short time period?
    ):
        # TODO: Test Illegal Names!
        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name="the_device")
            value = device.createXmlValue(
                name=value_name,
                permission=permission,
                type=vtype,
                xsd=xsd,
                namespace=namespace,
                description=description,
                period=period
            )

        finally:
            wappstoiot.close()

        value_obj = mock_device_server.get_obj(name=value_name)

        mock_device_server.fail_check()

        print(value_obj)

        assert value_name == value_obj.name == value.name
        assert value_obj.uuid == value.uuid
        assert xsd == value_obj.extra_info.get('xml', {}).get("xsd") == value.element.xml.xsd
        assert description == value_obj.extra_info.get("description") == value.element.description
        assert str(period) == value_obj.extra_info.get("period") == value.element.period
        assert vtype == value_obj.extra_info.get("type") == value.element.type
        assert namespace == value_obj.extra_info.get('xml', {}).get("namespace") == value.element.xml.namespace

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
            value_deleted = False

            @value.onDelete
            def value_delete(obj):
                nonlocal value_deleted
                value_deleted = True
            mock_value_rw_nr_server.send_delete(
                obj_uuid=value_obj.uuid,
                obj_type="value"
            )
            server_utils.wait_until_or(lambda: value_deleted, 1)
        finally:
            wappstoiot.close()

        mock_value_rw_nr_server.fail_check()
        assert value_deleted, "Didn't receive a Delete"

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

    @pytest.mark.parametrize(
        "fast_send",
        [
            True,
            False
        ]
    )
    @pytest.mark.parametrize(
        "new_permission",
        [
            wappstoiot.PermissionType.READWRITE,
            wappstoiot.PermissionType.READ,
            wappstoiot.PermissionType.WRITE,
            wappstoiot.PermissionType.NONE,
        ]
    )
    @pytest.mark.parametrize(
        "old_permission",
        [
            wappstoiot.PermissionType.READWRITE,
            wappstoiot.PermissionType.READ,
            wappstoiot.PermissionType.WRITE,
            wappstoiot.PermissionType.NONE,
        ]
    )
    def test_permission_change(
        self,
        mock_device_server,
        new_permission: wappstoiot.PermissionType,
        old_permission: wappstoiot.PermissionType,
        fast_send: bool,
    ):
        device_obj = mock_device_server.get_obj(name="the_device")

        value_uuid = uuid.uuid4()
        value_name = "the_value"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=wappstoiot.ValueTemplate.NUMBER,
            permission=old_permission
        )

        mock_device_server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_obj.uuid,
            extra_info=extra_info
        )

        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name=device_obj.name)
            device.createValue(
                name=value_name,
                permission=new_permission,
                value_template=wappstoiot.ValueTemplate.NUMBER
            )

        finally:
            wappstoiot.close()

        mock_device_server.fail_check()

        expected_pkg = 5  # No change & None Permission

        if new_permission == wappstoiot.PermissionType.READWRITE:
            # Get both values of the states or post them.
            expected_pkg += 2
        if new_permission in [wappstoiot.PermissionType.READ, wappstoiot.PermissionType.WRITE]:
            # Get the value of the state or post it.
            expected_pkg += 1
        if new_permission != old_permission:
            # Post the Value change.
            expected_pkg += 1

        assert len(mock_device_server.data_in) == expected_pkg

        # TODO: Check permission on remote & local

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
    @pytest.mark.parametrize(
        "new_template",
        [
            wappstoiot.ValueTemplate.NUMBER,
            wappstoiot.ValueTemplate.STRING,
            wappstoiot.ValueTemplate.BLOB,
            wappstoiot.ValueTemplate.XML,
        ]
    )
    @pytest.mark.parametrize(
        "old_template",
        [
            wappstoiot.ValueTemplate.NUMBER,
            wappstoiot.ValueTemplate.STRING,
            wappstoiot.ValueTemplate.BLOB,
            wappstoiot.ValueTemplate.XML,
        ]
    )
    def test_template_change(
        self,
        mock_device_server,
        new_template: wappstoiot.ValueTemplate,
        old_template: wappstoiot.ValueTemplate,
        fast_send: bool,
    ):
        device_obj = mock_device_server.get_obj(name="the_device")

        value_uuid = uuid.uuid4()
        value_name = "the_value"
        extra_info: Dict[str, Any] = server_utils.generate_value_extra_info(
            value_template=old_template,
            permission=wappstoiot.PermissionType.READWRITE
        )

        mock_device_server.add_object(
            this_uuid=value_uuid,
            this_type='value',
            this_name=value_name,
            parent_uuid=device_obj.uuid,
            extra_info=extra_info
        )

        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )
            network = wappstoiot.createNetwork(name=mock_device_server.network_name)
            device = network.createDevice(name=device_obj.name)
            device.createValue(
                name=value_name,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=new_template
            )

        finally:
            wappstoiot.close()

        mock_device_server.fail_check()

        expected_pkg = 5  # No change & None Permission

        expected_pkg += 2  # Permission READ & Write
        if new_template != old_template:
            # Post the Value change.
            expected_pkg += 1

        value_obj = mock_device_server.get_obj(name="the_value")
        server_utils.is_base_type(value_obj, new_template)

        assert len(mock_device_server.data_in) == expected_pkg

        server_utils.fast_send_check(
            pkg_list=mock_device_server.data_in,
            fast_send=fast_send
        )

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
        "timestamp_test",
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
    @pytest.mark.parametrize(
        "data_value",
        [
            0,
            float("nan"),
            "NA",
        ]
    )
    def test_report(  # TODO: Split up into one for number, string blob & xml
        self,
        mock_device_server,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        timestamp_test: bool,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):
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

        timestamp = datetime.datetime.utcnow() if timestamp_test else None

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
        if data_value != data_value:  # Data is float('nan')
            temp_control_value = value.getReportData()
            assert temp_control_value != temp_control_value
        else:
            if data_value == 'NA' and is_number_type:
                data_value = None
            assert value.getReportData() == data_value  # , "'getControlData' did not return expected data."

        if timestamp_test:
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
            wappstoiot.PermissionType.READ,
            # wappstoiot.PermissionType.WRITE,
            # wappstoiot.PermissionType.NONE
        ]
    )
    @pytest.mark.parametrize(
        "timestamp_test",
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
    @pytest.mark.parametrize(
        "value_template,data",
        [
            (
                wappstoiot.ValueTemplate.NUMBER,
                wappstoiot.LogValue(data=3, timestamp=datetime.datetime(2012,8,1,15,19,42))
            ),
            (
                wappstoiot.ValueTemplate.STRING,
                wappstoiot.LogValue(data='test', timestamp=datetime.datetime(2012,8,1,15,19,42))
            ),
        ]
    )
    def test_report_log_Value(
        self,
        mock_device_server,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        timestamp_test: bool,
        fast_send: bool,
        data: Union[wappstoiot.LogValue]
    ):
        is_number_type = wappstoiot.modules.template.valueSettings[value_template].value_type == wappstoiot.modules.template.ValueBaseType.NUMBER

        data_value = float(data.data) if is_number_type else str(data.data)
        timestamp = data.timestamp

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

        assert state.extra_info.get('data') == str(data_value)  # , "The server did not have the expected data."
        if data_value != data_value:  # Data is float('nan')
            temp_control_value = value.getReportData()
            assert temp_control_value != temp_control_value
        else:
            if data_value == 'NA' and is_number_type:
                data_value = None
            assert value.getReportData() == data_value  # , "'getControlData' did not return expected data."

        if timestamp_test:
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
            # (wappstoiot.ValueTemplate.STRING),
            # (wappstoiot.ValueTemplate.BLOB),
            # (wappstoiot.ValueTemplate.XML),
        ]
    )
    @pytest.mark.parametrize(
        "timestamp_test",
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
    @pytest.mark.parametrize(
        "data",
        [
            [
                wappstoiot.LogValue(data=2, timestamp=datetime.datetime(2012,8,1,15,19,41)),
                wappstoiot.LogValue(data=3, timestamp=datetime.datetime(2012,8,1,15,19,42)),
                wappstoiot.LogValue(data=1, timestamp=datetime.datetime(2012,8,1,15,19,40)),
            ],
        ]
    )
    def test_report_bulk(
        self,
        mock_device_server,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        timestamp_test: bool,
        fast_send: bool,
        data: Union[int, float, str, wappstoiot.LogValue]
    ):
        is_number_type = wappstoiot.modules.template.valueSettings[value_template].value_type == wappstoiot.modules.template.ValueBaseType.NUMBER

        last_data = sorted(data, key=lambda x: x.timestamp)[-1]
        last_data_value = float(last_data.data) if is_number_type else last_data.data
        last_timestamp = last_data.timestamp

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

        try:
            value.report(data)
            print(value.report_state)
        finally:
            wappstoiot.close()

        mock_device_server.fail_check()
        state = server_utils.get_state_obj(
            server=mock_device_server,
            value_uuid=value_uuid,
            state_type="Report"
        )

        # NOTE: Do not work with Bulk, since it only stores the last value.
        # assert state.extra_info.get('data') == str(data_value)  # , "The server did not have the expected data."

        # if data_value != data_value:  # Data is float('nan')
        #     temp_control_value = value.getReportData()
        #     assert temp_control_value != temp_control_value
        # else:
        #     if data_value == 'NA' and is_number_type:
        #         data_value = None
        assert value.getReportData() == last_data_value  # , "'getControlData' did not return expected data."

        # if timestamp_test:
        assert state.extra_info.get('timestamp') == last_timestamp
        assert value.getReportTimestamp() == last_timestamp

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
    def test_on_control(  # TODO: Split up into one for number, string blob & xml
        self,
        mock_device_server,
        permission: wappstoiot.PermissionType,
        value_template: wappstoiot.ValueTemplate,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):
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
            server_utils.wait_until_or(lambda: the_control_value, 1)

        finally:
            wappstoiot.close()

        mock_device_server.fail_check()

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

        assert state.extra_info.get('timestamp') == timestamp
        assert value.getControlTimestamp() == timestamp

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
    @pytest.mark.parametrize(
        "data_value",
        [
            "Testing",
        ]
    )
    def test_on_control_cancel(
        self,
        mock_value_string_server,
        fast_send: bool,
        data_value: Union[int, float, str]
    ):

        device_obj = mock_value_string_server.get_obj(name="the_device")
        value_obj = mock_value_string_server.get_obj(name="the_value")

        the_control_value = None
        timestamp = datetime.datetime.utcnow()

        not_control_value = "DataNotForTheCallback!"
        not_control_timestamp = datetime.datetime.utcnow()

        try:
            wappstoiot.config(
                config_folder=self.temp,
                fast_send=fast_send
            )

            network = wappstoiot.createNetwork(name=mock_value_string_server.network_name)

            device = network.createDevice(name=device_obj.name)

            value = device.createValue(
                name=value_obj.name,
                permission=wappstoiot.PermissionType.READWRITE,
                value_template=wappstoiot.ValueTemplate.STRING
            )

            @value.onControl
            def control_test(obj, value):
                nonlocal the_control_value
                the_control_value = value
                print(f"OnControl: {value}")

            state = server_utils.get_state_obj(
                server=mock_value_string_server,
                value_uuid=value_obj.uuid,
                state_type="Control"
            )

            mock_value_string_server.send_control(
                obj_uuid=state.uuid,
                data=data_value,
                timestamp=timestamp,
            )

            server_utils.wait_until_or(
                lambda: value.getControlData() == data_value,
                1
            )

            value.cancelOnControl()

            mock_value_string_server.send_control(
                obj_uuid=state.uuid,
                data=not_control_value,
                timestamp=not_control_timestamp,
            )

            server_utils.wait_until_or(
                lambda: state.extra_info.get('data') == str(not_control_value),
                1
            )

        finally:
            wappstoiot.close()

        mock_value_string_server.fail_check()

        # assert state.extra_info.get('data') == str(not_control_value)  # , "The server did not have the expected data."

        assert the_control_value == data_value  # , "Did not receive the expected data."
        assert state.extra_info.get('data') == str(data_value)  # , "The server did not have the expected data."
        assert value.getControlData() == not_control_value  # , "'getControlData' did not return expected data."

        # assert state.extra_info.get('timestamp') == not_control_timestamp
        assert value.getControlTimestamp() == not_control_timestamp

        server_utils.fast_send_check(
            pkg_list=mock_value_string_server.data_in,
            fast_send=fast_send
        )

    # def test_receive_report_value(self):
    #     pass

    # def test_send_control_value(self):
    #     pass

    # def test_examples(self, mock_rw_socket, mock_ssl_socket):
    #     # TODO:!!!!!!!!
    #     pass

    # def test_replays_w_errors(self,):
    #     pass

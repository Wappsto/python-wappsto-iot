import json
import time
import uuid

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import wappstoiot

from utils.wappstoserver import ObjectModel
from utils.wappstoserver import SimuServer


def wait_until_or(check: Callable[[], bool], max_wait: int):
    start = time.time() + max_wait
    while not check():
        if start <= time.time():
            break
        time.sleep(0.05)
    time.sleep(0.05)  # NOTE: To ensure the reply to reach the server.


def generate_value_extra_info(
    value_template: wappstoiot.ValueTemplate,
    permission: wappstoiot.PermissionType
) -> Dict[str, Any]:
    value_settings = wappstoiot.modules.template.valueSettings[value_template]

    extra_info: Dict[str, Any] = {
        'type': value_settings.type,
        'permission': permission
    }
    # TODO: Should just be MVP.
    if value_settings.value_type == wappstoiot.modules.template.ValueBaseType.NUMBER:
        extra_info['number'] = {
            'min': value_settings.min,
            'max': value_settings.max,
            'step': value_settings.step,
        }

        if value_settings.mapping:
            extra_info['number']['mapping'] = value_settings.mapping,
        if value_settings.meaningful_zero:
            extra_info['number']['meaningful_zero'] = value_settings.meaningful_zero,
        if value_settings.ordered_mapping:
            extra_info['number']['ordered_mapping'] = value_settings.ordered_mapping,
        if value_settings.si_conversion:
            extra_info['number']['si_conversion'] = value_settings.si_conversion,
        if value_settings.unit:
            extra_info['number']['unit'] = value_settings.unit,

    elif value_settings.value_type == wappstoiot.modules.template.ValueBaseType.STRING:
        extra_info['string'] = {
            "max": value_settings.max,
            "encoding": value_settings.encoding
        }
    elif value_settings.value_type == wappstoiot.modules.template.ValueBaseType.BLOB:
        extra_info['blob'] = {
            "max": value_settings.max,
            "encoding": value_settings.encoding
        }
    elif value_settings.value_type == wappstoiot.modules.template.ValueBaseType.XML:
        extra_info['xml'] = {
            "xsd": value_settings.xsd,
            "namespace": value_settings.namespace
        }

    return extra_info


def get_state_obj(
    server: SimuServer,
    value_uuid: uuid.UUID,
    state_type: str
) -> Optional[ObjectModel]:
    value_obj = server.objects[value_uuid]
    for state_uuid in value_obj.children:
        state = server.objects[state_uuid]
        if state.extra_info.get('type', "").lower() == state_type.lower():
            return state
    return None


def fast_send_check(pkg_list: List[Union[bytes, str, dict]], fast_send: bool):
    for x in pkg_list:
        print(x)
        if not isinstance(x, dict):
            pkg = json.loads(x)
        else:
            pkg = x
        if not isinstance(pkg, list):
            pkg = [pkg]
        for x_pkg in pkg:
            if x_pkg.get('result'):
                continue
            if x_pkg.get('method') == 'GET':
                assert x_pkg.get('params', {}).get('meta', {}).get('fast', False) is False
                continue
            assert x_pkg.get('params', {}).get('meta', {}).get('fast', False) is fast_send


def base_type_number_check(
    value: ObjectModel,
    target: wappstoiot.modules.template.ValueSettinsSchema
):
    assert 'number' in value.extra_info.keys(), "Not a number type"
    assert value.extra_info.get('type') == target.type, "Type Have not been changed"
    assert value.extra_info.get('number', {}).get('min') == target.min
    assert value.extra_info.get('number', {}).get('max') == target.max
    assert value.extra_info.get('number', {}).get('step') == target.step
    assert value.extra_info.get('number', {}).get('unit') == target.unit
    assert value.extra_info.get('number', {}).get('si_conversion') == target.si_conversion
    assert value.extra_info.get('number', {}).get('meaningful_zero') == target.meaningful_zero
    assert value.extra_info.get('number', {}).get('ordered_mapping') == target.ordered_mapping
    if target.mapping:
        assert value.extra_info.get('number', {}).get('mapping', {}).items() == target.mapping.items()


def base_type_string_check(
    value: ObjectModel,
    target: wappstoiot.modules.template.ValueSettinsSchema
):
    assert 'string' in value.extra_info.keys(), "Not a string type"
    assert value.extra_info.get('type') == target.type, "Type Have not been changed"
    assert value.extra_info.get('string', {}).get('max') == target.max
    assert value.extra_info.get('string', {}).get('encoding') == target.encoding


def base_type_blob_check(
    value: ObjectModel,
    target: wappstoiot.modules.template.ValueSettinsSchema
):
    assert 'blob' in value.extra_info.keys(), "Not a blob type"
    assert value.extra_info.get('type') == target.type, "Type Have not been changed"
    assert value.extra_info.get('blob', {}).get('max') == target.max
    assert value.extra_info.get('blob', {}).get('encoding') == target.encoding


def base_type_xml_check(
    value: ObjectModel,
    target: wappstoiot.modules.template.ValueSettinsSchema
):
    assert 'xml' in value.extra_info.keys(), "Not a XML type"
    assert value.extra_info.get('type') == target.type, "Type Have not been changed"
    assert value.extra_info.get('xml', {}).get('xsd') == target.xsd
    assert value.extra_info.get('xml', {}).get('namespace') == target.namespace


def is_base_type(
    value: ObjectModel,
    target: wappstoiot.ValueTemplate
):
    print(f"Value: {value}")
    value_type = wappstoiot.modules.template.valueSettings[target]
    print(f"Target: {value_type}")
    if value_type.value_type == wappstoiot.modules.template.ValueBaseType.NUMBER:
        base_type_number_check(value, value_type)

    elif value_type.value_type == wappstoiot.modules.template.ValueBaseType.STRING:
        base_type_string_check(value, value_type)

    elif value_type.value_type == wappstoiot.modules.template.ValueBaseType.BLOB:
        base_type_blob_check(value, value_type)

    elif value_type.value_type == wappstoiot.modules.template.ValueBaseType.XML:
        base_type_xml_check(value, value_type)

import json
import uuid

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import wappstoiot

from utils.wappstoserver import ObjectModel
from utils.wappstoserver import SimuServer


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

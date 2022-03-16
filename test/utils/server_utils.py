import uuid

from typing import Any
from typing import Dict
from typing import Optional

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
            'mapping': value_settings.mapping,
            'meaningful_zero': value_settings.meaningful_zero,
            'ordered_mapping': value_settings.ordered_mapping,
            'si_conversion': value_settings.si_conversion,
            'unit': value_settings.unit,
        }
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

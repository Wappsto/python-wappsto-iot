from typing import Any
from typing import Dict

import wappstoiot


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

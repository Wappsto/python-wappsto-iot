import datetime
import uuid

from typing import Dict
from typing import List
from typing import Optional
from typing import Union


def convert_timestamp(timestamp: Optional[datetime.datetime] = None) -> str:
    """
    Return The default timestamp used for Wappsto.

    The timestamp are always set to the UTC timezone.

    Returns:
        The UTC time string in ISO format.
    """
    # TODO: Move to package_smithing.py
    if not timestamp:
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def error_pkg(
    pkg_id: str,
    msg: str,
    code: int,
    data: dict,
    traceback: Optional[str] = None
) -> dict:
    return {
        'jsonrpc': '2.0',
        'id': pkg_id,
        'error': {
            'code': code,
            'message': msg,
            'data': {
                'meta': {
                    'type': 'httpresponse',
                    'version': '2.0'
                },
                'message': 'Something Not good!',
                'data': data,
                'debug': {
                    'backtrace':
                        traceback.split('\n') if traceback else []
                }
            }
        }
    }


def success_pkg(
    pkg_id: str,
    timestamp: Optional[datetime.datetime] = None,
) -> dict:
    return rpc_pkg(
        pkg_id=pkg_id,
        pkg_data=True,
        timestamp=timestamp
    )


def rpc_pkg(
    pkg_id: str,
    pkg_data: Union[dict, bool],
    timestamp: Optional[datetime.datetime] = None,
) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": pkg_id,
        "result": {
            "value": pkg_data,
            "meta": {
                "server_send_time": convert_timestamp(timestamp)
            }
        }
    }


def idlist_pkg(
    obj_type: str,
    obj_list: Optional[List[uuid.UUID]] = None,
    timestamp: Optional[datetime.datetime] = None,
) -> dict:
    obj_str_list: List[str] = []
    if obj_list:
        obj_str_list = [str(x) for x in obj_list]

    the_idlist = {
        "child": [{"type": obj_type, "version": "2.0"}] if obj_str_list else [],
        "id": obj_str_list,
        "more": False,
        "limit": 1000,
        "count": len(obj_str_list),
        "meta": {
            "type": "idlist",
            "version": "2.0"
        }
    }
    return the_idlist


def network_pkg(
    obj_uuid: uuid.UUID,
    obj_children: Optional[List[uuid.UUID]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    # **kwargs
) -> dict:
    device_str_list: List[str] = []
    if obj_children:
        device_str_list = [str(x) for x in obj_children]

    return {
        "device": device_str_list,
        "name": name if name else "",
        "description": description if description else "",
        "meta": {
            "id": str(obj_uuid),
            "type": "network",
            "version": "2.0"
        }
    }


def device_pkg(
    obj_uuid: uuid.UUID,
    obj_children: Optional[List[uuid.UUID]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    manufacturer: Optional[str] = None,
    product: Optional[str] = None,
    version: Optional[str] = None,
    serial: Optional[str] = None,
    protocol: Optional[str] = None,
    communication: Optional[str] = None,
    # **kwargs
) -> dict:
    value_str_list: List[str] = []
    if obj_children:
        value_str_list = [str(x) for x in obj_children]

    return {
        "name": name if name else "",
        "description": description if description else "",
        "manufacturer": manufacturer if manufacturer else "",
        "product": product if product else "",
        "version": version if version else "",
        "serial": serial if serial else "",
        "protocol": protocol if protocol else "",
        "communication": communication if communication else "",
        "value": value_str_list,
        "meta": {
            "id": str(obj_uuid),
            "version": "2.0",
            "type": "device"
        }
    }


def value_pkg(
    obj_uuid: uuid.UUID,
    permission: str = None,
    obj_children: Optional[List[uuid.UUID]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    period: Optional[str] = None,
    delta: Optional[str] = None,
    type: Optional[str] = None,
    number: Optional[dict] = None,
    string: Optional[dict] = None,
    blob: Optional[dict] = None,
    xml: Optional[dict] = None,
) -> Dict[str, Union[str, bool, int, float, None, dict, list]]:
    state_str_list: List[str] = []
    if obj_children:
        state_str_list = [str(x) for x in obj_children]

    the_value_pkg: Dict[str, Union[str, bool, int, float, None, dict, list]] = {
        "state": state_str_list,
        "name": name if name else "",
        "permission": permission,
        "type": type,
        "meta": {
            "id": str(obj_uuid),
            "type": "value",
            "version": "2.0"
        }
    }
    # TODO: FIXME!!!! Uses sub dictionaries! for stuff!!!!!
    if period:
        the_value_pkg['period'] = period
    if delta:
        the_value_pkg['delta'] = delta
    if description:
        the_value_pkg['description'] = description

    if string:
        the_value_pkg['string'] = string
    elif number:
        the_value_pkg['number'] = number
    elif blob:
        the_value_pkg['blob'] = blob
    elif xml:
        the_value_pkg['xml'] = xml

    return the_value_pkg


def state_pkg(
    obj_uuid: uuid.UUID,
    type: str,
    data: Optional[str],
    timestamp: Optional[datetime.datetime] = None,
) -> dict:
    if type not in ['Report', 'Control']:
        raise ValueError(f"Type must be: 'Report' or 'Control' not: {type}")
    return {
        "type": type,
        "data": data if data else "NA",
        "timestamp": convert_timestamp(timestamp),
        "meta": {
            "id": str(obj_uuid),
            "type": "state",
            "version": "2.0"
        }
    }

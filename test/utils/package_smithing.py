import datetime

from typing import Optional

pkg_success = '{{"jsonrpc":"2.0","id":"{id}","result":{{"value":true,"meta":{{"server_send_time":"{timestamp}"}}}}}}'


def get_success_pkg(id: str, timestamp: Optional[datetime.datetime] = None) -> bytes:
    if not timestamp:
        timestamp = datetime.datetime.utcnow()
    return pkg_success.format(
        id=id,
        timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    ).encode()

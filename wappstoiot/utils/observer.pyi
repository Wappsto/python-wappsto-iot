from _typeshed import Incomplete
from typing import Any, Callable, Dict, List

obs_log: Incomplete
default_subscriber: Incomplete
subscriber: Dict[str, List[Callable[[str, Any], None]]]

def subscribe(event_name: str, callback: Callable[[str, Any], None]) -> None: ...
def post(event_name: str, data: Any) -> None: ...
def unsubscribe(event_name: str, callback: Callable[[str, Any], None]) -> bool: ...

import logging

from typing import Any
from typing import Dict
from typing import List
from typing import Callable


obs_log = logging.getLogger(__name__)
obs_log.addHandler(logging.NullHandler())

default_subscriber = [
    lambda event_name, data: obs_log.info(
        f"Default Observer: {event_name=}, {data=}"
    )
]

subscriber: Dict[str, List[Callable[[str, Any], None]]] = {}


def subscribe(event_name: str, fn: Callable[[str, Any], None]) -> None:
    """
    Subscribe to the event with given event name.

    Note: If lambda was used to subscribe with, it need to be the same
    instance that is used to unsubscribe with. So if it is needed to
    unsubscibe, save the instance.

    Args:
        event_name: The Unique name for the wanted event.
        fn: The function that need triggeret on the given event.
            The function will be called with the 'event_name', and 'data', 
            that the event generate.
    """
    obs_log.debug(f"New Subscriber: {event_name=}, {fn=}")
    subscriber.setdefault(event_name, default_subscriber).append(fn)


def post(event_name: str, data: Any) -> None:
    """
    Post the event with given event name.

    Args:
        event_name: An unique name for the given event.
        data: The given event subscriber might want.
    """
    obs_log.debug(f"New event was posted: {event_name=}, {data=}")
    for fn in subscriber.get(event_name, default_subscriber):
        fn(event_name, data)


def unsubscribe(event_name: str, fn: Callable[[str, Any], None]) -> bool:
    """
    Unsubscribe from given event name.

    Note: if lambda was used to subscribe with, it need to be the same
    instance that is used to unsubscribe with.

    Args:
        event_name: The Unique name for the wanted event.
        fn: The function that need triggeret on the given event.
            The function will be called with the 'event_name', and 'data', 
            that the event generate.

    Returns:
        True, is the function was removed from the subcriber list.
        False, if it could not be, as in could not find it.
    """
    obs_log.debug(f"Unsubscribing: {event_name=}, {fn=}")

    try:
        # NOTE: Faster then testing if fn is in the list, when it is (60%+).
        subscriber.get(event_name, []).remove(fn)
    except ValueError:
        return False
    else:
        return True

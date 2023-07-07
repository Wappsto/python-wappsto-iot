"""
Contain the Observer functionality.

The Observer Pattern, is as design pattern, that
"""
import logging
import threading

from typing import Any
from typing import Dict
from typing import List
from typing import Callable


obs_log = logging.getLogger(__name__)
obs_log.addHandler(logging.NullHandler())

default_subscriber = [
    lambda event_name, data: obs_log.debug(
        f"Default Observer: event_name={event_name}, data={data}"
    )
]

subscriber: Dict[str, List[Callable[[str, Any], None]]] = {}


def subscribe(event_name: str, callback: Callable[[str, Any], None]) -> None:
    """
    Subscribe to the event with given event name.

    Note: If lambda was used to subscribe with, it need to be the same
    instance that is used to unsubscribe with. So if it is needed to
    unsubscribe, save the instance.

    Args:
        event_name: The Unique name for the wanted event.
        callback: The function that need triggered on the given event.
            The function will be called with the 'event_name', and 'data',
            that the event generate.
    """
    obs_log.debug(f"New Subscriber: {event_name}, {callback}")
    if event_name not in subscriber:
        subscriber[event_name] = default_subscriber.copy()
    subscriber[event_name].append(callback)


def post(event_name: str, data: Any) -> None:
    """
    Post the event with given event name.

    Args:
        event_name: An unique name for the given event.
        data: The given event subscriber might want.
    """
    def executer() -> None:
        for fn in subscriber.get(event_name, default_subscriber):
            fn(event_name, data)

    # NOTE: Needed for ensure that the receive thread do not get blocked.
    th = threading.Thread(target=executer)
    th.start()


def unsubscribe(event_name: str, callback: Callable[[str, Any], None]) -> bool:
    """
    Unsubscribe from given event name.

    Note: if lambda was used to subscribe with, it need to be the same
    instance that is used to unsubscribe with.

    Args:
        event_name: The Unique name for the wanted event.
        callback: The function that need triggered on the given event.
            The function will be called with the 'event_name', and 'data',
            that the event generate.

    Returns:
        True, is the function was removed from the subscriber list.
        False, if it could not be, as in could not find it.
    """
    obs_log.debug(f"Unsubscribing: {event_name}, {callback}")

    try:
        # NOTE: Faster then testing if callback is in the list, when it is (60%+).
        subscriber.get(event_name, []).remove(callback)
    except ValueError:
        return False
    else:
        return True

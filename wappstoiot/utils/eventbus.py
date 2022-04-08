import logging
import threading

from dataclasses import dataclass

from typing import Any
from typing import Dict
from typing import List
from typing import Callable


@dataclass
class Subscriber:
    event: str
    subscriber_name: str
    callback: Callable[[str, Any], None]


class EventBusTemplate:
    def __init__(self):
        pass

    def subscribe(
        self,
        event: str,
        subscriber_name: str,
        callback: Callable[[str, Any], None]
    ) -> None:
        pass

    def subscribers(self) -> List[str]:
        pass

    def post(self, event: str, data: Any) -> None:
        pass

    def unsubscribe(
        self,
        subscriber_name: str,
        event: str
    ):
        pass

    def unsubscribe_all(self, subscriber_name) -> None:
        pass

    def close(self):
        pass


class EventBus(EventBusTemplate):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.subscriber_list: Dict[str, List[Subscriber]] = {}
        self.event_list: Dict[str, List[Subscriber]] = {}

        self.default_subscriber = [
            Subscriber(
                event="",
                subscriber_name="Default",
                callback=lambda event_name, data: self.log.debug(
                    f"Default Observer: event_name={event_name}, data={data}"
                )
            )
            
        ]

    def _add(self, subscriber: Subscriber) -> None:
        # if subscriber.subscriber_name not in self.subscriber_list:
        #     self.subscriber_list[subscriber.subscriber_name] = []    
        self.subscriber_list.setdefault(subscriber.subscriber_name, []).append(
            subscriber
        )
        # if subscriber.event not in self.event_list:
        #     self.subscriber_list[subscriber.event] = []
        self.event_list.setdefault(subscriber.event, []).append(
            subscriber
        )

    def subscribe(
        self,
        event: str,
        subscriber_name: str,
        callback: Callable[[str, Any], None]
    ) -> None:
        """
        Subscribe to the event with given event name.

        Note: If lambda was used to subscribe with, it need to be the same
        instance that is used to unsubscribe with. So if it is needed to
        unsubscibe, save the instance.

        Args:
            event: The Unique name for the wanted event.
            callback: The function that need triggeret on the given event.
                The function will be called with the 'event', and 'data',
                that the event generate.
        """
        self.log.debug(f"New Subscriber: {subscriber_name} on event: {event}")
        self._add(
            Subscriber(
                event=event,
                subscriber_name=subscriber_name,
                callback=callback
            )
        )

    def subscribers(self) -> List[str]:
        return List(self.subscriber_list.keys())

    def post(self, event: str, data: Any) -> None:
        """
        Post the event with given event name.

        Args:
            event: An unique name for the given event.
            data: The given event subscriber might want.
        """
        def executer():
            for sub in self.event_list.get(event, self.default_subscriber):
                sub.callback(event, data)

        # UNSURE: Should use Threadpool?
        # NOTE: Needed for ensure that the receive thread do not get blocked.
        th = threading.Thread(target=executer)
        th.start()

    def unsubscribe(
        self,
        subscriber_name: str,
        event: str
    ):
        """
        Unsubscribe from given event name.

        Note: if lambda was used to subscribe with, it need to be the same
        instance that is used to unsubscribe with.

        Args:
            event: The Unique name for the wanted event.
            callback: The function that need triggeret on the given event.
                The function will be called with the 'event', and 'data',
                that the event generate.

        Returns:
            True, is the function was removed from the subcriber list.
            False, if it could not be, as in could not find it.
        """
        self.log.debug(f"{subscriber_name} is unsubscribing from: {event}")

        # self._remove(subscriber_name, )

        subscribers = filter(lambda x: x.event == event, self.subscriber_list.get(subscriber_name, []))
        for sub in subscribers:
            self.subscriber_list[subscriber_name].remove(sub)
            self.event_list[event].remove(sub)
        if not self.event_list[event]:
            del self.event_list[event]

    def unsubscribe_all(self, subscriber_name) -> None:
        """
        Unsubscribe all from the subscribtions.

        Returns:
            True, is the function was removed from the subcriber list.
            False, if it could not be, as in could not find it.
        """
        self.log.debug(f"{subscriber_name} unsubscribing from all events.")
        subscribers = self.subscriber_list.pop(subscriber_name, [])
        for sub in subscribers:
            self.event_list[sub.event].remove(sub)
            if not self.event_list[sub.event]:
                del self.event_list[sub.event]

    def close(self):
        self.log.debug("Closing.")
        self.subscriber_list.clear()
        self.event_list.clear()

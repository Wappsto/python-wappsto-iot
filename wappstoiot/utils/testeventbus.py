import threading
import time

import rich

from .eventbus import EventBus


class TestEventBus:
    @classmethod
    def setup_class(cls):
        cls.bus = EventBus()
        cls.subs = ['Tom', 'John', 'Boris', 'Jerry']
        cls.events = ['Start', 'Add', 'Update', 'Remove', 'Stop']

    @classmethod
    def teardown_class(cls):
        del cls.bus

    def test_multiple_subscriber(self):
        event = "Testing"
        subs = [
            {'name': x, 'triggered': threading.Event()} for x in self.subs
        ]

        for sub in subs:
            def cb_gen(temp):
                def cb(event, data):
                    temp['triggered'].set()
                return cb
            self.bus.subscribe(
                event=event,
                subscriber_name=sub.get('name'),
                callback=cb_gen(sub)
            )

        self.bus.post(event, "Data")

        for sub in subs:
            assert sub['triggered'].is_set()

    def test_single_trigger(self):
        event = self.events[0]
        subs = [
            {'name': x, 'triggered': threading.Event(), "event": y}
            for x, y in zip(self.subs, self.events)
        ]

        for sub in subs:
            def cb_gen(temp):
                def cb(event, data):
                    temp['triggered'].set()
                return cb
            self.bus.subscribe(
                event=sub['event'],
                subscriber_name=sub.get('name'),
                callback=cb_gen(sub)
            )

        self.bus.post(event, "Data")

        for sub in subs:
            rich.print(sub['name'])
            assert sub['triggered'].is_set()

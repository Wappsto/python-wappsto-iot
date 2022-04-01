"""
"""
import logging
import threading
import pathlib

from typing import Any

from .plugin_template import PlugInTemplate
from .plugin_template import ServiceTemplate
from ..utils import observer


class PingPong(PlugInTemplate):
    def __init__(
        self,
        config_location: pathlib.Path,
        service: ServiceTemplate.ServiceClass,
        observer: observer,
        period_s: int,
        **kwargs: Any
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.period_s = period_s
        self.service = service
        self.killed = threading.Event()

        self.start()

    def start(self):
        self.thread = threading.Timer(self.period_s, self.send_ping)
        self.thread.daemon = True
        self.thread.start()

    def send_ping(self):
        self.log.debug("Ping-Pong called!")
        self.thread
        if self.killed.is_set():
            return
        try:
            self.thread = threading.Timer(self.period_s, self.send_ping)
            self.thread.start()
            self.service.ping()
        except Exception:
            self.log.exception("Ping-Pong:")

    def close(self):
        self.killed.set()
        self.thread.cancel()

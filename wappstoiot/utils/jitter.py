"""Contain all the jitter related functions."""
import threading
import random

from typing import Any
from typing import Callable

jitter_range_sec: int = 10


def exec_with_jitter(
    obj: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Execute given function between new and the jitter range."""
    jitter_time = random.randrange(
        start=0,
        stop=jitter_range_sec * 10,
        step=1,
    ) / 10
    temp = threading.Timer(jitter_time, obj, args=args, kwargs=kwargs)
    temp.start()

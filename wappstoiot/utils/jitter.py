"""Contain all the jitter related functions."""
import threading
import random


jitter_range_sec: int = 10


def exec_with_jitter(obj, *args, **kwargs):
    """Execute given function between new and the jitter range."""
    jitter_time = random.randrange(start=0, stop=jitter_range_sec, step=0.1)
    temp = threading.Timer(jitter_time, obj, args=args, kwargs=kwargs)
    temp.start()

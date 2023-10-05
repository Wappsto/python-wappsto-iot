"""Contain the Period class."""
import datetime
import threading
import time

from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Tuple


class PeriodClass(ABC):
    period: datetime.timedelta
    call_function: Callable[[], None]

    @abstractmethod
    def __init__(self, period: datetime.timedelta): ...

    @abstractmethod
    def time_to_next_period(self) -> float: ...

    @abstractmethod
    def start(
        self,
        function: Callable[..., Any],
        args: Optional[Tuple[Any]]=None,
        kwargs: Optional[Dict[str, Any]]=None,
    ): ...

    @abstractmethod
    def close(self): ...


class Period(PeriodClass):
    period: datetime.timedelta
    call_function: Callable[[], None]
    current_timer: threading.Timer

    def __init__(
        self,
        period: datetime.timedelta,
        function: Callable[..., Any],
        args: Optional[Tuple[Any]]=None,
        kwargs: Optional[Dict[str, Any]]=None,
    ):
        """Initialize the period."""
        self.period = period

        f_args: tuple = args if args is not None else tuple()
        f_kwargs: tuple = kwargs if kwargs is not None else {}
        self.call_function = lambda: function(*f_args, **f_kwargs)

    def __unix_day_start(self) -> float:
        return datetime.datetime.utcnow().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=datetime.UTC,
        ).timestamp()

    def time_to_next_period(self) -> float:
        """Return the seconds to next time period are triggered."""
        # NOTE: datetime do not support leap seconds so unix time is just as good.
        return (- time.time()) % self.period.seconds  # next_period

    def start(self):
        """Start the period logic."""

        def repeat_logic():
            self.call_function()
            self.current_timer = threading.Timer(
                interval=self.time_to_next_period(),
                function=repeat_logic
            )
            self.current_timer.start()

        self.current_timer = threading.Timer(
            interval=self.time_to_next_period(),
            function=repeat_logic
        )
        self.current_timer.start()

    def close(self):
        """Stop the period logic."""
        self.current_timer.cancel()

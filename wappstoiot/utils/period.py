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
    """
    The Abstract base class for Period.

    Period is used to define a minimum report interval.
    """

    period: datetime.timedelta
    call_function: Callable[..., Any]
    call_args: Tuple[Any, ...]
    call_kwargs: Dict[str, Any]

    @abstractmethod
    def __init__(
        self,
        period: datetime.timedelta,
        function: Callable[..., Any],
        args: Optional[Tuple[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the period."""
        ...

    @abstractmethod
    def time_to_next_period(self) -> float:
        """Return the seconds to next time period are triggered."""
        ...

    @abstractmethod
    def start(self) -> None:
        """Start the period logic."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Stop the period logic."""
        ...


class Period(PeriodClass):
    """
    Used to define a minimum report interval.

    The Period are always relative to UTC 00:00.
    Period is disabled if set to: 0, None or float('inf')
    """
    period: datetime.timedelta
    call_function: Callable[..., Any]
    call_args: Tuple[Any, ...]
    call_kwargs: Dict[str, Any]
    current_timer: threading.Timer

    def __init__(
        self,
        period: datetime.timedelta,
        function: Callable[..., Any],
        args: Optional[Tuple[Any, ...]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the period."""
        self.period = period

        self.call_args: Tuple[Any, ...] = args if not args else tuple()
        self.call_kwargs: Dict[str, Any] = kwargs if not kwargs else {}
        self.call_function = function

    def time_to_next_period(self) -> float:
        """Return the seconds to next time period are triggered."""
        # NOTE: datetime do not support leap seconds so unix time is just as good.
        return (- time.time()) % self.period.seconds  # next_period

    def start(self) -> None:
        """Start the period logic."""

        def repeat_logic() -> None:
            self.call_function(*self.call_args, **self.call_kwargs)
            self.current_timer = threading.Timer(
                interval=self.time_to_next_period(),
                function=repeat_logic
            )
            self.current_timer.start()

        self.current_timer = threading.Timer(
            interval=self.time_to_next_period(),
            function=repeat_logic,
        )
        self.current_timer.start()

    def close(self) -> None:
        """Stop the period logic."""
        self.current_timer.cancel()

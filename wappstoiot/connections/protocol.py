from abc import ABC
from abc import abstractmethod

from threading import Lock
from enum import Enum

from typing import Union
from typing import Any
from typing import Callable
from typing import Optional


class Status(str, Enum):
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    DISCONNECTING = "Disconnecting"
    DISCONNETCED = "Disconnected"


class Connection(ABC):

    send_ready: Lock

    @abstractmethod
    def send(
        self,
        data: Union[str, bytes]
    ) -> bool:
        """
        Send the str/Bytes to the server.

        If given string, it is encoded as 'uft-8' & send.

        Returns:
            True, if the data could be send else
            False.
        """

    @abstractmethod
    def receive(
        self,
        parser: Callable[[bytes], Any],
    ) -> Any:
        """
        Socket receive method.

        Method that handles receiving data from a socket. Capable of handling
        data chunks.

        Args:
            Callable: A parser, that returns the parsed data.
                      On Parsing Error, it should raise a
                      ValueError TypeError or any subClasses of those.
                      (Like 'JSONDecodeError' & 'pydantic.ValidationError' is)
        Returns:
            The Parsers output.

        """
        pass

    @abstractmethod
    def connect(self) -> None:
        """
        Connect to the server.

        Attempts a connection to the server on the provided address and port.

        Returns:
            'True' if the connection was successful else
            'False'
        """
        pass

    @abstractmethod
    def reconnect(
        self,
        retry_limit: Optional[int] = None
    ) -> bool:
        """
        Attempt to reconnect.

        Close the current connection, and then try to reconnect to the server,
        until the given amount of attempts, are above the retry_limit.
        If the retry_limit are not set, it will continue end.

        Args:
            retry_limit: the amount of retries, before it stops.

        Returns:
            'True' if the connection was successful else
            'False'
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the server."""
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Close the connection.

        Closes the socket object connection.
        """
        pass

import enum
import logging

from typing import Union
from typing import Any
from typing import Callable
from typing import Optional


class Status(str, enum.Enum):
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    DISCONNECTING = "Disconnecting"
    DISCONNETCED = "Disconnected"


class Debug:
    """For debuging purposes."""
    def __init__(
        self,
        address: str,
        port: int,
        observer: Callable[[str, str], None]
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.observer_name = "CONNECTION"
        self.observer = observer if observer else lambda st, nd: None
        self.observer(self.observer_name, Status.DISCONNETCED)

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

    def receive(
        self,
        parser: Callable[[bytes], Any]
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

    def connect(self) -> bool:
        """
        Connect to the server.

        Attempts a connection to the server on the provided address and port.

        Returns:
            'True' if the connection was successful else
            'False'
        """
        self.observer(self.observer_name, Status.CONNECTING)

        self.observer(self.observer_name, Status.CONNECTED)
        return True

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
        self.log.info("Reconnection...")
        return True

    def disconnect(self) -> None:
        """Disconnect from the server."""

    def close(self) -> None:
        self.log.info("Closing connection...")
        self.observer(self.observer_name, Status.DISCONNECTING)
        self.observer(self.observer_name, Status.DISCONNETCED)

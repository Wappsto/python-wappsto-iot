import logging
import socket
import threading
import time
import ssl

from pathlib import Path

from typing import Any
from typing import Callable
from typing import Optional
from typing import Union

from .protocol import Status
from .protocol import Connection


class TlsSocket(Connection):
    def __init__(
        self,
        address: str,
        port: int,
        ca: Path,  # ca.crt
        crt: Path,  # client.crt
        key: Path,  # client.key
        observer: Optional[Callable[[str, str], None]] = None,
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.observer_name = "CONNECTION"
        self.observer = observer if observer else lambda st, nd: None
        self.observer.post(Status.DISCONNETCED, None)

        self.send_ready = threading.Lock()

        self.address = address
        self.port = port
        self.socket_timeout = 30_000
        self.RECEIVE_SIZE = 2048

        self.log.debug(f"Address: {self.address}")
        self.log.debug(f"Port: {self.port}")

        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.load_cert_chain(crt, key)
        self.ssl_context.load_verify_locations(ca)

        self._socket_setup()

    def _socket_setup(self) -> None:
        """
        Create socket to communicate with server.

        Creates a socket instance and sets the options for communication.
        Passes the socket to the ssl_wrap method

        Note:
        After 5 idle minutes, start sending keepalives every 1 minutes.
        Drop connection after 2 failed keepalives
        """
        self.raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.raw_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_KEEPALIVE,
            1
        )
        self.raw_socket.settimeout(2)
        if (
            hasattr(socket, "TCP_KEEPIDLE")
            and hasattr(socket, "TCP_KEEPINTVL")
            and hasattr(socket, "TCP_KEEPCNT")
        ):
            self.log.debug(
                "Setting TCP_KEEPIDLE, TCP_KEEPINTVL & TCP_KEEPCNT."
            )
            self.raw_socket.setsockopt(
                socket.SOL_TCP,
                socket.TCP_KEEPIDLE,
                5 * 60
            )
            self.raw_socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_KEEPIDLE,
                5 * 60
            )
            self.raw_socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_KEEPINTVL,
                60
            )
            self.raw_socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_KEEPCNT,
                2
            )

        if hasattr(socket, "TCP_USER_TIMEOUT"):
            self.log.debug(
                f"Setting TCP_USER_TIMEOUT to {self.socket_timeout}ms."
            )
            self.raw_socket.setsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_USER_TIMEOUT,
                self.socket_timeout
            )

        self.socket = self._ssl_wrap()

    def _ssl_wrap(self):
        """
        Wrap socket.

        Wraps the socket using the SSL protocol as configured in the SSL
        context, with hostname verification enabled.

        Returns:
            An SSL wrapped socket.
        """
        return self.ssl_context.wrap_socket(
            self.raw_socket,
            server_hostname=self.address
        )

    def send(
        self,
        data: Union[str, bytes]
    ) -> bool:
        """
        Send the str/Bytes to the server.

        If given string, it is encoded as 'uft-8' & send.

        UNSURE(MBK): Should the encoding be moved outside this class?

        Returns:
            True, if the data could be send else
            False.
        """

        if isinstance(data, str):
            data = data.encode('utf-8')

        try:
            self.socket.sendall(data)
        except ConnectionError:
            msg = "Get an ConnectionError, while trying to send"
            self.log.exception(msg)
            self.reconnect()
            return False
        except TimeoutError:
            msg = "Get an TimeoutError, while trying to send"
            self.log.exception(msg)
            # UNSURE: How do we hit this?
            return False
        else:
            self.log.debug(f"Raw Data Send: {data}")
            return True

    def receive(self, parser: Callable[[bytes], Any]) -> Any:
        """
        Socket receive method.

        Method that handles receiving data from a socket. Capable of handling
        data chunks.

        Args:
            Callable: A parser, that returns the parsed data.
                      On Parsen Error, it should raise a
                      ValueError TypeError or any subClasses of those.
                      (Like 'JSONDecodeError' & 'pydantic.ValidationError' is)
        Returns:
            The "parser"'s output.

        """
        data = []
        while self.socket:
            try:
                data_chunk = self.socket.recv(self.RECEIVE_SIZE)
            except socket.timeout:
                continue
            except OSError:
                # UNSURE:
                self.reconnect()
                continue
            if data_chunk == b'':
                self.log.debug("Server Closed socket.")
                self.reconnect()
            data.append(data_chunk)

            try:
                parsed_data = parser(b"".join(data))
            except ValueError:  # parentClass for JSONDecodeError.
                pass
            except TypeError:  # parentClass for pydantic.ValidationError
                pass
            else:
                self.log.debug(f"Raw Data Received: {data}")
                return parsed_data

    def connect(self) -> None:
        """
        Connect to the server.

        Attempts a connection to the server on the provided addres and port.

        Returns:
            'True' if the connection was successful else
            'False'
        """

        try:
            self.log.info("Trying to Connect.")
            self.observer.post(Status.CONNECTING, None)
            # self.socket.settimeout(10)  # Why?
            self.socket.connect((self.address, self.port))
            # self.socket.settimeout(None)  # Why?
            self.log.info(
                f"Connected on interface: {self.socket.getsockname()[0]}"
            )
            self.observer.post(Status.CONNECTED, None)
            # if self.sockt_thread is None:
            #     self._start()
            # return True

        except Exception as e:
            self.log.error("Failed to connect: {}".format(e))
            raise

    def reconnect(self, retry_limit: Optional[int] = None) -> bool:
        """
        Attempt to reconnect.

        Reconnect to the server, until the given amount af attempts,
        are above the retry_limit.
        if the retry_limit are not set, it will never end.

        Returns:
            'True' if the connection was successful else
            'False'
        """
        if not self.socket:
            return False

        self.log.info("Reconnection...")

        while retry_limit is None or retry_limit > 0:
            if retry_limit:
                retry_limit -= 1
            self.disconnect()
            self._socket_setup()
            if self.connect():
                return True
            self.log.info("Trying to reconnect in 5 seconds")
            time.sleep(5)
        return False

    def disconnect(self) -> None:
        """Disconnect from the server."""
        if self.socket:
            self.socket.close()

    def close(self) -> None:
        """
        Close the connection.

        Closes the socket object connection.
        """
        self.log.info("Closing connection...")
        self.observer.post(Status.DISCONNECTING, None)
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.raw_socket:
            self.raw_socket.close()
            self.raw_socket = None
        self.observer.post(Status.DISCONNETCED, None)
        self.log.info("Connection closed!")

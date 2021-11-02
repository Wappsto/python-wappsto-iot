import logging
import ssl

from pathlib import Path
from typing import Callable
from typing import Optional

from WappstoIoT.connections.rawsocket import RawSocket


class TlsSocket(RawSocket):
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

        super().__init__(address, port, observer)

        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.load_cert_chain(crt, key)
        self.ssl_context.load_verify_locations(ca)
        self.raw_socket = self.socket
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

    def close(self) -> None:
        """
        Close the connection.

        Closes the socket object connection.
        """
        self.log.info("Closing connection...")
        super().close()
        if self.raw_socket:
            self.raw_socket.close()
            self.raw_socket = None

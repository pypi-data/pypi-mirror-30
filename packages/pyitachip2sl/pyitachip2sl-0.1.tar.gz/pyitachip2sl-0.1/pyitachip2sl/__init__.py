import socket
import logging

_LOGGER = logging.getLogger(__name__)


class ITachIP2SLSocketClient(object):
    """
    Python client for the iTach IP2SL Socket server
    """

    _socket_recv = 1024

    def __init__(self, host, port=4999, timeout=1):
        """
        Initialize the socket client.
        """
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((self.host, self.port))

        # Flush any login banner messages
        try:
            self.socket.recv(self._socket_recv)

        except socket.timeout as e:
            return

    def send_data(self, data, raw=False):
        """
        Send data to socket.
        """
        if raw:
            try:
                data = bytes.fromhex(data)

            except ValueError as e:
                _LOGGER.debug("Invalid data received: " + str(e))
                return
        else:
            try:
                data = data.encode('ascii')

            except UnicodeEncodeError as e:
                _LOGGER.debug("Invalid data received: " + str(e))
                return

        _LOGGER.debug("Sending data: " + str(data))
        self.socket.send(data)

        try:
            response = self.socket.recv(self._socket_recv)
            _LOGGER.debug("Received response: " + str(response))
            return response.decode('ascii')

        except UnicodeDecodeError:
            newresponse = str()
            for c in response:
                newresponse += hex(c)
            return newresponse
        
        except socket.timeout as e:
            _LOGGER.debug("Socket timeout. Error: " + str(e))
            return 

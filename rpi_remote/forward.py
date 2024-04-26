import socket
import select


class ClientForwarder:  # pylint: disable=too-few-public-methods

    def __init__(self, host, port, local_port, local_host='127.0.0.1'):
        self._host = host
        self._port = int(port)
        self._local_host = local_host
        self._local_port = int(local_port)

    def _handler(self, source, target):
        while True:
            rlist, _, _ = select.select([source, target], [], [])
            if source in rlist:
                data = source.recv(4096)
                if len(data) == 0:
                    break
                target.sendall(data)
            if target in rlist:
                data = target.recv(4096)
                if len(data) == 0:
                    break
                source.sendall(data)

    @staticmethod
    def _create_socket(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    def start(self):
        try:
            source_sock = self._create_socket(self._local_host, self._local_port)
            target_sock = self._create_socket(self._host, self._port)

            self._handler(source_sock, target_sock)
        finally:
            source_sock.close()
            target_sock.close()

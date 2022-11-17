import socket
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException
import select


class ClientForwarder:

    def __init__(self, host, port, username, passwd, from_port, to_port, logger):
        self.host = host
        self.port = port
        self.username = username
        self.password = passwd
        self.from_port = from_port
        self.to_port = to_port
        self.logger = logger

    def handler(self, chan):
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_socket.connect(("127.0.0.1", self.from_port))
        except Exception as e:
            self.logger.error(e)
            return

        while True:
            r, _, _ = select.select([remote_socket, chan], [], [])
            if remote_socket in r:
                if data := remote_socket.recv(1024):
                    chan.send(data)
                else:
                    break
            if chan in r:
                if chan.closed:
                    break
                if data := chan.recv(1024):
                    remote_socket.send(data)
                else:
                    break
        chan.close()
        remote_socket.close()

    def reverse_port_forward(self, client_transport):
        try:
            client_transport.request_port_forward("", self.to_port)
            client_transport.open_session()
        except paramiko.SSHException as err:
            self.logger.error(err)
            return

        try:
            if chan := client_transport.accept(60):
                self.handler(chan)
        finally:
            client_transport.cancel_port_forward("", self.to_port)
            client_transport.close()

    def start(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.logger.info("Connecting to %s:%d", self.host, self.port)
            client.connect(self.host, port=self.port, username=self.username, password=self.password)
        except NoValidConnectionsError:
            self.logger.info("Unable to connect to: %s:%s", self.host, self.port)
            return
        except AuthenticationException:
            self.logger.info("Authentication failed to: %s:%s", self.host, self.port)
            return
        except Exception as e:
            self.logger.error(e)
            return
        self.reverse_port_forward(client.get_transport())
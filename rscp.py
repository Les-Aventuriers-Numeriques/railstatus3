import socket
import threading
import arrow
import click
import csv


def debug(message, err=False):
    click.echo('{} - {} - {}'.format(
        arrow.now().format('DD/MM/YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
    ), err=err)


class Server:
    """RSCP (RailStatus Command Protocol) server. Once instantiated, you must call :func:`rscp.Server.run` to
    actually run the server.

    :param server_ip: The IP to bind the server to
    :type server_ip: string
    :param server_port: The port the server will listen to
    :type server_port: int
    :param server_max_clients: The maximum number of clients that the server will handle
    :type server_max_clients: int
    """

    _server_ip = None
    _server_port = None
    _server_max_clients = None

    _server_handler = None
    _server_socket = None

    def __init__(self, server_ip, server_port, server_max_clients):
        self._server_ip = server_ip
        self._server_port = server_port
        self._server_max_clients = server_max_clients

    def run(self):
        """Run the RSCP server in a new thread dedicated to handle new incomming client connection. See :func:`rscp.Server.handle_server`
        for more informations about client connection handling.
        """
        self._server_handler = threading.Thread(
            target=self.handle_server,
            args=(self._server_ip, self._server_port, self._server_max_clients)
        )

        self._server_handler.start()

    def handle_server(self, server_ip, server_port, server_max_clients):
        """Responsible of handling any new incomming client connection. For each new incoming connection, a new thread
        is started, dedicated to this connection. The :func:`rscp.Server.handle_client` method is then used to handle
        all things happening with the client and the server (command parsing, etc).
        """
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._server_socket.bind((server_ip, server_port))
            debug('Bind successful')
        except Exception as e:
            debug('Failed to bind to {}:{}: {}'.format(server_ip, server_port, e), err=True)

        self._server_socket.listen(server_max_clients)
        debug('Listening to {}:{} with a clients limit of {}'.format(server_ip, server_port, server_max_clients))
        
        while True:
            client_socket, (client_ip, client_port) = self._server_socket.accept()
            debug('New incomming connection from {}:{}'.format(client_ip, client_port))

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_ip, client_port))
            client_handler.start()

        debug('Closing server socket')
        self._server_socket.close()

    def handle_client(self, client_socket, client_ip, client_port):
        """Responsible of handling any incoming data from a client.
        """
        def send_data_to_client(data):
            data += '\n'
            client_socket.sendall(data.encode('utf8'))

        local = threading.local()
        local.rscp_version = None

        while True:
            message = self.read_one_message(client_socket)

            if not message: # Empty message
                send_data_to_client('BAD_FORMAT')
                continue

            message = self.parse_message(''.join(message))

            if not message or len(message) <= 1:
                send_data_to_client('BAD_FORMAT')
                continue

            command_type = message[0]
            command = message[1]
            parameters = message[2:]

            if not local.rscp_version:
                if command != 'RSCP_SET_VERSION':
                    send_data_to_client('NOT_A_RSCP_CLIENT')
                    break
                elif len(parameters) != 1:
                    send_data_to_client('INVALID_PARAMETERS')
                    break
                else:
                    local.rscp_version = parameters[0]
                    send_data_to_client('ACK')
                    continue

            if command == 'UPDATE_POSITION':
                if len(parameters) != 1:
                    send_data_to_client('INVALID_PARAMETERS_NUMBER')
                    continue

                position = parameters[0]

                with open('positions.txt', 'a') as f:
                    f.write(arrow.now().format('DD/MM/YYYY HH:mm:ss') + ' : ' + position + '\n')

                send_data_to_client('OK')
            else:
                send_data_to_client('UNKNOWN_COMMAND')

        client_socket.close()
        debug('Connection from {}:{} closed'.format(client_ip, client_port))

    def read_one_message(self, client_socket):
        buffer = client_socket.recv(1024)
        buffering = True

        while buffering:
            if '\n' in buffer:
                (line, buffer) = buffer.split('\n', 1)
                yield line + '\n'
            else:
                more = client_socket.recv(1024)

                if not more:
                    buffering = False
                else:
                    buffer += more

        if buffer:
            yield buffer

    def parse_message(self, message_string):
        for row in csv.reader([message_string], dialect=csv.unix_dialect): # Should loop one time
            return row

        return False


class Protocol:
    """RSCP (RailStatus Command Protocol) Python wrapper. Prevent to manually forge and parse RSCP messages.
    """

    def parse_message(self, message):
        """Parse a RSCP message and return its data.

        :param message: The RSCP message to parse.
        :type message: string
        """
        pass

    class Command:
        """RSCP commands. One method represent one command.
        """

        def rscp_set_version(self, version_number):
            """Handshake command. Must be sent prior any other commands. This allow the RSCP server to
            reject any incoming TCP connection that aren’t a RSCP client.

            :param version_number: The RSCP version used (``1`` at this moment of writing)
            :type version_number: int
            """
            pass


    class Response:
        """RSCP responses.. One method represent one response.
        """

        def ok(self):
            """The command was executed successfuly.
            """
            pass

        def bad_format(self):
            """The previously sent command wasn’t well-formed.
            """
            pass

        def unknown_command(self):
            """Unknown command.
            """
            pass

        def invalid_parameters(self):
            """The number of parameters doesn’t match the ones required by the command.
            """
            pass

        def not_a_rscp_client(self):
            """Handshake failure. See :func:`rscp.Protocol.Command.rscp_set_version`.
            """
            pass

        def ack(self):
            """Handshake success. See :func:`rscp.Protocol.Command.rscp_set_version`.
            """
            pass

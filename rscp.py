from enum import Enum
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

    Example usage:

    .. code-block:: python

        import rscp

        rscp_server = rscp.Server('127.0.0.1', 8888, 10)
        rscp_server.run()

    :param str server_ip: The IP to bind the server to
    :param int server_port: The port the server will listen to
    :param int server_max_clients: The maximum number of clients that the server will handle
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
        """Run the RSCP server in a new thread dedicated to handle new incomming client connection.
        """
        self._server_handler = threading.Thread(
            target=self.handle_server,
            args=(self._server_ip, self._server_port, self._server_max_clients)
        )

        self._server_handler.start()

    def handle_server(self, server_ip, server_port, server_max_clients):
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


class Message:
    """Base class for RSCP (RailStatus Command Protocol) messages (see :class:`rscp.Command` and :class:`rscp.Response`).

    Used to convert text message into Python object and vice-versa.

    Example usage:

    .. code-block:: python

        import rscp.Message

        command = Message.parse('C,RSCP_SET_VERSION,1\\n') # Object
        print(command) # String
    """

    type = None
    name = None
    data = []

    def __init__(self, type, name, *args):
        self.type = type
        self.name = name
        self.data = args

    @staticmethod
    def parse(self, message):
        """Parse a RSCP message and return its object representation.

        :param str message: The RSCP message to parse.
        :return: Either a :class:`rscp.Command` or :class:`rscp.Response` object
        """
        pass

    def __str__(self):
        return '{type},{name}{data}'.format(
            type=self.type,
            name=self.name,
            data=',' + ','.join(self.data) if self.data else None
        )


class Command(Message):
    """RSCP commands. One method represent one command.

    Example usage:

    .. code-block:: python

        import rscp.Command

        print(Command.rscp_set_version(1))
    """

    def __init__(self, name, *args):
        super(Command, self).__init__('C', name, *args)

    @staticmethod
    def rscp_set_version(version_number):
        """Handshake command. Must be sent prior any other commands. This allow the RSCP server to
        reject any incoming TCP connection that aren’t a RSCP client.

        :param int version_number: The RSCP version used (``1`` at this moment of writing)
        :rtype: Command
        """
        return Command('RSCP_SET_VERSION', version_number)


class Response(Message):
    """RSCP responses. One method represent one response.

    Example usage:

    .. code-block:: python

        import rscp.Response

        print(Command.ok('some', 'data'))
    """

    def __init__(self, name, *args):
        super(Response, self).__init__('R', name, *args)

    @staticmethod
    def ok(*args):
        """The command was executed successfuly.

        :rtype: Response
        """
        return Response('OK', *args)

    @staticmethod
    def bad_format():
        """The previously sent command wasn’t well-formed.

        :rtype: Response
        """
        return Response('BAD_FORMAT')

    @staticmethod
    def unknown_command(command_name=None):
        """Unknown command.

        :rtype: Response
        """
        return Response('UNKNOWN_COMMAND', command_name)

    @staticmethod
    def invalid_parameters(command_name=None):
        """The number of parameters doesn’t match the ones required by the command.

        :rtype: Response
        """
        return Response('INVALID_PARAMETERS', command_name)

    @staticmethod
    def not_a_rscp_client():
        """Handshake failure. See :func:`rscp.Command.rscp_set_version`.

        :rtype: Response
        """
        return Response('NOT_A_RSCP_CLIENT')

    @staticmethod
    def ack():
        """Handshake success. See :func:`rscp.Command.rscp_set_version`.

        :rtype: Response
        """
        return Response('ACK')

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
    server_ip = None
    server_port = None
    server_max_clients = None

    server_handler = None
    server_socket = None

    def __init__(self, server_ip, server_port, server_max_clients):
        self.server_ip = server_ip
        self.server_port = server_port
        self.server_max_clients = server_max_clients

    def run(self):
        self.server_handler = threading.Thread(
            target=self.handle_server,
            args=(self.server_ip, self.server_port, self.server_max_clients)
        )

        self.server_handler.start()

    def handle_server(self, server_ip, server_port, server_max_clients):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server_socket.bind((server_ip, server_port))
            debug('Bind successful')
        except Exception as e:
            debug('Failed to bind to {}:{}: {}'.format(server_ip, server_port, e), err=True)

        self.server_socket.listen(server_max_clients)
        debug('Listening to {}:{} with a clients limit of {}'.format(server_ip, server_port, server_max_clients))
        
        while True:
            client_socket, addr = self.server_socket.accept()
            client_ip, client_port = addr[0], addr[1]
            debug('New incomming connection from {}:{}'.format(client_ip, client_port))

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_ip, client_port))
            client_handler.start()

        debug('Closing server socket')
        self.server_socket.close()

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

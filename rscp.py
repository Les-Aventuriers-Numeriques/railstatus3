import socket
import threading
import arrow
import click


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
            debug('Failed to bind to {}:{}: {}'.format(bind_ip, server_port, e), err=True)

        self.server_socket.listen(server_max_clients)
        debug('Listening to {}:{} with a clients limit of {}'.format(server_ip, server_port, server_max_clients))
        
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                client_ip, client_port = addr[0], addr[1]
                debug('New incomming connection from {}:{}'.format(client_ip, client_port))
        
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_ip, client_port))
                client_handler.start()
            except Exception as e:
                debug('Server error: {}'.format(e), err=True)
        
        debug('Closing server socket')
        self.server_socket.close()

    def handle_client(self, client_socket, client_ip, client_port):
        def send_data_to_client(data):
            data += '\n'
            client_socket.sendall(data.encode('utf8'))

        local = threading.local()
        local.rscp_version = None

        while True:
            try:
                data = client_socket.recv(1024)

                if not data:
                    break
                
                data = data.decode('utf8').strip().split(' ')

                if len(data) < 2:
                    send_data_to_client('BAD_FORMAT')
                    continue
                
                obj = data[0]
                action = data[1]
                parameters = data[2:]

                if not local.rscp_version:
                    if obj != 'RSCP' or action != 'VERSION' or len(parameters[0]) != 1:
                        send_data_to_client('NOT_A_RSCP_CLIENT')
                        break
                    else:
                        local.rscp_version = parameters[0]
                        send_data_to_client('ACK')
                        continue

                if obj == 'POSITION':
                    if action == 'UPDATE':
                        if len(parameters[0]) != 1:
                            send_data_to_client('INVALID_PARAMETERS_NUMBER')
                            continue

                        position = parameters[0]

                        with open('positions.txt', 'a') as f:
                            f.write(arrow.now().format('DD/MM/YYYY HH:mm:ss') + ' : ' + position + '\n')

                        send_data_to_client('SUCCESS')
                    else:
                        send_data_to_client('UNKNOWN_ACTION')
                else:
                    send_data_to_client('UNKNOWN_OBJECT')
            except Exception as e:
                debug('recv error from {}:{}: {}'.format(client_ip, client_port, e), err=True)

        client_socket.close()
        debug('Connection from {}:{} closed'.format(client_ip, client_port))

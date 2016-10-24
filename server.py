import socket
import threading
import sys
import click
import arrow


def debug(message, err=False):
    click.echo('{} - {} - {}'.format(
        arrow.now().format('DD/MM/YYYY HH:mm:ss'),
        'ERR ' if err else 'INFO',
        message
    ), err=err)


@click.command()
@click.option('--ip', default='127.0.0.1', help='Bind IP')
@click.option('--port', default=8888, help='Bind port')
@click.option('--clients', default=10, help='Maximum concurrent clients')
def run_server(ip, port, clients):
    debug('Running server')

    server_handler = threading.Thread(target=handle_server, args=(ip, port, clients))
    server_handler.start()


def handle_server(bind_ip, bind_port, max_clients):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind((bind_ip, bind_port))
        debug('Bind successful')
    except Exception as e:
        debug('Failed to bind to {}:{}: {}'.format(bind_ip, bind_port, e), err=True)
        sys.exit(1)

    server_socket.listen(max_clients)
    debug('Listening to {}:{} with a clients limit of {}'.format(bind_ip, bind_port, max_clients))
    
    while True:
        try:
            client_socket, addr = server_socket.accept()
            client_ip, client_port = addr[0], addr[1]
            debug('New incomming connection from {}:{}'.format(client_ip, client_port))
    
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_ip, client_port))
            client_handler.start()
        except Exception as e:
            debug('Server error: {}'.format(e), err=True)
    
    debug('Closing server socket')
    server_socket.close()


def handle_client(client_socket, client_ip, client_port):
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
                send_data_to_client('PROTOCOL_VIOLATION')
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


if __name__ == '__main__':
    debug('Initializing')

    run_server()
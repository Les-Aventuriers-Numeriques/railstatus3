import click
import rscp


@click.command()
@click.option('--ip', default='127.0.0.1', help='Bind IP')
@click.option('--port', default=8888, help='Bind port')
@click.option('--clients', default=10, help='Maximum concurrent clients')
def run(ip, port, clients):
    rscp.debug('Running RSCP server')

    rscp_server = rscp.Server(ip, port, clients)
    rscp_server.run()


# TODO
# HTTP server http://flask.pocoo.org/
# Push events to the browser https://flask-sse.readthedocs.io/en/latest/

if __name__ == '__main__':
    run()

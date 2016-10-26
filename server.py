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
# SSE to the browser https://www.html5rocks.com/en/tutorials/eventsource/basics/

if __name__ == '__main__':
    run()

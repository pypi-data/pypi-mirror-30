import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)

def cli():
    click.echo("Welcome to Basematic-Server")

@cli.command(short_help="Qsub the Jobs In The File")
@click.option('--thread', '-t', default='1', help='Threads')
@click.option('--mem', '-m', default='2G', help='Memory')
@click.argument('jobs')

def QSUB(jobs, thread, mem):
    print('RNA-Seq', jobs)

@cli.command(short_help="Serve the current Dir")
@click.option('--port', default='8777', help='The Port')
def server(port):
    try:
        from http.server import test
        test(port = int(port))
    except:
        import SimpleHTTPServer
        import SocketServer
        PORT = int(port)
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        Handler.extensions_map.update({
            '.webapp': 'application/x-web-app-manifest+json',
        });
        httpd = SocketServer.TCPServer(("", PORT), Handler)
        httpd.serve_forever()
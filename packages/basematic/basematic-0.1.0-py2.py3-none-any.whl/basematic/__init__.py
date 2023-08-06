import basematic
import click

def main():
    pass

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--name', default='', help='Who are you?')

def cli(name):
    click.echo("Welcome to Basematic.")

@cli.command()
@click.option('--input', '-i', default='', help='File Path')
@click.option('--output', '-o', default='', help='File Output Path')
@click.argument('name')
def RNASeq(name, input, output):
    """
    RNASeq is Very important
    """
    print('RNA-Seq', name, input, output)

@cli.command()
def CNV():
    click.echo('Start Using CNV Analysis')

@cli.command()
def GATK():
    click.echo('Synching')

@cli.command()
@click.option('--port', default='8777', help='The Port')
def webServer(port):
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
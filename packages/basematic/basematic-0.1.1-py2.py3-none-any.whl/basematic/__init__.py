import basematic
import click

def main():
    pass

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--name', default='', help='Who are you?')

def cli(name):
    import subprocess
    cmd = 'eval "$(_BASEMATIC_COMPLETE=source basematic)"'
    subprocess.call(cmd, shell=True)
    click.echo("Welcome to Basematic.")

@cli.command(short_help = "Show the status of jobs")
@click.option('--port', '-p', default='./', help='port')
@click.argument('name')
def looker(name, port):
    click.echo('Start Using CNV Analysis')
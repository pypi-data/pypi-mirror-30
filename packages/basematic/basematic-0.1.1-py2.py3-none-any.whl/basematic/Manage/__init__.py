import basematic
import click

def main():
    pass

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--name', default='', help='Who are you?')

def cli(name):
    pass

@cli.command(short_help = "Show the status of jobs")
@click.argument('path')
def list_fastq(path):
    click.echo('Start Using CNV Analysis')

@cli.command(short_help = "Show the Softs")
def softs():
    click.echo('Show the softs')

@cli.command(short_help = "Show the Softs")
@click.option('--file', default='', help='File path with softname and its path, for multiple softs')
@click.option('--name', default='', help='Name of Software')
@click.option('--path', default='', help='path')
def soft_add(name, path):
    click.echo('Show the softs')

@cli.command(short_help = "Show the status of jobs")
@click.argument('path')
def list_reference(path):
    click.echo('Start Using CNV Analysis')

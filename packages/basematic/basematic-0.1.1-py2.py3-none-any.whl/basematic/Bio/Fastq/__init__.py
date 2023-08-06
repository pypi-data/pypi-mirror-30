import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)

def cli():
    click.echo("Welcome to Basematic-GATK")

@cli.command(short_help="Quality Control")
@click.option('--path', '-d', default='./', help='File Path')
def Quality(path):
    from basematic.Bio.Fastq.Stats import Stats_Fastq
    click.echo('Start Using CNV Analysis')
    print(Stats_Fastq(path))

@cli.command(short_help="Quality Control")
@click.option('--path', '-d', default='./', help='File Path')
def Trim(path):
    from basematic.Bio.Fastq.Stats import Stats_Fastq
    click.echo('Start Using CNV Analysis')
    print(Stats_Fastq(path))

import click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)

def cli():
    click.echo("Welcome to Basematic-GATK")

@cli.command(short_help="Install GATK and related references")
@click.option('--path', '-d', default='./', help='File Path')
def INSTALL(name, input, output):
    """
    GATK can be download by running:
        wget https://github.com/broadinstitute/gatk/releases/download/4.0.3.0/gatk-4.0.3.0.zip
    Picard can be downloaded:
        wget XX.picard
    """
    print('RNA-Seq', name, input, output)

@cli.command(short_help="Config The Reference")
@click.option('--file', '-d', default='./', help='softdir')
@click.option('--soft', '-d', default='./', help='BWA Path')
def Config(soft, dir):
    """
    """
    from basematic.Server.Check_Softs import get_soft_path
    softs = ['samtools', 'bwa', 'java', 'picard']
    resource = ['DBSNP', 'hg38_genome', 'hg38_bwa_index']
    for soft in softs:
        print(soft, get_soft_path(soft))

@cli.command(short_help="Test the pipeline...")
def TEST():
    click.echo('Start Using CNV Analysis')

@cli.command(short_help="Run")
@click.option('--name', help="Sample Files, include name, fq1, fq2")
@click.option('--dir', default='', help='run in qsub mode')
@click.option('--fq1', default='', help='run in qsub mode')
@click.option('--fq2', default='', help='run in qsub mode')
def RUN(name, dir, fq1, fq2):
    click.echo('Start Using CNV Analysis')

@cli.command(short_help="Run the GATK for Multiple Samples")
@click.option('--sample', help="Sample Files, include name, fq1, fq2")
@click.option('--qsub', default='', help='run in qsub mode')
def RUN_BATCH(qsub):
    click.echo('RUN SEVERAL SAMPLES IN THE SAME')

@cli.command(short_help="Filter the VCF")
def VCFFilter():
    click.echo('Start Using CNV Analysis')
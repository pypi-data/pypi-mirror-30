import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    message = """
    Welcome to Basematic-RNA, you can process your RNA-Seq datas with our tools.
    """
    click.echo(message)

@cli.command(short_help="Install Salmon and related references")
@click.option('--path', '-d', default='./', help='File Path')
@click.option('--species', '-s', default='human', help='Species: human, mouse, zebrafish')
def INSTALL(path, species):
    """
    salmon can be installed by: conda install salmon \n
    supported species: human, mouse, zebrafish \n
    salmon index: \n
    salmon quant: \n
    """
    species = ['human', 'mouse', 'zebrafish']
    print('RNA-Seq')

@cli.command(short_help="Config The Reference")
@click.option('--dir', '-d', default='./', help='softdir')
@click.option('--soft', '-s', default='./', help='softs')
def Config(soft, dir):
    from basematic.Server.Check_Softs import get_soft_path
    pass

@cli.command(short_help="Test the pipeline...")
def TEST():
    click.echo('Start Using RNA-Seq')

@cli.command(short_help="Run")
@click.option('-species', help="human mouse zebrafish")
@click.option('-name', help="Sample Files, include name, fq1, fq2(optional)")
@click.option('-dir', default='./', help='folder to write to')
@click.option('-mode', default='local', help='run in local(default) or qsub mode')
def RUN(name, species, d, qsub, local):
    click.echo('Start Using RNA')

@cli.command(short_help="Run the GATK for Multiple Samples")
@click.option('--sample', help="Sample Files, include name, fq1, fq2")
@click.option('--tpmFile', default='', help='Aggregate')
@click.option('--qsub', default='', help='run in qsub mode')
def RUN_BATCH(qsub, sample, tpmfile):
    click.echo('RUN SEVERAL SAMPLES IN THE SAME')
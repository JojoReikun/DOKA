"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""

import os
import click
from pathlib import Path

import lizardanalysis

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(invoke_without_command=True)
# @click.version_option()
@click.option('-v', '--verbose', is_flag=True, help='Verbose printing')
@click.pass_context
def main(ctx, verbose):
    if ctx.invoked_subcommand is None:
        click.echo('lizardanalysis v0.0.')
        click.echo(main.get_help(ctx))

##################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('project')
@click.argument('experimenter')
@click.argument('species')
@click.argument('files', nargs=-1, type=click.Path(exists=True, dir_okay=True))
@click.option('-d', '--wd', 'working_directory',
              type=click.Path(exists=True, file_okay=False, resolve_path=True), default=Path.cwd(),
              help='Directory to create project in. Default is cwd().')
@click.pass_context

def start_new_analysis(_, *args, **kwargs):
    """Create a new project directory, sub-directories and a basic configuration file. The configuration file is loaded with default values. Change its parameters to your projects need.\n
    Options \n
    ---------- \n
    project : string \n
    \tString containing the name of the project.\n
    experimenter : string \n
    \tString containing the name of the experimenter. \n
    species : string \n
    \tString containing the name of the species analyzed. \n
    files : list \n
    \tA list of string containing the full path to the folder containing the DLC result csv files to include in the project.\n
    working_directory : string, optional \n
    \tThe directory where the project will be created. The default is the ``current working directory``; if provided, it must be a string\n
    """
    from lizardanalysis.start_new_analysis import new
    new.create_new_project(*args, **kwargs)



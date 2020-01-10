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


def create_new_project(_, *args, **kwargs):
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


#####################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config')
@click.option('--separate_gravity_file', 'separate_gravity_file',
              is_flag=False,
              default=False,
              help='Set True if you want to import a separate gravity csv file as calibration. The default is False')
@click.option('--likelihood', 'likelihood',
              default=0.90,
              help='Change to vary accuracy of labels included in analysis. Likelihood is always 3rd column for every tracked label of DLC results.')
@click.pass_context


def read_csv_files(_, *args, **kwargs):
    """Reads in the given list of .csv files.
    Options \n
    ---------- \n
    config : string \n
    \tString containing the full path to the config file of the project. \n
    separate_gravity_file : bool, optional \n
    \tOptionally define a csv file with gravity data for calibration. Default: seperate_gravity_file=False.
    likelihood: float \n
    \tFloat betw. 0.0 and 1.0, which defines the accuracy used to include labels into the analysis. Default: 0.9
    """
    from lizardanalysis.calculations import read_in_files
    read_in_files.read_csv_files(*args, **kwargs)


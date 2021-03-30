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


def analyze_files(_, *args, **kwargs):
    """Reads in the given list of .csv files and performs calculations on all of them.
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
    read_in_files.analyze_files(*args, **kwargs)


#####################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config')
@click.option('save_as_csv',
              is_flag=True,
              default=True,
              help='Set True if you want to save the morph data for every file. The default is True')
@click.pass_context


def calc_morphometrics(_, *args, **kwargs):
    """Calculated the morphometrics of the skeleton as defined in the DLC config file.
    Requires to paste the skeleton into the config file used for lizardanalysis.
    Options \n
    ---------- \n
    config : string \n
    \tString containing the full path to the config file of the project. \n
    save_as_csv : bool, optional \n
    \tOptionally Save the morph data for every file as csv. Default: save_as_csv=True.
    """
    from lizardanalysis.calculations import lizard_morphometrics
    lizard_morphometrics.calc_morphometrics(*args, **kwargs)

#####################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config')
@click.option('--plotting', 'plotting',
              is_flag=False,
              default=False,
              help='Set True if you want to generate overview plots grouped by species. The default is False')
@click.option('--direction_filter', 'direction_filter',
              is_flag=True,
              default=True,
              help='Set True if you want to filter the results by direction. The default is True')
@click.pass_context


def summarize_results(_, *args, **kwargs):
    """Creates species-wise result files and result overview. Also includes plotting as an option.
    Options \n
    ---------- \n
    config : string \n
    \tString containing the full path to the config file of the project. \n
    plotting : bool, optional \n
    \tOptionally define a csv file with gravity data for calibration. Default: seperate_gravity_file=False.
    likelihood: float \n
    \tFloat betw. 0.0 and 1.0, which defines the accuracy used to include labels into the analysis. Default: 0.9
    """
    from lizardanalysis.calculations import write_result_files
    write_result_files.summarize_results(*args, **kwargs)


#####################################################################################

@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument('config')
@click.pass_context


def create_stepwise_summary(_, *args, **kwargs):
    """Creates an step-wise result file.
    Options \n
    ---------- \n
    config : string \n
    \tString containing the full path to the config file of the project. \n
    """
    from lizardanalysis.calculations import step_wise_summary
    step_wise_summary.summarize_stepwise(*args, **kwargs)
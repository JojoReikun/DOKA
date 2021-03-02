"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""

# TODO: complete as going along
import os

DEBUG = True and 'DEBUG' in os.environ and os.environ['DEBUG']
from lizardanalysis import DEBUG

from lizardanalysis import start_new_analysis
from lizardanalysis.start_new_analysis import create_new_project
from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis import calculations
from lizardanalysis.calculations.read_in_files import analyze_files, initialize
from lizardanalysis.calculations.write_result_files import summarize_results
from lizardanalysis.calculations.lizard_morphometrics import calc_morphometrics
from lizardanalysis.calculations.step_wise_summary import summarize_stepwise

from lizardanalysis.version import __version__, VERSION

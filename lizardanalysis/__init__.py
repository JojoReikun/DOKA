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
from lizardanalysis.calculations import read_csv_files


from lizardanalysis.version import __version__, VERSION
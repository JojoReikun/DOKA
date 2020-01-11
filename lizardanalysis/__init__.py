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
from lizardanalysis.calculations.read_in_files import read_csv_files
# ,calc_direction_of_climbing, calc_climbing_speed, calc_stride_and_stance_phases, calc_stride_length, calc_limb_kinematics, calc_wrist_angles


from lizardanalysis.version import __version__, VERSION
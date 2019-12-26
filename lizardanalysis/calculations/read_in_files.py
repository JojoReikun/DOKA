"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""


def read_csv_files(config, seperate_gravity_file=False):
    """
    Reads the DLC result csv files which are listed in the config file.
    config : string
        Contains the full path to the config file of the project.
        Tipp: Store path as a variable >>config<<
    seperate_gravity_file : bool, optional
        If this is set to True, user can choose a gravity csv file to use the gravity axis as reference axis for analysis.
        If this is set to False, x-axis of video will be used as reference axis for analysis.
        Default: False
    """
    import os
    import sys
    import numpy as np
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    print("Config file read successfully.")

    # get the file paths from the config file
    files = cfg['file_sets'].keys()

    # check if user entered camera specs in config file
    if cfg['framerate'] == '' and cfg['shutter'] == '':
        print('Please add camera settings in the config file before you continue.')
        return

    # TODO: read in the csv result files, store the pandas data frames somehow and check & store existing labels
    # TODO: depending on existing labels and requirements of the individual calculations check which calculations are possible

    if seperate_gravity_file:
        # TODO: open file explorer and let user choose a gravity csv file


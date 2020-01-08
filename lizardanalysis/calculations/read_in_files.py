"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""

def check_calculation_requirements(cfg):
    """
    this function checks if the required labels needed for the respective calculations
    are available in the list of available label extracted from the .csv file before.
    Depending on the result of the comparison, the calculation bool will be set to True/False.
    :param cfg: read in config file
    :return: bolls of the calculations
    If labels are named similarly but differ from default slightly, variations can be added to another variation list
    and additionally checked with any() instead of all()
    """
    requ_direction_of_climbing = ['nose']
    direction_of_climbing = all(elem in cfg['labels'] for elem in requ_direction_of_climbing)

    requ_climbing_speed = ['nose', 'framerate']
    climbing_speed = all(elem in cfg['labels'] for elem in requ_climbing_speed)

    requ_stride_and_stance_phases = ['FL', 'FR', 'HL', 'HR']
    stride_and_stance_phases = all(elem in cfg['labels'] for elem in requ_stride_and_stance_phases)

    if stride_and_stance_phases:
        stride_length = True

    requ_limb_kinematics = ['Shoulder', 'Hip', 'FR_knee', 'Shoulder_FR', 'FL_knee', 'Shoulder_FL', 'HR_knee',
                       'Shoulder_HR', 'HL_knee', 'Shoulder_HL']
    limb_kinematics = all(elem in cfg['labels'] for elem in requ_limb_kinematics)

    # wrist_angles = FL, FR, HL, HR, ti, to, shoulder, hip
    requ_wrist_angles = ['Shoulder', 'Hip', 'FR_knee', 'FR_ti', 'FR_to', 'FL_knee', 'FL_ti', 'FL_to', 'Shoulder_FL',
                         'HR_knee', 'HR_ti', 'HR_to', 'HL_knee', 'HL_ti', 'HL_to']
    wrist_angles = all(elem in cfg['labels'] for elem in requ_wrist_angles)

    # ROM
    return direction_of_climbing, climbing_speed, stride_and_stance_phases, stride_length, limb_kinematics, wrist_angles


def process_file(data, direction_of_climbing, climbing_speed, stride_and_stance_phases, stride_length, limb_kinematics, wrist_angles):
    """
    Goes through all calculations and calculates the parameters depending on the state of the booleans.
    If boolean is True, the required labels for the calculation are available and parameter will be calculated.
    If boolean is False, one or more of the required labels are missing/weren't found and parameter will be skipped.
    :param direction_of_climbing: bool
    :param climbing_speed: bool
    :param stride_and_stance_phases: bool
    :param stride_length: bool
    :param limb_kinematics: bool
    :param wrist_angles: bool
    :return: #TODO
    """
    # TODO: write and import functions
    if direction_of_climbing:
        from lizardanalysis.calculations import calc_direction_of_climbing
        calc_direction_of_climbing(data)
    else:
        print('At least one label required for the calculation of the direction of climbing is missing. Parameter skipped.')


def read_csv_files(config, separate_gravity_file=False):
    """
    Reads the DLC result csv files which are listed in the config file and checks which labels are available for calculation.
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
    from tkinter import Tk, filedialog
    from lizardanalysis.utils import auxiliaryfunctions
    import pandas as pd

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    print("Config file read successfully.")

    # get the file paths from the config file
    project_path = cfg['project_path']

    files = cfg['file_sets'].keys()   # object type ('CommentedMapKeysView' object), does not support indexing
    filelist = []   # store filepaths as list
    for file in files:
        filelist.append(file)
    #print("files (keys): ,", filelist)  # TEST

    # check if user entered camera specs in config file
    if cfg['framerate'] is None and cfg['shutter'] is None:
        print('Please add camera settings in the config file before you continue.')
        return
    else:
        print('Camera settings entered: \n',
              'framerate: ', cfg['framerate'], '\n',
              'shutter: ', cfg['shutter'], '\n',
              'Available labels will be checked and written to config file...')

    # check if user set separate gravity file to True
    if separate_gravity_file:
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        gravity_filepath = filedialog.askopenfilename(filetype=[('csv files', '*.csv')])  # show an "Open" dialog box and return the path to the selected file
        df_gravity = pd.read_csv(gravity_filepath)   # read in gravity file

    # check available labels in .csv files and write them to config file. Uses the first .csv file in the directory.
    # TODO: Check if working directory differs from default and set path respectively
    # if working_directory = DEFAULT:
    # use Path lib
    current_path = Path(os.getcwd())
    project_dir = '{pn}-{exp}-{spec}-{date}'.format(pn=cfg['Task'], exp=cfg['scorer'], spec=cfg['species'], date=cfg['date'])
    label_file_path_2 = os.path.join(project_dir, "files", os.path.basename(filelist[0]))
    label_file_path = os.path.join(current_path, label_file_path_2)
    #print('label_file_path: ', label_file_path)
    # else:
    # TODO: look for working directory
    data = pd.read_csv(label_file_path, delimiter=",", header=[0, 1, 2]) # reads in first csv file in filelist to extract all available labels
    data.rename(columns=lambda x: x.strip(), inplace=True) # remove whitespaces from column names
    #print(data.head())

    data_columns = list(data.columns)
    # scorer = data_columns[1][0]     atm not needed
    label_names = []
    for i in range(1, len(data_columns)):
        label_names.append(data_columns[i][1])
    label_names_no_doubles = []
    [label_names_no_doubles.append(label) for label in label_names if label not in label_names_no_doubles]

    if len(label_names_no_doubles) == 0:
        print('no labels could be found. Maybe check that there are .csv files available in the files folder with the DLC result format.')
        return
    else:
        print("available are the following ", len(label_names_no_doubles), " labels in csv files: ", label_names_no_doubles)

    # write labels to config file:
    if cfg['labels'] is None:
        cfg['labels'] = label_names_no_doubles
        auxiliaryfunctions.write_config(config, cfg)
        print('\n labels written to config file.')
    else:
        print('labels already exist in config file.')

    # check label requirements for calculations:
    direction_of_climbing, climbing_speed, stride_and_stance_phases, stride_length, limb_kinematics, wrist_angles = check_calculation_requirements(cfg)

    # TODO: run calculations loop
    process_file(data, direction_of_climbing, climbing_speed, stride_and_stance_phases, stride_length, limb_kinematics, wrist_angles)




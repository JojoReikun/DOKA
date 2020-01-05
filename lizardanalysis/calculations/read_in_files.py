"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""


def read_csv_files(config, separate_gravity_file=False):
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

    # check available labels in .csv files and write them to config file
    # TODO: Check if working directory differs from default and set path respectively
    # if working_directory = DEFAULT:
    # use Path lib
    current_path = Path(os.getcwd())
    project_dir = '{pn}-{exp}-{spec}-{date}'.format(pn=cfg['Task'], exp=cfg['scorer'], spec=cfg['species'], date=cfg['date'])
    label_file_path = project_dir / "files" / os.path.basename(filelist[0])
    print('label_file_path: ', label_file_path)
    rel_label_file_path = os.path.relpath(label_file_path)
    # else:
    # TODO: look for working directory
    rel_label_file_path = os.path.relpath(label_file_path)
    print('relative label file path: ', label_file_path)
    data = pd.read_csv(label_file_path)
    data.head()
    # print('labels written to config file.')



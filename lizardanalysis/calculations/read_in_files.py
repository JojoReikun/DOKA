"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""
import pandas as pd
import glob
from lizardanalysis.utils.auxiliaryfunctions import UserFunc

drop_empty_cols = True

# list of all calculations and their requirements of labels as implemented in the program
calculations = {'direction_of_climbing': ['nose'],
                'body_axis_deflection_angle': ['shoulder', 'hip'],
                'climbing_speed_framewise': ['nose'],
                'stride_and_stance_phases': ['fl', 'fr', 'hl', 'hr'],
                'step_length': ['fl', 'fr', 'hl', 'hr'],
                'limb_kinematics': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl', 'hr_knee',
                                    'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                'wrist_angles': ['shoulder', 'hip', 'fr_knee', 'fr_ti', 'fr_to', 'fl_knee', 'fl_ti', 'fl_to',
                                 'shoulder_fl', 'hr_knee', 'hr_ti', 'hr_to', 'hl_knee', 'hl_ti', 'hl_to'],
                'limb_rom': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                             'hr_knee', 'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                'spine_rom': ['shoulder', 'hip', 'spine'],
                'center_limb_rom_angle': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                                          'hr_knee', 'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                'hip_and_shoulder_angles': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                                            'hr_knee',
                                            'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                'knee_and_elbow_angles': ['fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl', 'hr_knee',
                                          'shoulder_hr', 'hl_knee', 'shoulder_hl', 'fl', 'fr', 'hl', 'hr']
                }

calculations_str = [calc for calc in calculations.keys()]
#print('list of calculations ', calculations_str)
MODULE_PREFIX, _ = __name__.rsplit('.', 1)


def check_labels(cfg, filelist):
    """
    checks available labels in .csv files and write them to config file.
    Uses the first .csv file in the directory.
    :param cfg: the config file
    :param filelist: all csv files found in the directory
    :return: list with available labels
    """
    import os
    from pathlib import Path

    # TODO: Check if working directory differs from default and set path respectively
    # if working_directory = DEFAULT:
    current_path = Path(os.getcwd())
    # mgs: replaced this by f-string. Much more concise and even faster ;-)
    project_dir = f"{cfg['task']}-{cfg['scorer']}-{cfg['species']}-{cfg['date']}"
    label_file_path_2 = os.path.join(project_dir, "files", os.path.basename(filelist[0]))
    label_file_path = os.path.join(current_path, label_file_path_2)
    # print('label_file_path: ', label_file_path)
    # else:
    # TODO: look for working directory
    data_labels = pd.read_csv(label_file_path, delimiter=",",
                              header=[0, 1, 2])  # reads in first csv file in filelist to extract all available labels
    data_labels.rename(columns=lambda x: x.strip(), inplace=True)  # remove whitespaces from column names
    # print(data.head())

    data_labels_columns = list(data_labels.columns)

    # find unique labels and make sure they appear only once. Convert them all to lower case
    label_names = [str(data_labels_columns[i][1]).lower() for i in range(1, len(data_labels_columns))]
    label_names = [str(label[1]).lower() for label in data_labels_columns]
    label_names_no_doubles = list(set(label_names))

    if len(label_names_no_doubles) == 0:
        print(
            'no labels could be found. Maybe check that there are .csv files available in the files folder with the DLC result format.')
        return
    else:
        print("available are the following ", len(label_names_no_doubles), " labels in csv files: ",
              label_names_no_doubles)

    return data_labels, label_names_no_doubles, project_dir


def check_calculation_requirements(cfg):
    """
    this function checks if the required labels needed for the respective calculations
    are available in the list of available label extracted from the .csv file before.
    Depending on the result of the comparison, the calculation will be added to the calculations_checked list
    :param cfg: read in config file
    :return: list of available calculations
    """
    # If labels are named similarly but differ from default slightly, variations can be added to another variation list
    # and additionally checked with any() instead of all()

    calculations_checked = []
    calculations_checked_namelist = []
    for calculation in calculations_str:
        # print('cfg labels: ', cfg['labels'])
        # print('calculation values: ', calculations['{}'.format(calculation)])
        calculation_ok = all(elem in cfg['labels'] for elem in calculations['{}'.format(calculation)])   # RETURNS bool
        # print('calculation_ok: ', calculation_ok)
        # add available calculations to list
        if calculation_ok:
            calculations_checked_namelist.append(calculation)
            func = UserFunc(MODULE_PREFIX+'.'+calculation, calculation)   # module name calculation, function name calculation
            calculations_checked.append(func)
    if len(calculations_checked) == 0:
        print(
            'there is no calculation available for analysis due to insufficient or non-relevant labels in DLC result files.')
        return

    return calculations_checked, calculations_checked_namelist


def process_file(data, clicked, likelihood, calculations_checked, df_result_current, data_rows_count, config, filename):
    """
    Goes through all available calculations which were determined on their labels and stored in calculations_checked.
    For all calculations in that list the parameter will be calculated.
    If calculations not in calculations_checked but in calculations, one or more of the required labels are missing/weren't found and parameter will be skipped.
    :param data: pd.dataframe DLC csv file
    :param likelihood: float value to change accuracy of results
    :param calculations_checked: list of available calculations (required labels exist)
    :param clicked value determines definition of direction UP for the given videos from experiment. Value determined in GUI during execution of create_new_project()
    :param df_result_current: empty result dataframe for current file which will be filled up while looping through these calculations
    :param data_rows_count: number of rows in current csv file
    :param config: given filepath to the config file by the user
    :filename: filename of the current file
    :return: retval: dataframe
             returns the results from the calculation as dictionary to write to df_results_current
    """

    # filter data for values using the given likelihood >= e.g. 90%

    for calc in calculations_checked:
        # TODO: Can I pass a different number of kwargs for different calculations? E.g. df_result_current is only needed for calcs after stride_and_stance phases?
        retval = calc(data=data, clicked=clicked, data_rows_count=data_rows_count, likelihood=likelihood,
                      config=config, filename=filename, df_result_current=df_result_current) # returns a dict with numpy arrays
        for key in retval:
            df_result_current[key] = retval[key]
        #print(df_result_current.head(5), '\n',
              #df_result_current.tail(5))

    return df_result_current


def read_csv_files(config, separate_gravity_file=False, likelihood=0.90):
    """
    Reads the DLC result csv files which are listed in the config file and checks which labels are available for calculation.
    config : string
        Contains the full path to the config file of the project.
        Tipp: Store path as a variable >>config<<
    seperate_gravity_file : bool, optional
        If this is set to True, user can choose a gravity csv file to use the gravity axis as reference axis for analysis.
        If this is set to False, x-axis of video will be used as reference axis for analysis.
        Default: False
    likelihood: float [0.0-1.0]
        defines the level of accuracy used for including label results in the analysis.
        Default: 0.90
    """
    import os
    from pathlib import Path
    from tkinter import Tk, filedialog
    from lizardanalysis.utils import auxiliaryfunctions
    import errno

    current_path = os.getcwd()
    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    print("Config file read successfully.")

    # find the clicked value which defines the configuration of directions
    clicked = cfg['clicked']

    # get the file paths from the config file
    project_path = cfg['project_path']

    files = cfg['file_sets'].keys()  # object type ('CommentedMapKeysView' object), does not support indexing
    filelist = []  # store filepaths as list
    for file in files:
        filelist.append(file)

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
        gravity_filepath = filedialog.askopenfilename(
            filetype=[('csv files', '*.csv')])  # show an "Open" dialog box and return the path to the selected file
        df_gravity = pd.read_csv(gravity_filepath)  # read in gravity file

    # check available labels:
    data_labels, labels_no_doubles, project_dir = check_labels(cfg, filelist)
    # write labels to config file:
    if cfg['labels'] is None:
        cfg['labels'] = labels_no_doubles
        auxiliaryfunctions.write_config(config, cfg)
        print('\n labels written to config file.')
    else:
        print('labels already exist in config file. Proceed...')

    # check label requirements for calculations:
    calculations_checked, calculations_checked_namelist = check_calculation_requirements(cfg)
    print("available calculations are the following: ", *calculations_checked_namelist, sep='\n - ')  #* vor print list enables nice prints

    ############################################## RUN CALCULATION LOOP #################################################
    print("\nSTART analysis off all {} csv files in project ...".format(len(filelist)))

    if cfg['save_rmse_values']:
        dynamics_folder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results",
                                       "limb_dynamics_curve_fitting")
        try:
            os.makedirs(dynamics_folder)
            print("folder for curve_fitting plots created")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        columns_list = ['filename', 'rmse_sig', 'std_sig', 'rmse_lin', 'std_lin', 'rmse_exp', 'std_exp', 'rmse_log',
                        'std_log']
        df_rmse = pd.DataFrame(columns=columns_list)
        df_rmse.to_csv(os.path.join(dynamics_folder, "rmse.csv"), header=True, index=False)

        # try:
        #     os.path.isfile(os.path.join(dynamics_folder, "rmse.csv"))
        #     print("folder for curve_fitting plots created")
        # except OSError as e:
        #     if e.errno != errno.EEXIST:
        #         raise

    for i in range(len(filelist)):
        #print('\n \n ----- FILE: ', filelist[i])
        filename = filelist[i].rsplit(os.sep, 1)[1]
        filename = filename.rsplit(".", 1)[0]
        print(' ----- FILENAME: ', filename)
        file_path_2 = os.path.join(project_dir, "files", os.path.basename(filelist[i]))
        file_path = os.path.join(current_path, file_path_2)

        # read in the current csv file as dataframe
        data = pd.read_csv(file_path, delimiter=",",
                           header=[0, 1, 2])  # reads in first csv file in filelist to extract all available labels
        data_labels.rename(columns=lambda x: x.strip(), inplace=True)  # remove whitespaces from column names
        data_rows_count = data.shape[0]   # number of rows already excluded the 3 headers
        #print(data.head())
        #print('row count for dataframe (excluding headers): ', data_rows_count)

        # generate empty result file for current file: columns = available calculations, rows = nb. of rows in csv file
        df_result_current = pd.DataFrame(columns=calculations_checked_namelist, index=range(data_rows_count))
        #print(df_result_current.head())

        ##################################### PROCESS FILE #########################################
        # perform calculations for the current file and get dataframe with results as return
        df_result_current = process_file(data, clicked, likelihood, calculations_checked, df_result_current, data_rows_count, config, filename)

        #################################### SAVE RESULT FILES ######################################
        #create result file for every file and save to analysis-results folder
        result_file = df_result_current.copy()
        if drop_empty_cols:
            empty_cols = [col for col in result_file.columns[0:len(calculations_checked_namelist)] if result_file[col].isnull().all()]
            # Drop empty columns from the dataframe which are created for every calculation_checked
            result_file.drop(empty_cols,
                             axis=1,
                             inplace=True)
        # TODO: same... function in utils to define result path, call here
        result_file_path = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results")
        result_file.to_csv(os.path.join(result_file_path, "{}.csv".format(filename)), index=True, header=True)
        # TODO: allow filters for result dataframe e.g. direction of climbing
        # count up to proceed to next file
        i += 1

    print("\n", "DONE!")


    # generate TOTAL result dataframe combining the results from all runs:
    #df_results_total = pd.DataFrame(columns=calculations_checked_namelist())

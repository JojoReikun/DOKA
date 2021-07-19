"""
LizardDLCAnalysis Toolbox
© Johanna T. Schultz
© Fabian Plum
Licensed under MIT License
"""

import os, pickle
import pandas as pd
from pathlib import Path
import numpy as np
import ruamel.yaml
from importlib import import_module


def create_config_template():
    """
    Creates a template for config.yaml file. This specific order is preserved while saving as yaml file.
    """
    import ruamel.yaml
    yaml_str = """\
# Project definitions (do not edit!)
    task:
    scorer:
    species:
    date:
    \n
# Experiment details (edit):
    location, where species was caught: 
    date, species was caught:
    date, experiments were conducted:
    individuals of species analyzed:
# Camera settings:
    model:
    framerate:
    shutter:
    \n
# Project path (change when moving around)
    project_path:
    \n
# Annotation of data set
    file_sets:
    \n
# Plotting configuration
    dotsize:
    alphavalue:
    colormap:
    \n
# Available labels (will be added automatically when running read_csv_files())
    labels:
    \n
# Analysis configurations:
# clicked: The selected video confoguration: clicked = 1 --> direction up with increasing x, clicked = 2 --> opposite
# distance_limit: The distance a foot has to move (px) to be viewed as in stride
# save_rmse_values: Defines if RMSE values for curve fitting of kinematics are saved to results. Default is True.
    clicked:
    distance_limit: 
    save_rmse_values:
    """


    ruamelFile = ruamel.yaml.YAML()
    cfg_file = ruamelFile.load(yaml_str)
    return(cfg_file,ruamelFile)


def read_config(configname):
    """
    Reads structured config file
    """
    ruamelFile = ruamel.yaml.YAML()
    path = Path(configname)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                cfg = ruamelFile.load(f)
        except Exception as err:
            if err.args[2] == "could not determine a constructor for the tag '!!python/tuple'":
                with open(path, 'r') as ymlfile:
                  cfg = yaml.load(ymlfile,Loader=yaml.SafeLoader)
                  write_config(configname,cfg)
    else:
        raise FileNotFoundError ("Config file is not found. Please make sure that the file exists and/or there are no unnecessary spaces in the path of the config file!")
    return(cfg)


def write_config(configname, cfg):
    """
    Write structured config file.
    """
    with open(configname, 'w') as cf:
        ruamelFile = ruamel.yaml.YAML()
        cfg_file, ruamelFile = create_config_template()
        for key in cfg.keys():
            cfg_file[key] = cfg[key]

        ruamelFile.dump(cfg_file, cf)


def attempttomakefolder(foldername,recursive=False):
    ''' Attempts to create a folder with specified name. Does nothing if it already exists. '''

    try:
        os.path.isdir(foldername)
    except TypeError: #https://www.python.org/dev/peps/pep-0519/
        foldername=os.fspath(foldername) #https://github.com/AlexEMG/DeepLabCut/issues/105 (windows)

    if os.path.isdir(foldername):
        #print(foldername, " already exists!")
        pass
    else:
        if recursive:
            os.makedirs(foldername)
        else:
            os.mkdir(foldername)


def py_angle_betw_2vectors(v1, v2):
    import numpy.linalg as la
    """Returns the angle in degrees between vectors 'v1' and 'v2'.
    The cosang function does not return the direction of deflection. Use atan if you need that feature"""
    cosang = np.dot(v1, v2) / (la.norm(v1) * la.norm(v2))
    # sinang = la.norm(np.cross(v1, v2))
    # return math.degrees(np.arctan2(sinang, cosang))
    return np.rad2deg(np.arccos(cosang))


def py_angle_betw_2vectors_atan(v1, v2):
    """Returns the angle in degrees between vectors 'v1' and 'v2'.
    Also gives the direction of deflection.
    If body axis is the first vector to be put in the deflection to the left of the body axis is positive angles,
    deflection to the right of the body axis negative."""
    import numpy.linalg as la

    #atan_rad = np.arctan2(sinang, cosang)

    #angle = atan2(vector2.y, vector2.x) - atan2(vector1.y, vector1.x)
    angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
    if angle > np.pi:
        angle -= 2 * np.pi
    elif angle <= -1*np.pi:
        angle +=2*np.pi

    return np.rad2deg(angle)


def calc_body_axis(df, index, scorer):
    """calculates the body axis vector of the gecko for the passed index: START = Hip, END = Shoulder
    returns a vector (x,y)"""
    #TODO: use likelihood value from config file
    likelihood_shoulder = df.loc[index, (scorer, "Shoulder", "likelihood")]
    likelihood_hip = df.loc[index, (scorer, "Hip", "likelihood")]
    if likelihood_shoulder >= 0.90 and likelihood_hip >= 0.90:
        body_axis_vector = ((df.loc[index, (scorer, "Shoulder", "x")] - df.loc[index, (scorer, "Hip", "x")]),
                            (df.loc[index, (scorer, "Shoulder", "y")] - df.loc[index, (scorer, "Hip", "y")]))
    else:
        body_axis_vector = (np.NAN, np.NAN)
    return body_axis_vector


def calc_spine_axis(df, index, scorer, spine_segment):
    """calculates the caudal or cranial axis vector of the gecko's spine for the passed index.
    the spine_segment is passed as an argument and contains the two labels defining the spine vector, e.g.
    cranial spine axis: spine_segment = ["Shoulder", "Spine_B]
    returns a vector (x,y)"""
    #TODO: use likelihood value from config file
    likelihood_a = df.loc[index, (scorer, spine_segment[0], "likelihood")]
    likelihood_b = df.loc[index, (scorer, spine_segment[1], "likelihood")]
    if likelihood_a >= 0.90 and likelihood_b >= 0.90:
        spine_axis_vector = ((df.loc[index, (scorer, spine_segment[0], "x")] - df.loc[index, (scorer, spine_segment[1], "x")]),
                            (df.loc[index, (scorer, spine_segment[0], "y")] - df.loc[index, (scorer, spine_segment[1], "y")]))
    else:
        spine_axis_vector = (np.NAN, np.NAN)
    return spine_axis_vector


def get_perpendicular_dist_to_vector(E, df, index, scorer):
    """
    calculates the perpendicular distance of point E to vector BA (= body axis)
    :param E: 'label name' of the point, for which the amplitude is wanted. Type: String
    df, index, and scorer are required to access the label locations in the current file
    :return: distance
    """
    A = (df.loc[index, (scorer, "Shoulder", "x")], df.loc[index, (scorer, "Shoulder", "y")])
    BA = calc_body_axis(df, index, scorer)
    E = (df.loc[index, (scorer, E, "x")], df.loc[index, (scorer, E, "y")])

    AE = ((E[0] - A[0]), E[1] - A[1])

    # Finding the perpendicular distance
    x1 = BA[0]
    y1 = BA[1]
    x2 = AE[0]
    y2 = AE[1]
    mod = np.sqrt(x1 * x1 + y1 * y1)
    dist = abs(x1 * y2 - y1 * x2) / mod

    return dist


def calculate_gravity_deflection_angle(bodyaxis):
    # TODO: add option to use  data from separate gravity file here
    gravity_axis = (100., 0.)
    angle_deflection = py_angle_betw_2vectors(gravity_axis, bodyaxis)
    return angle_deflection


def append_list_as_row_to_csv(file_name, list_of_elem):
    from csv import writer
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


class UserFunc():
    """Handle a user function which is defined as directory entry"""
    """
    Usage:
        # demo 1: os.getcwd()
        func = UserFunc(module_name='os', func_name='getcwd')
        print( 'Current working dir: ', func() )
        # demo 2: numpy arange(100)
        func = UserFunc('numpy', 'arange', 100)
        print( 'Numpy demo: ', func() )
        print( 'Numpy demo with new arg: ', func(20) )
    """
    def __init__(self, module_name=None, func_name=None, *args, **kwargs):

        try:
            self.module = import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f'Module {module_name} not found!')
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        func = getattr(self.module, self.func_name)
        if len(args) == 0:
            args = self.args
        if len(kwargs) == 0:
            kwargs = self.kwargs
        #print('args=', args, ', kwargs=', kwargs)
        #        if func_arg is None:
        #            retval = func()
        #        else:
        retval = func(*args, **kwargs)
        return retval

    def __repr__(self):
        return f'<function {self.func_name} at {hex(id(self))}>'


def find_conversion_factor_for_spider(filename):
    # calibrate distance: convert px to mm:
    # dictionary: Spider (Lxx,Lyy):factor in px/mm
    conversion_factors = {(62, 76): 2.57,
                          (77, 91): 2.56,
                          (92, 111): 2.58,
                          (112, 126): 2.58}
    spidername = filename.split(sep="_")[0]
    spidernumber = int(''.join(list(filter(str.isdigit, spidername))))      # find digits in string
    #print(f"spidername: {spidername}, spidernumber: {spidernumber}")

    conv_fac = np.nan
    for i in range(len(conversion_factors.keys())):
        key = list(conversion_factors.keys())[i]
        if spidernumber in range(key[0], key[1]):  # assign correct converion factor to spider
            conv_fac = conversion_factors[key]
            #print(f"spidernumber: {spidernumber}, conv_fac: {conv_fac}")

    if conv_fac == np.nan:
        print(f"no conversion factor was found for this spidernumber: {spidernumber}")
        conv_fac = 1.0

    return conv_fac


def calculate_speed(distance_calib, framerate):
    # calculate the speed in mm/second
    speed = distance_calib/(1.0/framerate)  # --> distance * framerate
    retval = speed
    return retval


def find_conversion_factor_for_spider(filename):
    # calibrate distance: convert px to mm:
    # dictionary: Spider (Lxx,Lyy):factor in px/mm
    conversion_factors = {(62, 76): 2.57,
                          (77, 91): 2.56,
                          (92, 111): 2.58,
                          (112, 126): 2.58}
    spidername = filename.split(sep="_")[0]
    spidernumber = int(''.join(list(filter(str.isdigit, spidername))))
    #print(f"spidername: {spidername}, spidernumber: {spidernumber}")

    conv_fac = np.nan
    for i in range(len(conversion_factors.keys())):
        key = list(conversion_factors.keys())[i]
        if spidernumber in range(key[0], key[1]):  # assign correct converion factor to spider
            conv_fac = conversion_factors[key]
            #print(f"spidernumber: {spidernumber}, conv_fac: {conv_fac}")

    if conv_fac == np.nan:
        print(f"no conversion factor was found for this spidernumber: {spidernumber}")
        conv_fac = 1.0

    return conv_fac


def strip_scorer_column_counter(data, scorer):
    print("stripping")
    # TODO: strip .Number from scorer in data frame header...
    print(data.keys())
    data.loc['scorer'] = scorer
    #The following j for loop accesses the correct values, but not possible to replace
    # for j in range(2, len(data.columns)-2):
    #     print(data.columns)
    #     print(data.columns[j][0])
    #     data.columns[j][0] = data.columns[1][0]

    # for i in range(2, len(data.columns)-2):
    #     data.rename(columns={''})
    #     print("2:", data.columns[2][0])     # column, row
    #     print("pre: ", data.columns[i][0])
    #     print(data.columns[i][0].rsplit("."))
    #     print("data.iloc[0, i]: ", data.iloc[0, i])
    #     data.iloc[i, 0] = data.columns[i][0].rsplit(".")[0]
    #     print("post: ",  data.columns[i][0].rsplit(".")[0])
    return


def calculate_speed(distance_calib, framerate):
    # calculate the speed in mm/second
    speed = distance_calib/(1.0/framerate)  # --> distance * framerate
    retval = speed
    return retval


def estimate_TCOM_label_coords(list_tail_a_x_coords, list_tail_a_y_coords, list_tail_b_x_coords, list_tail_b_y_coords):
    """
    takes the x coordinates and y coordinates of the TAIL_A and TAIL_B label of the interval of interest and
    estimates the tailCOM label position in the middle between the two
    :param list_tail_a_x_coords:
    :param list_tail_b_x_coords:
    :return: list with x values for TCOM and list with y values for TCOM
    """
    list_tcom_x_coords = []
    list_tcom_y_coords = []

    print(len(list_tail_a_x_coords),
          len(list_tail_a_y_coords),
          len(list_tail_b_x_coords),
          len(list_tail_b_y_coords))

    if (len(list_tail_a_x_coords) > 0 and len(list_tail_a_y_coords) > 0 and len(list_tail_b_x_coords) > 0 and len(list_tail_b_y_coords) > 0):
        # 1) check which way lizard is going --> which of the labels x-coordinates is bigger
        if list_tail_a_x_coords[0] >= list_tail_b_x_coords[0]:
            cond_right = True
            cond_left = False
        elif list_tail_a_x_coords[0] < list_tail_b_x_coords[0]:
            cond_left = True
            cond_right = False
        # 2) for every entry in list (frame) do: x_tcom = x+((x2-x)/2) and same for y if lizards climbs/runs up/right and
        # x_tcom = x2+((x-x2)/2) and same for y if lizard climbs/runs down/left

        for coord_xA, coord_xB in zip(list_tail_a_x_coords, list_tail_b_x_coords):
            if cond_right:
                tcom_x = coord_xB + ((coord_xA - coord_xB) / 2.0)
            elif cond_left:
                tcom_x = coord_xA + ((coord_xB - coord_xA) / 2.0)
            list_tcom_x_coords.append(tcom_x)
        for coord_yA, coord_yB in zip(list_tail_a_y_coords, list_tail_b_y_coords):
            if coord_yA < coord_yB:
                tcom_y = coord_yA + ((coord_yB - coord_yA) / 2.0)
            elif coord_yB <= coord_yA:
                tcom_y = coord_yB + ((coord_yA - coord_yB) / 2.0)
            list_tcom_y_coords.append(tcom_y)

    return list_tcom_x_coords, list_tcom_y_coords


def rmsValue(array):
    """
    takes an array of values and calculates the RMS value, which is defined as the square root of the arithmetic
    mean of the squares of the values.
    """
    import math

    n = len(array)

    square = 0
    mean = 0.0
    root = 0.0

    # Calculate square
    for i in range(0, n):
        if np.isnan(array[i]) == False:
            square += (array[i] ** 2)
        else:
            square += 0.0

    # Calculate Mean
    mean = (square / float(n))

    # Calculate Root
    root = math.sqrt(mean)

    return root
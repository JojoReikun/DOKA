"""
LizardDLCAnalysis Toolbox
© Jojo S.
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
    clicked:
    distance_limit: 
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


def py_angle_betw_2vectors(v1, v2):
    import numpy.linalg as la
    """Returns the angle in degrees between vectors 'v1' and 'v2'"""
    cosang = np.dot(v1, v2) / (la.norm(v1) * la.norm(v2))
    # sinang = la.norm(np.cross(v1, v2))
    # return math.degrees(np.arctan2(sinang, cosang))
    return np.rad2deg(np.arccos(cosang))


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


def calculate_gravity_deflection_angle(bodyaxis):
    # TODO: add option to use  data from separate gravity file here
    gravity_axis = (100., 0.)
    angle_deflection = py_angle_betw_2vectors(gravity_axis, bodyaxis)
    return angle_deflection


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






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


"""Handle a user function which is defined as directory entry"""

class UserFunc():
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

    def __init__(self, module_name=None, func_name=None, func_arg=None):

        try:
            self.module = import_module(module_name)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(f'Module {module_name} not found!')
        self.func_name = func_name
        self.func_arg = func_arg

    def __call__(self, func_arg=None):
        func = getattr(self.module, self.func_name)
        if func_arg is None:
            func_arg = self.func_arg
        if func_arg is None:
            retval = func()
        else:
            retval = func(func_arg)
        return retval



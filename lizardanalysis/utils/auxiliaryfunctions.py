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


def create_config_template():
    """
    Creates a template for config.yaml file. This specific order is preserved while saving as yaml file.
    """
    import ruamel.yaml
    yaml_str = """\
# Project definitions (do not edit!)
    Task:
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

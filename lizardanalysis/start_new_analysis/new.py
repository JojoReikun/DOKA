"""
LizardDLCAnalysis Toolbox
© Jojo S.
Licensed under MIT License
"""

import os
from pathlib import Path
import shutil
from lizardanalysis import DEBUG


def create_new_project(project, experimenter, species, file_directory, working_directory=None, filetype='.csv'):
    """Creates a new project directory, sub-directories and a basic configuration file. The configuration file is loaded with the default values. Change its parameters to your projects need.

    Parameters
    ----------
    project : string
        String containing the name of the project.

    experimenter : string
        String containing the name of the experimenter.

    species : string
        String containing the name of the species analyzed.

    file_directory : string
        String containing the full path of the folder containing the DLC result files (.csv) to include in the project.

    working_directory : string, optional
        The directory where the project will be created. The default is the ``current working directory``; if provided, it must be a string.

     Example
    --------
    >>> lizardanalysis.create_new_project('gecko_DLC_analysis','Jojo','GekkoGecko',r'C:\yourusername\Documents\DeepLabCut\geckos\DLC_result_files\')
    Users must format paths with either:  r'C:\ OR 'C:\\ <- i.e. a double backslash \ \ )
    """

    from datetime import datetime as dt
    from lizardanalysis.utils import auxiliaryfunctions

    date = dt.today()
    month = date.strftime("%B")
    day = date.day
    d = str(month[0:3] + str(day))
    date = dt.today().strftime('%Y-%m-%d')
    if working_directory == None:
        working_directory = '.'
    wd = Path(working_directory).resolve()
    project_name = '{pn}-{exp}-{spec}-{date}'.format(pn=project, exp=experimenter, spec=species, date=date)
    project_path = wd / project_name

    # Create project and sub-directories
    if not DEBUG and project_path.exists():
        print('Project "{}" already exists!'.format(project_path))
        return
    file_path = project_path / 'files'
    results_path = project_path / 'analysis-results'
    for p in [file_path, results_path]:
        p.mkdir(parents=True)
        print('Created "{}"'.format(p))

    # Import all videos in a folder then make it a list.
    if isinstance(file_directory, str):
        if os.path.isdir(file_directory):  # it is a path!
            path = file_directory
            files = [os.path.join(path, vp) for vp in os.listdir(path) if filetype in vp]
            if len(files) == 0:
                print("No files found in", path, os.listdir(path))
                print("Perhaps change the filetype, which is currently set to:", filetype)
            else:
                print("Directory entered, ", len(files), " files were found.")

    # --- copy the csv files to project folder
    # destinations = [file_path.joinpath(vp.name) for vp in files]
    destinations = [file_path.joinpath(os.path.basename(vp)) for vp in files]
    print("Copying the files")
    for src, dst in zip(files, destinations):
        shutil.copy(os.fspath(src), os.fspath(dst))  # https://www.python.org/dev/peps/pep-0519/
        #(for windows)
        # try:
        #    #shutil.copy(src,dst)
        # except OSError or TypeError: #https://github.com/AlexEMG/DeepLabCut/issues/105 (for windows)
        #    shutil.copy(os.fspath(src),os.fspath(dst))

    files = destinations  # the *new* file location should be added to the config file
    number_of_files = len(files)

    # adds the video list to the config.yaml file
    file_sets = {}
    for file in files:
        i = 1
        print(file)
        try:
            # For windows os.path.realpath does not work and does not link to the real video. [old: rel_video_path = os.path.realpath(video)]
            rel_file_path = str(Path.resolve(Path(file)))
        except:
            rel_file_path = os.readlink(str(file))
        file_sets[rel_file_path] = {'file_number': ', '.join(map(str, str(i)))}
        i += 1

    # Set values to config file:
    cfg_file, ruamelFile = auxiliaryfunctions.create_config_template()
    cfg_file
    cfg_file['Task'] = project
    cfg_file['scorer'] = experimenter
    cfg_file['species'] = species
    cfg_file['file_sets'] = file_sets
    cfg_file['project_path'] = str(project_path)
    cfg_file['date'] = d
    cfg_file['dotsize'] = 10  # for plots size of dots
    cfg_file['alphavalue'] = 1.0  # for plots transparency of markers
    cfg_file['colormap'] = 'jet'  # for plots type of colormap

    projconfigfile = os.path.join(str(project_path), 'config.yaml')

    # Write dictionary to yaml config file
    auxiliaryfunctions.write_config(projconfigfile, cfg_file)

    print('Generated "{}"'.format(project_path / 'config.yaml'))
    print(
        "\nA new project with name %s is created at %s and a configurable file (config.yaml) is stored there. "
        "Now go and add the >>Experiment details<< and >>Camera settings<< in this file to adapt to your project's "
        "needs.\n Once you have changed the configuration file, use the function read_in_files(config)\n. " % (
            project_name, str(wd)))
    return projconfigfile



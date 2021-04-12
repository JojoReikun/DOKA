# ClimbingLizardDLCAnalysis
This software tool is being developed for making multi-species comparison easier and to facilitate kinematic analyses for many individuals. 
It is designed to take the tracked data from DeepLabCut (csv output files) as input and then automatically perform species-independent kinematic calculations.
Tracked data with the same file formatting as the DLC outputs can also be used.
It is currently set-up to work for 4 different animals (even with different number of legs): Lizards, Spiders, Ants and Stickinsects.
The software structure was built to make it easy to adjust the kinematic analysis to individual needs and allows to easily add new calculations as their own python scripts, which can then be executed as part of the analysis.

## A few features of this script in keynotes:
- works for 4 groups of animals (from top-view) so far: Lizards, Spiders, Ants, and Stickinsects
- works species independent and therefore facilitates multi-species analyses
- easy to add new calculations
- GUI or command line input (cli)
- so far allows a maximum of certain pre-defined labels per animal, but functionality to add own marker positions in GUI will be added soon.
- label names don't matter, they can be reconfigured to match defaults in the GUI
- we are working on more features!!

A **GUI** is now available to make the use of this program easier:

![](DOKA_gui_docu.jpg)

A) Select the animal you want to analyse. If your animal is not included, you can either include it yourself, or message us and we will see waht we can do.
Once the animal is selected the responding silhouette and the default labels appear in the big window.

B) An existing project config.yaml can be loaded. Or a new project can be created. 

C) Once an existing project is confirmed, the number of files and the available labels will be displayed. Available labels appear green. If your label name does not match the default name, they appear grey, but label names can be reconfigured --> D
A log tells you what to do or what was done by the software.

D) Displays default, non-available, and available labels in a visual way. By clicking on the label in this window, a pop-up window appears which allows you to choose one of the default label names for that label. The name will be adjusted and thereby recognized by the software. 
In future the option to add your own labels on the animal will be included. These can then be used in your own calculations. Currently that would have to be done "behind the scenes" in the code.

E) Displays all for that animal existing calculations and marks all available calculations (determined by which labels are there/green) in green.
In future instead of executing all green calculations, the desired ones will be selectable/deselectable.

## Overview over the programstructure:
This chart displays th eprogram structure, how calculations or even animals could be added and where which functionality can be found.
![](images/Program_structure_chart.jpg)


## Overview over the basic program flow:
For any animal the basic program flow looks like this:

![](images/DLC_analysis_script_flowchart.jpg)

The process_file() function is called for every file included in the project (every DLC output csv), which loops through 
all available calculations. For some calculations the knowledge about the step-phases is essential. Therefore a 
step detection algorithm using rel. feet to body velocities is implemented.
Some kinematic parameters that can be calculated for lizards are shown below:

![](images/KinematicCalculations.jpg)

## Platforms:
DOKA is generally functional across platforms. It has been mainly developed on Windows 10 64-bit, but also tested on linux ubuntu (v: ), and iOS (v: )

## Install

git clone git@github.com:JojoReikun/ClimbingLizardDLCAnalysis.git

To run the project on Ubuntu, you need to install Pillow and TKinter:
```
sudo apt-get update
sudo apt-get install python3-tk python3-pil python3-pil.imagetk
```


## Run OVERVIEW
Works in the Pycharm (JetBrains) console. Alternatively DOKA.py can be executed and a gui will open, which includes generation of a new project, label definitions, and kinematic calculations. 'Lizardanalysis' is supposed to be a click program executable via anaconda console, but it hasn't been tested yet.
```
>> import lizardanalysis
>> path_to_csv = r'path to input csv files'
>> args = {'project': 'project_name',
           'experimenter': 'your name',
           'species': 'investigated species',
           'file_directory': path_to_csv }
```
change framerate and shutterspeed in config.yaml
```
>> lizardanalysis.create_new_project(**args)
>> config = r'path_to_config.yaml'
```
all arguments other than config are _optional_. The default values which will be passed if not set otherwise are displayed here.
```
>> lizardanalysis.analyze_files(config, likelihood=0.90)
>> lizardanalysis.summarize_results(config, plotting=False, direction_filter=True)
```

---
## Run DETAIL for cli:

open python console in Pycharm

**1st)** import toolbox lizardanalysis: 
```
>> import lizardanalysis
```
---
**2nd)** define variables to pass in args dictionary {key:value, key2:value2, ...}:  
* project: choose any project name
* experimenter: the name of the person who is running the project = you ;)
* species: enter the species name. If multiple either put them all in one string or name a group
* file_directory: filepath to the file directory which contains all csv output files from DeepLabCut.\
(__If on Windows:__ put r' ' aroud the path)

(can also be done in function call, if you want to do that skip step 2)  
_obviously:_ replace values of dictionaries (e.g. "project_name") with your inputs
```
>> path_to_csv = r'path to input csv files'
>> args = {'project': 'project_name',
           'experimenter': 'your name',
           'species': 'investigated species',
           'file_directory': path_to_csv }
```
---
**3rd)** call function to create a new project:  
--> if you did step 2, just pass the arguments to the function like this:
```
>> lizardanalysis.create_new_project(**args)
```
--> if you skipped step 2, call the function and pass the arguments inside the call:
```
>> lizardanalysis.create_new_project('project_name', 'your name', 'investigated species', path_to_csv)
```
*example:*\
 lizardanalysis.create_new_project('geckos', 'jojo', 'hemidactylusFrenatus', r'C:\Users\JojoS\Documents\phd\ClimbingRobot_XGen4\ClimbingLizardDLCAnalysis\all_csv')

---
**!!!If you have just created the project and this is the first time you analyze it, you have to change _framerate_ and _shutterspeed_ in the config.yaml file**!!!

**4th)** call function to analyze all the csv files.\
you can either define the config path as a variable beforehand or just pass the path in the function call
```
>> config = r'path_to_config.yaml'
```
*example:*\
config = r'C:\Users\JojoS\Documents\phd\ClimbingRobot_XGen4\ClimbingLizardDLCAnalysis\geckos-jojo-hemidactylusFrenatus-2020-04-16\config.yaml'

now call the function to start the analysis:
```
>> lizardanalysis.analyze_files(config)
```
There is an optional argument you can pass in this function: likelihood (default = 0.90).
This determines the likelihood limit, so that labels with a likelihood below will be set to NaN values in results 
and not included in calculations. If you want to pass this, the function looks like this:
```
>> lizardanalysis.analyze_files(config, likelihood=0.95)
```

---
**5th)** call function to summarize all results species-wise.

**-- This is still "work in progress", please wait for updates! --**
* plotting (bool): If True this generates speecies-wise overview plots
* direction_filter (bool): If True the species-wise results will also be seperated by direction
```
>> lizardanalysis.summarize_results(config, plotting=False, direction_filter=True)
```

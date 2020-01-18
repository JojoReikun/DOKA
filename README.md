# ClimbingLizardDLCAnalysis

## Install

git clone git@github.com:JojoReikun/ClimbingLizardDLCAnalysis.git

To run the project on Ubuntu, you need to install Pillow and TKinter:
````
sudo apt-get update
sudo apt-get install python3-tk python3-pil python3-pil.imagetk
````

## Run

open python console in main directory
````
>> import lizardanalysis
>> path_to_csv = r'path to input csv files'
>> args = {'project': 'project_name',
           'experimenter': 'your name',
           'species': 'investigated species',
           'file_directory': path_to_csv }
>> lizardanalysis.create_new_project(**args)
>> config = r'path_to_config.yaml'
>> lizardanalysis.read_csv_files(config)
````


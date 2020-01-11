# ClimbingLizardDLCAnalysis

## Install

git clone git@github.com:JojoReikun/ClimbingLizardDLCAnalysis.git

## Run

open python console in main directory
````
>> import lizardanalysis
>> project = r'path_to_project_data'
>> path_to_output = r'path for output files'
>> args = {'project': project,
           'experimentor': 'your name',
           'species': 'investigated species',
           'file_directory': path_to_output }
>> lizardanalysis.create_new_project(**args)
>> config = r'path_to_config.yaml'
>> lizardanalysis.read_csv_files(config)
````


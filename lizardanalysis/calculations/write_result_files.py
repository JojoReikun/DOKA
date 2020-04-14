# TODO: Needed results:
#           - GENERAL
#               - species, videoname, all individual results of the calculations
#           - SUMMARY
#               - species-wise, nb of videos, up count, down count, means of all calculations

def write_summary_result_files(config):
    print('\nCREATING AND WRITING SUMMARY RESULT FILES...\n...')

    from pathlib import Path
    import os
    import errno
    import glob
    from collections import Counter

    current_path = os.getcwd()
    config_file = Path(config).resolve()
    project_path = os.path.split(config_file)[0]

    result_file_path = os.path.join(current_path, project_path, "analysis-results")
    print('result filepath: ', result_file_path)

    try:
        os.makedirs(os.path.join(result_file_path, "analysis-summary"))
        print("folder for summary result files created")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    filelist = glob.glob(os.path.join(result_file_path, "*.csv"))
    filelist_split = [x.rsplit(os.sep, 1)[1] for x in filelist]
    print(" + ", len(filelist_split), *filelist_split, sep='\n + ')

    # ----------------------------------------------------------------------------------------------------------
    # options: sort by species, and optional by direction
    filter = {'species': True, 'direction': False}

    # loop through all individual result files to generate summary
    speciesnames = []
    for file in filelist_split:
        speciesname = species_name_split(file)
        speciesnames.append(speciesname[0])         # extracts first bit of filename until first number for species name
    print(speciesnames)
    speciescount = dict(Counter(speciesnames))    # unique species names & count
    print("species summary: ", speciescount)

    # create one class instance for every species to calculate individual summaries
    class_dict = {}
    results = {}
    for species in speciescount.keys():
        #one class instance for very species
        class_dict[species] = species_summary(filter, species, filelist_split, result_file_path, filelist)
        print(str(class_dict[species]))

        # store results species wise
        #test:
        class_dict[species].summarize_species()
        # results[species][row] = class_dict[species].summarize_species()

    # create overview plots and show in grid at the end

    print('\n \nDONE!!!')




class species_summary:

    def __init__(self, filter, speciesname, filelist_split, result_file_path, filelist):
        self.species_filter = filter['species']
        self.direction_filter = filter['direction']
        self.result_path = result_file_path
        self.name = speciesname
        self.filelist_split_filtered = [file for file in filelist_split if speciesname in file] # contains file names
        self.filelist_filtered = [file for file in filelist if speciesname in file] # contains file paths

    def __str__(self):
        return "\n\nClass: {}\n" \
               "The filtered split filelist is: \n{}".format(self.name, self.filelist_split_filtered)

    def mean_deflection(self):
        return

    def summarize_species(self):
        import pandas as pd
        import os
        import numpy as np
        from statistics import mean, stdev

        retval = {}

        direction_up_counter = 0
        direction_down_counter = 0
        deflection_species = []
        speed_species = []

        # >>>>> read in all csv files belonging to the species:
        for file in self.filelist_filtered:
            data = pd.read_csv(os.path.join(self.result_path, file), sep=',')
            #print(data.head())
            data.rename(columns=lambda x: x.strip(), inplace=True)  # remove whitespaces from column names

            # direction ---------------------------------------------------------- :
            direction = direction_encode_and_strip(data['direction_of_climbing'][1])
            if direction == "UP":
                direction_up_counter += 1
            elif direction == "DOWN":
                direction_down_counter += 1
            else:
                pass

            # deflection ---------------------------------------------------------- :
            deflection_species.append(list(data['body_deflection_angle']))

            # speed --------------------------------------------------------------- :
            speed_species.append(list(data['speed_PXperS']))

        # >>>>> mean and stds:
        # deflection ---------------------------------------------------------- :
        deflection_species_flattened = [element for sublist in deflection_species for element in sublist]
        deflection_species_mean = np.nanmean(deflection_species_flattened)
        deflection_species_std = np.nanstd(deflection_species_flattened)
        # speed --------------------------------------------------------------- :
        speed_species_flattened = [element for sublist in speed_species for element in sublist]
        speed_species_mean = np.nanmean(speed_species_flattened)
        speed_species_std = np.nanstd(speed_species_flattened)

        # >>>>> TEST PRINTS:
        print("UP: {} | DOWN: {} ".format(direction_up_counter, direction_down_counter))
        print("deflection mean: {0:.2f} ".format(deflection_species_mean),
              "deflection std: {0:.2f}".format(deflection_species_std),
              "\nspeed mean: {0:.2f} ".format(speed_species_mean),
              "speed std: {0:.2f}".format(speed_species_std))

        return


def species_name_split(s):
    import re
    splitstring = re.split(r'(\d+)', s)
    #print(splitstring)
    return splitstring


def direction_encode_and_strip(bytestring):
    # get rid of b"..." for direction
    if "UP" in bytestring:
        direction = "UP"
    elif "DOWN" in bytestring:
        direction = "DOWN"
    else:
        print("no known direction found")
        direction = "UNKNOWN"
    return direction

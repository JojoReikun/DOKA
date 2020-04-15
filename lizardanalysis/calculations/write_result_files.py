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
    #print(" + ", len(filelist_split), *filelist_split, sep='\n + ')

    # ----------------------------------------------------------------------------------------------------------
    # options: sort by species, and optional by direction
    filter = {'species': True, 'direction': True}

    # loop through all individual result files to generate summary
    speciesnames = []
    for file in filelist_split:
        speciesname = species_name_split(file)
        speciesnames.append(speciesname[0])         # extracts first bit of filename until first number for species name
    #print(speciesnames)
    speciescount = dict(Counter(speciesnames))    # unique species names & count
    print("species summary: ", speciescount)

    # create one class instance for every species to calculate individual summaries
    class_dict = {}
    results = {}
    dict_list = []
    for species in speciescount.keys():
        #one class instance for very species
        class_dict[species] = species_summary(filter, species, filelist_split, result_file_path, filelist)
        print(str(class_dict[species]))

        # store plot lists species wise:
        species_dict = class_dict[species].store_species_plot_lists()
        dict_list.append(species_dict)
        print(species_dict)

        # print overview results species wise:
        #test:
        class_dict[species].summarize_species()
        # results[species][row] = class_dict[species].summarize_species()

    # create overview plots and show in grid at the end
    # merge the dict_list od species dicts into one dict
    res = merge_dicts(dict_list)
    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in res.items()) + "}")

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

    def store_species_plot_lists(self):
        import pandas as pd
        import os

        species_dict = {}   # {'species': {'wrist_fore':[a, b, c], 'wrist_hind':[d,e,f], ... }}
        species_plot = {}

        # reads in first result csv file to get all column names
        data = pd.read_csv(os.path.join(self.result_path, self.filelist_filtered[1]), sep=',')
        data.rename(columns=lambda x: x.strip(), inplace=True)  # remove whitespaces from column names
        column_name_list = [col for col in data.columns]

        # defines categories to be extracted from results and requirements of string bits to appear in columnnames
        # values: first string in list is a must exist + either the second or the third must be included
        category = {'wrist_fore': ['wrist', 'FL', 'FR'],
                    'wrist_hind': ['wrist', 'HR', 'HL']}
        category_columnnames = {}

        # gets the real column names for categories, so respective data can be pulled from data frame
        for key in list(category.keys()):
            # looks for the matching column names in the data which contain the string bits defined in category dict
            names = [column for column in column_name_list if category[key][0] in column
                     and (category[key][1] in column or category[key][2] in column)]
            category_columnnames[key] = names
        #print(category_columnnames)

        for file in self.filelist_filtered:
            tmp_species = []
            data = pd.read_csv(os.path.join(self.result_path, file), sep=',')
            data.rename(columns=lambda x: x.strip(), inplace=True)  # remove whitespaces from column names
            for key in list(category_columnnames.keys()):
                tmp = []
                for name in category_columnnames[key]:
                    tmp.append(list(data[name]))
                tmp = [element for sublist in tmp for element in sublist] # flatten list so all values for key are in 1
                #print(tmp)
                species_plot[key] = tmp

        #print(species_plot)
        species_dict[self.name] = species_plot

        return species_dict

    def sformat(self, label, value, stdvalue=None, numformat=None):
        if stdvalue is not None:
            numformat = numformat if numformat else 'f'
            stdstring = ("({:" + numformat + "})").format(stdvalue)
        else:
            stdstring = ""
        if numformat is None:
            return f"{label}: {value} {stdstring}"
        else:
            return ("{}: {:" + numformat + "} {}").format(label, value, stdstring)

    def sprint(self, label1, value1, stdvalue1, label2, value2, stdvalue2, slen=64, format=None):
        s1 = ("{:<" + str(slen) + "}").format(self.sformat(label1, value1, stdvalue1, format))
        s2 = ("{:<" + str(slen) + "}").format(self.sformat(label2, value2, stdvalue2, format))
        return s1 + " | " + s2

    def summarize_species(self):
        import pandas as pd
        import os
        import numpy as np

        retval = {}
        toe_angles = False

        direction_up_counter = 0
        direction_down_counter = 0
        deflection_species_UP = []
        deflection_species_DOWN = []
        speed_species_UP = []
        speed_species_DOWN = []
        wrist_angles_fore_UP = []
        wrist_angles_fore_DOWN = []
        wrist_angles_hind_UP = []
        wrist_angles_hind_DOWN = []
        limb_ROM_fore_UP = []
        limb_ROM_fore_DOWN = []
        limb_ROM_hind_UP = []
        limb_ROM_hind_DOWN = []
        spine_ROM_UP = []
        spine_ROM_DOWN = []
        CROM_fore_UP = []
        CROM_fore_DOWN = []
        CROM_hind_UP = []
        CROM_hind_DOWN = []
        toe_angle_sum_UP = []
        toe_angle_sum_DOWN = []

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


            if direction == "UP":
                # deflection ---------------------------------------------------------- :
                deflection_species_UP.append(list(data['body_deflection_angle']))
                # speed --------------------------------------------------------------- :
                speed_species_UP.append(list(data['speed_PXperS']))
                # wrist angles -------------------------------------------------------- :
                wrist_angles_fore_UP.append(list(data['mid_stance_wrist_angles_mean_FL']))
                wrist_angles_fore_UP.append(list(data['mid_stance_wrist_angles_mean_FR']))
                wrist_angles_hind_UP.append(list(data['mid_stance_wrist_angles_mean_HL']))
                wrist_angles_hind_UP.append(list(data['mid_stance_wrist_angles_mean_HR']))
                # limb ROM ------------------------------------------------------------ :
                limb_ROM_fore_UP.append(list(data['limbROM_FL']))
                limb_ROM_fore_UP.append(list(data['limbROM_FR']))
                limb_ROM_hind_UP.append(list(data['limbROM_HR']))
                limb_ROM_hind_UP.append(list(data['limbROM_HL']))
                # spine ROM ----------------------------------------------------------- :
                spine_ROM_UP.append(list(data['spineROM_FL']))
                spine_ROM_UP.append(list(data['spineROM_FR']))
                spine_ROM_UP.append(list(data['spineROM_HR']))
                spine_ROM_UP.append(list(data['spineROM_HL']))
                # CROM ---------------------------------------------------------------- :
                CROM_fore_UP.append(list(data['CROM_FL']))
                CROM_fore_UP.append(list(data['CROM_FR']))
                CROM_hind_UP.append(list(data['CROM_HR']))
                CROM_hind_UP.append(list(data['CROM_HL']))
                if toe_angles == True:
                    # toe angle sum ------------------------------------------------------- :
                    toe_angle_sum_UP.append(list(data['fl_ti-fl_ti1']))
                    toe_angle_sum_UP.append(list(data['fl_ti1-fl_to1']))
                    toe_angle_sum_UP.append(list(data['fl_to1-fl_to']))
                    toe_angle_sum_UP.append(list(data['fr_ti-fr_ti1']))
                    toe_angle_sum_UP.append(list(data['fr_ti1-fr_to1']))
                    toe_angle_sum_UP.append(list(data['fr_to1-fr_to']))

            else:
                # deflection ---------------------------------------------------------- :
                deflection_species_DOWN.append(list(data['body_deflection_angle']))
                # speed --------------------------------------------------------------- :
                speed_species_DOWN.append(list(data['speed_PXperS']))
                # wrist angles -------------------------------------------------------- :
                wrist_angles_fore_DOWN.append(list(data['mid_stance_wrist_angles_mean_FL']))
                wrist_angles_fore_DOWN.append(list(data['mid_stance_wrist_angles_mean_FR']))
                wrist_angles_hind_DOWN.append(list(data['mid_stance_wrist_angles_mean_HL']))
                wrist_angles_hind_DOWN.append(list(data['mid_stance_wrist_angles_mean_HR']))
                # limb ROM ------------------------------------------------------------ :
                limb_ROM_fore_DOWN.append(list(data['limbROM_FL']))
                limb_ROM_fore_DOWN.append(list(data['limbROM_FR']))
                limb_ROM_hind_DOWN.append(list(data['limbROM_HR']))
                limb_ROM_hind_DOWN.append(list(data['limbROM_HL']))
                # spine ROM ----------------------------------------------------------- :
                spine_ROM_DOWN.append(list(data['spineROM_FL']))
                spine_ROM_DOWN.append(list(data['spineROM_FR']))
                spine_ROM_DOWN.append(list(data['spineROM_HR']))
                spine_ROM_DOWN.append(list(data['spineROM_HL']))
                # CROM ---------------------------------------------------------------- :
                CROM_fore_DOWN.append(list(data['CROM_FL']))
                CROM_fore_DOWN.append(list(data['CROM_FR']))
                CROM_hind_DOWN.append(list(data['CROM_HR']))
                CROM_hind_DOWN.append(list(data['CROM_HL']))
                if toe_angles == True:
                    # toe angle sum ------------------------------------------------------- :
                    toe_angle_sum_DOWN.append(list(data['hl_ti-hl_ti1']))
                    toe_angle_sum_DOWN.append(list(data['hl_ti1-hl_to1']))
                    toe_angle_sum_DOWN.append(list(data['hl_to1-hl_to']))
                    toe_angle_sum_DOWN.append(list(data['hr_ti-hr_ti1']))
                    toe_angle_sum_DOWN.append(list(data['hr_ti1-hr_to1']))
                    toe_angle_sum_DOWN.append(list(data['hr_to1-hr_to']))


        # >>>>> mean and stds:
        # TODO: surely there is a better way to do this :)
        # deflection ---------------------------------------------------------- :
        deflection_species_flattened_UP = [element for sublist in deflection_species_UP for element in sublist]
        deflection_species_mean_UP = np.nanmean(deflection_species_flattened_UP)
        deflection_species_std_UP = np.nanstd(deflection_species_flattened_UP)
        deflection_species_flattened_DOWN = [element for sublist in deflection_species_DOWN for element in sublist]
        deflection_species_mean_DOWN = np.nanmean(deflection_species_flattened_DOWN)
        deflection_species_std_DOWN = np.nanstd(deflection_species_flattened_DOWN)
        # speed --------------------------------------------------------------- :
        speed_species_flattened_UP = [element for sublist in speed_species_UP for element in sublist]
        speed_species_mean_UP = np.nanmean(speed_species_flattened_UP)
        speed_species_std_UP = np.nanstd(speed_species_flattened_UP)
        speed_species_flattened_DOWN = [element for sublist in speed_species_DOWN for element in sublist]
        speed_species_mean_DOWN = np.nanmean(speed_species_flattened_DOWN)
        speed_species_std_DOWN = np.nanstd(speed_species_flattened_DOWN)
        # wrist angles -------------------------------------------------------- :
        wrist_angles_fore_flattened_UP = [element for sublist in wrist_angles_fore_UP for element in sublist]
        wrist_angles_hind_flattened_UP = [element for sublist in wrist_angles_hind_UP for element in sublist]
        wrist_angles_fore_mean_UP = np.nanmean(wrist_angles_fore_flattened_UP)
        wrist_angles_fore_std_UP = np.nanstd(wrist_angles_fore_flattened_UP)
        wrist_angles_hind_mean_UP = np.nanmean(wrist_angles_hind_flattened_UP)
        wrist_angles_hind_std_UP = np.nanstd(wrist_angles_hind_flattened_UP)
        wrist_angles_fore_flattened_DOWN = [element for sublist in wrist_angles_fore_DOWN for element in sublist]
        wrist_angles_hind_flattened_DOWN = [element for sublist in wrist_angles_hind_DOWN for element in sublist]
        wrist_angles_fore_mean_DOWN = np.nanmean(wrist_angles_fore_flattened_DOWN)
        wrist_angles_fore_std_DOWN = np.nanstd(wrist_angles_fore_flattened_DOWN)
        wrist_angles_hind_mean_DOWN = np.nanmean(wrist_angles_hind_flattened_DOWN)
        wrist_angles_hind_std_DOWN = np.nanstd(wrist_angles_hind_flattened_DOWN)
        # limb ROM ------------------------------------------------------------ :
        limb_ROM_fore_flattened_UP = [element for sublist in limb_ROM_fore_UP for element in sublist]
        limb_ROM_hind_flattened_UP = [element for sublist in limb_ROM_hind_UP for element in sublist]
        limb_ROM_fore_mean_UP = np.nanmean(limb_ROM_fore_flattened_UP)
        limb_ROM_fore_std_UP = np.nanstd(limb_ROM_fore_flattened_UP)
        limb_ROM_hind_mean_UP = np.nanmean(limb_ROM_hind_flattened_UP)
        limb_ROM_hind_std_UP = np.nanstd(limb_ROM_hind_flattened_UP)
        limb_ROM_fore_flattened_DOWN = [element for sublist in limb_ROM_fore_DOWN for element in sublist]
        limb_ROM_hind_flattened_DOWN = [element for sublist in limb_ROM_hind_DOWN for element in sublist]
        limb_ROM_fore_mean_DOWN = np.nanmean(limb_ROM_fore_flattened_DOWN)
        limb_ROM_fore_std_DOWN = np.nanstd(limb_ROM_fore_flattened_DOWN)
        limb_ROM_hind_mean_DOWN = np.nanmean(limb_ROM_hind_flattened_DOWN)
        limb_ROM_hind_std_DOWN = np.nanstd(limb_ROM_hind_flattened_DOWN)
        # spine ROM ------------------------------------------------------------ :
        spine_ROM_flattened_UP = [element for sublist in spine_ROM_UP for element in sublist]
        spine_ROM_flattened_DOWN = [element for sublist in spine_ROM_DOWN for element in sublist]
        spine_ROM_mean_UP = np.nanmean(spine_ROM_flattened_UP)
        spine_ROM_std_UP = np.nanstd(spine_ROM_flattened_UP)
        spine_ROM_mean_DOWN = np.nanmean(spine_ROM_flattened_DOWN)
        spine_ROM_std_DOWN = np.nanstd(spine_ROM_flattened_DOWN)
        # CROM ------------------------------------------------------------ :
        CROM_fore_flattened_UP = [element for sublist in CROM_fore_UP for element in sublist]
        CROM_hind_flattened_UP = [element for sublist in CROM_hind_UP for element in sublist]
        CROM_fore_mean_UP = np.nanmean(CROM_fore_flattened_UP)
        CROM_fore_std_UP = np.nanstd(CROM_fore_flattened_UP)
        CROM_hind_mean_UP = np.nanmean(CROM_hind_flattened_UP)
        CROM_hind_std_UP = np.nanstd(CROM_hind_flattened_UP)
        CROM_fore_flattened_DOWN = [element for sublist in CROM_fore_DOWN for element in sublist]
        CROM_hind_flattened_DOWN = [element for sublist in CROM_hind_DOWN for element in sublist]
        CROM_fore_mean_DOWN = np.nanmean(CROM_fore_flattened_DOWN)
        CROM_fore_std_DOWN = np.nanstd(CROM_fore_flattened_DOWN)
        CROM_hind_mean_DOWN = np.nanmean(CROM_hind_flattened_DOWN)
        CROM_hind_std_DOWN = np.nanstd(CROM_hind_flattened_DOWN)
        if toe_angles:
            # toe angle sum ------------------------------------------------------- :
            toe_angle_sum_UP = [element for sublist in toe_angle_sum_UP for element in sublist]
            toe_angle_sum_DOWN = [element for sublist in toe_angle_sum_DOWN for element in sublist]
            toe_angle_sum_mean_UP = np.nanmean(toe_angle_sum_UP)
            toe_angle_sum_std_UP = np.nanstd(toe_angle_sum_UP)
            toe_angle_sum_mean_DOWN = np.nanmean(toe_angle_sum_DOWN)
            toe_angle_sum_std_DOWN = np.nanstd(toe_angle_sum_DOWN)


        # >>>>> TEST PRINTS:
        slen = 64
        print(self.sprint('UP', direction_up_counter, None, 'DOWN', direction_down_counter, None, slen=slen, format=None))
        print(self.sprint("deflection mean UP", deflection_species_mean_UP, deflection_species_std_UP,
                          "deflection mean DOWN", deflection_species_mean_DOWN, deflection_species_std_DOWN, format='.2f'))
        print(self.sprint("speed mean UP", speed_species_mean_UP, speed_species_std_UP,
                          "speed mean DOWN", speed_species_mean_DOWN, speed_species_std_DOWN, format='.2f'))
        print(self.sprint("wrist fore mean UP", wrist_angles_fore_mean_UP, wrist_angles_fore_std_UP,
                          "wrist fore mean DOWN", wrist_angles_fore_mean_DOWN, wrist_angles_fore_std_DOWN, format='.2f'))
        print(self.sprint("wrist hind mean UP", wrist_angles_hind_mean_UP, wrist_angles_hind_std_UP,
                          "wrist hind mean DOWN", wrist_angles_hind_mean_DOWN, wrist_angles_hind_std_DOWN, format='.2f'))
        print(self.sprint("limb ROM fore mean UP", limb_ROM_fore_mean_UP, limb_ROM_fore_std_UP,
                          "limb ROM fore mean DOWN", limb_ROM_fore_mean_DOWN, limb_ROM_fore_std_DOWN, format='.2f'))
        print(self.sprint("limb ROM hind mean UP", limb_ROM_hind_mean_UP, limb_ROM_hind_std_UP,
                          "limb ROM hind mean DOWN", limb_ROM_hind_mean_DOWN, limb_ROM_hind_std_DOWN, format='.2f'))
        print(self.sprint("spine ROM mean UP", spine_ROM_mean_UP, spine_ROM_std_UP,
                          "spine ROM mean DOWN", spine_ROM_mean_DOWN, spine_ROM_std_DOWN, format='.2f'))
        print(self.sprint("CROM fore mean UP", CROM_fore_mean_UP, CROM_fore_std_UP,
                          "CROM fore mean DOWN", CROM_fore_mean_DOWN, CROM_fore_std_DOWN, format='.2f'))
        print(self.sprint("CROM hind mean UP", CROM_hind_mean_UP, CROM_hind_std_UP,
                          "CROM hind mean DOWN", CROM_hind_mean_DOWN, CROM_hind_std_DOWN, format='.2f'))

        if toe_angles:
            print("\ntoe_angle_sum mean UP: {0:.2f} ".format(toe_angle_sum_mean_UP), "toe_angle_sum std UP: {0:.2f}".format(toe_angle_sum_std_UP), " | ",
                  "toe_angle_sum mean DOWN: {0:.2f} ".format(toe_angle_sum_mean_DOWN), "toe_angle_sum std DOWN: {0:.2f}".format(toe_angle_sum_std_DOWN))

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


def merge_dicts(list_of_dictionaries):
    res = {}
    for dict in list_of_dictionaries:
        for key in dict.keys():
            res[key] = dict[key]
    return res

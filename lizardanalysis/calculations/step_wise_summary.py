def read_DOKAoutput_files(config):
    """
    All filenames should follow the pattern: ID_num_run_trialnum_direction*.csv
    If they don't, use the R script nameFixer_v2.R in LizardTails first.
    The summary file for the current DOKA project will be stored in the summary_folder in analysis_results.
    :param config:
    :return:
    """
    print('\nCREATING AND WRITING SUMMARY RESULT FILES...\n...')
    from pathlib import Path
    import os
    import errno
    import glob

    current_path = os.getcwd()
    config_file = Path(config).resolve()
    project_path = os.path.split(config_file)[0]

    result_file_path = os.path.join(current_path, project_path, "analysis-results")
    print('result filepath: ', result_file_path)
    summary_folder = os.path.join(result_file_path, "analysis-summary")

    try:
        os.makedirs(summary_folder)
        print("folder for summary result files created")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # read in all csv files in folder which contain "_run_"
    filelist = glob.glob(os.path.join(result_file_path, "*.csv"))
    filelist_split = [x.rsplit(os.sep, 1)[1] for x in filelist]
    print("Number of files found: ", len(filelist_split))
    #print(" + ", *filelist_split, sep='\n + ')

    return result_file_path, summary_folder, filelist_split, filelist


def create_tail_file(config):
    ### IMPORTS
    import pandas as pd
    from tkinter import Tk, filedialog

    root = Tk()
    root.withdraw()  # we don't want a full GUI, so keep the root window from appearing
    root.call('wm', 'attributes', '.', '-topmost', True)
    tail_filepath = filedialog.askopenfilename(parent=root, initialdir=config, title="Select tailMass file")  # show an "Open" dialog box and return the path to the selected file
    root.destroy()

    df_tailMorphs = pd.read_csv(tail_filepath)  # read in gravity file
    nrows = df_tailMorphs.shape[0]
    # create dict which matched tail values with the responding column names in tailMass.csv/df_tailMorphs
    tail_values_dict = {"SVL":"svlMM_speciesMean",
                        "tailLength":"tailLengthMM",
                        "bodyMass":"bodymass",
                        "tailMass":"tailMassEstimate",
                        "BCOMhip":"bodyCOMEstimateHip",
                        "TCOMhip":"TCOM_2"}
    id_dict = {}
    #print(list(df_tailMorphs['ID']))
    for i, id in enumerate(list(df_tailMorphs['ID'])):
        df_subsection_id = df_tailMorphs[df_tailMorphs['ID'] == id]
        #print(df_subsection_id)
        id_dict_values_dict = {}
        for tail_value, tail_column in tail_values_dict.items():
            id_dict_values_dict[tail_value] = df_subsection_id[tail_column].values[0]
        id_dict[id] = id_dict_values_dict
    #print("\n\n\n")
    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in id_dict.items()) + "}")

    return id_dict


def fill_in_tail_morphs(id_dict, species):
    species_tailMorphs_dict = id_dict[species]
    return species_tailMorphs_dict


def calculate_tail_kinematics():
    """
    calculates the tail angular amplitude, velocity and acceleration of the TCOM relative to the body axis.
    The average TCOM location of the lizards is ~30% (get correct value).
    Given that we have 4 labels along the tail (Tail_A, Tail_B, Tail_C, Tail_Tip), where A is 25% tailLength, B 50%,
    C 75% and Tip 100%, the rough TCOM label is between Tail_A and Tail_B.
    We did not use the exact TCOM position in percent to average this, because the label positions on the tail jump
    a bit during tracking.
    :return: tail_angular_amplitude, tail_angular_velocity, tail_angular_acceleration
    """




def summarize_stepwise(config):
    """
    Reads in all DOKA output files and summarizes the data step-wise in one big csv document.
    :param kwargs:
    :return:
    """
    ### IMPORTS:
    import pandas as pd
    import os
    import numpy as np
    from lizardanalysis.utils import animal_settings

    # SETUP
    feet = animal_settings.get_list_of_feet('lizard')
    stepphase_columns = ["stepphase_{}".format(foot) for foot in feet]

    print("summarizing data step wise")
    # get a list of all DOKA output files:
    result_file_path, summary_folder, filelist_split, filelist = read_DOKAoutput_files(config=config)

    # TODO: create new dataframe for step-wise combined data
    column_names = ["speciesID", "runNum", "direction", "footpair", "res_phase", "mean_body_deflection",
                    "mean_speed_PXperS",
                    "cranial_bA", "prox_bA", "tip_bA", "prox_dist", "dist_bA", "cranial_caudal",
                    "amplitude_Spine_A", "amplitude_Spine_B", "amplitude_Spine_C",
                    "amplitude_Tail_A", "amplitude_Tail_B", "amplitude_Tail_C", "amplitude_Tail_Tip",
                    "svl", "tailLength", "bodyMass", "tailMass", "BCOMhip", "TCOMhip"]
    step_wise_df = pd.DataFrame(columns=column_names)
    #print(step_wise_df)

    # create tail_file_dict which contains tail morphs for species
    id_dict = create_tail_file(config)

    # loop through every file and get...:
    for file, file_name in zip(filelist, filelist_split):
        # ... speciesID, trial, direction from the filename
        species = file_name.split("_")[0]
        speciesID = file_name.split("_")[0] + "_" + file_name.split("_")[1]
        runNum = file_name.split("_")[2] + "_" + file_name.split("_")[3]
        direction = file_name.split("_")[4]

        ### fill in tail mass, TCOM, BCOM, tailLength means per species ###
        species_tailMorphs_dict = fill_in_tail_morphs(id_dict, species)
        svl = species_tailMorphs_dict["SVL"]
        tailLength = species_tailMorphs_dict["tailLength"]
        bodyMass = species_tailMorphs_dict["bodyMass"]
        tailMass = species_tailMorphs_dict["tailMass"]
        BCOMhip = species_tailMorphs_dict["BCOMhip"]
        TCOMhip = species_tailMorphs_dict["TCOMhip"]


        ### PROCESS FILE
        print("\n========= ", speciesID, " =========")
        print(runNum, direction)

        # read in data as data frame
        df = pd.read_csv(file, index_col=0)
        #print(df.head(), "\n indices: ", df.index)

        # find all step intervals for FL|HR, and FR|HL:
        unique_steps_dict = {}
        for step_col in stepphase_columns:
            unique_steps_dict[step_col] = df[step_col].unique()
        # delete all "b'nan'" entries in dict
        for key, value_list in unique_steps_dict.items():
            unique_steps_dict[key] = list(value_list[value_list != "b'nan'"])

        #print(unique_steps_dict)

        # find phases that occure in both stepphases of one foot-pair
        FR_HL_stepphases = [i for i in unique_steps_dict['stepphase_FR'] if i in unique_steps_dict['stepphase_HL']]
        FL_HR_stepphases = [i for i in unique_steps_dict['stepphase_FL'] if i in unique_steps_dict['stepphase_HR']]

        print("---\n", FR_HL_stepphases)
        print(FL_HR_stepphases)


        # loop through every step (pairwise) and get section of data frame for rows where both stepphase columns have same phase
        # --- FR_HL_stepphases
        #print("\n### FR_HL_stepphases ####\n")
        #i = 0
        #nr_of_swings = [i + 1 for phase in FR_HL_stepphases if "swing" in phase]
        #print("nr_of_swings: ", nr_of_swings)
        for j, phase in enumerate(FR_HL_stepphases):
            footpair = "FR_HL"

            if "swing" in phase:
                #print("j: ", j)
                if j == 0 or j == 1:
                    # stance phases might often be empty because numbering can be different
                    # only detect swing phases, then add stance phase which comes before/after?? until next step phase
                    df_section_swing_old = df.loc[(df['stepphase_FR'] == phase) & (df['stepphase_HL'] == phase)]
                    #print("phase: ", phase, "\n", df_section_swing_old)
                else:
                    # gets the next swing phase already to get the end for the swing phase
                    df_section_swing_new = df.loc[(df['stepphase_FR'] == phase) & (df['stepphase_HL'] == phase)]
                    #print("phase: ", phase, "\n", df_section_swing_new)

                    if df_section_swing_old.empty == False and df_section_swing_new.empty == False:
                        # gets the stance phase belonging after df_section_swing_old
                        df_section_stance_indexSTART = list(df_section_swing_old.index)[-1]
                        df_section_stance_indexEND = list(df_section_swing_new.index)[0]-1
                        df_section_stance = df.iloc[df_section_stance_indexSTART:df_section_stance_indexEND]
                        #print("stance {}: \n".format(FR_HL_stepphases[j-1]), df_section_stance)

                        # combine step-wise data:
                        res_phase = "step_" + ''.join(filter(lambda i: i.isdigit(), FR_HL_stepphases[j-1]))
                        mean_body_deflection = (np.mean(df_section_swing_old['body_deflection_angle']) + np.mean(df_section_stance['body_deflection_angle']))/2.0
                        mean_speed_PXperS = (np.mean(df_section_swing_old['speed_PXperS']) + np.mean(df_section_stance['speed_PXperS']))/2.0
                        cranial_bA = [i for i in list(df_section_swing_old["cranial_bA"])]+[j for j in list(df_section_stance["cranial_bA"])]
                        prox_bA = [i for i in list(df_section_swing_old["prox_bA"])]+[j for j in list(df_section_stance["prox_bA"])]
                        tip_bA = [i for i in list(df_section_swing_old["tip_bA"])]+[j for j in list(df_section_stance["tip_bA"])]
                        prox_dist = [i for i in list(df_section_swing_old["prox_dist"])]+[j for j in list(df_section_stance["prox_dist"])]
                        dist_bA = [i for i in list(df_section_swing_old["dist_bA"])]+[j for j in list(df_section_stance["dist_bA"])]
                        cranial_caudal = [i for i in list(df_section_swing_old["cranial_caudal"])]+[j for j in list(df_section_stance["cranial_caudal"])]
                        amplitude_Spine_A = [i for i in list(df_section_swing_old["amplitude_Spine_A"])]+[j for j in list(df_section_stance["amplitude_Spine_A"])]
                        amplitude_Spine_B = [i for i in list(df_section_swing_old["amplitude_Spine_B"])] + [j for j in list(df_section_stance["amplitude_Spine_B"])]
                        amplitude_Spine_C = [i for i in list(df_section_swing_old["amplitude_Spine_C"])] + [j for j in list(df_section_stance["amplitude_Spine_C"])]
                        amplitude_Tail_A = [i for i in list(df_section_swing_old["amplitude_Tail_A"])] + [j for j in list(df_section_stance["amplitude_Tail_A"])]
                        amplitude_Tail_B = [i for i in list(df_section_swing_old["amplitude_Tail_B"])] + [j for j in list(df_section_stance["amplitude_Tail_B"])]
                        amplitude_Tail_C = [i for i in list(df_section_swing_old["amplitude_Tail_C"])] + [j for j in list(df_section_stance["amplitude_Tail_C"])]
                        amplitude_Tail_Tip = [i for i in list(df_section_swing_old["amplitude_Tail_Tip"])] + [j for j in list(df_section_stance["amplitude_Tail_Tip"])]

                        # write data from df_section_swing_old as swing phase and data from df_section_stance as stance phase of one step to new_step_row
                        # only do in this if loop because this gives complete steps
                        new_step_row = [speciesID, runNum, direction, footpair, res_phase, mean_body_deflection, mean_speed_PXperS,
                                        cranial_bA, prox_bA, tip_bA, prox_dist, dist_bA, cranial_caudal,
                                        amplitude_Spine_A, amplitude_Spine_B, amplitude_Spine_C,
                                        amplitude_Tail_A, amplitude_Tail_B, amplitude_Tail_C, amplitude_Tail_Tip,
                                        svl, tailLength, bodyMass, tailMass, BCOMhip, TCOMhip]

                        #print("\n==> new_step_row: \n", new_step_row, "\n")

                        # append new_step_row to data frame:
                        df_length = len(step_wise_df)
                        step_wise_df.loc[df_length] = new_step_row

                    df_section_swing_old = df_section_swing_new


    # --- FL_HR_stepphases
        #print("\n### FL_HR_stepphases ####\n")
        #i = 0
        #nr_of_swings = [(i+1) for phase in FL_HR_stepphases if "swing" in phase][-1]
        #print("nr_of_swings: ", nr_of_swings)
        for j, phase in enumerate(FL_HR_stepphases):
            footpair = "FL_HR"

            if "swing" in phase:
                #print("j: ", j)
                if j == 0 or j == 1:
                    # stance phases might often be empty because numbering can be different
                    # only detect swing phases, then add stance phase which comes before/after?? until next step phase
                    df_section_swing_old = df.loc[(df['stepphase_FL'] == phase) & (df['stepphase_HR'] == phase)]
                    #print("phase: ", phase, "\n", df_section_swing_old)
                else:
                    # gets the next swing phase already to get the end for the swing phase
                    df_section_swing_new = df.loc[(df['stepphase_FL'] == phase) & (df['stepphase_HR'] == phase)]
                    #print("phase: ", phase, "\n", df_section_swing_new)

                    if df_section_swing_old.empty == False and df_section_swing_new.empty == False:
                        # gets the stance phase belonging after df_section_swing_old
                        df_section_stance_indexSTART = list(df_section_swing_old.index)[-1]
                        df_section_stance_indexEND = list(df_section_swing_new.index)[0] - 1
                        df_section_stance = df.iloc[df_section_stance_indexSTART:df_section_stance_indexEND]
                        #print("stance {}: \n".format(FL_HR_stepphases[j - 1]), df_section_stance)

                        # combine step-wise data:
                        res_phase = "step_" + ''.join(filter(lambda i: i.isdigit(), FL_HR_stepphases[j - 1]))
                        mean_body_deflection = (np.mean(df_section_swing_old['body_deflection_angle']) + np.mean(df_section_stance['body_deflection_angle'])) / 2.0
                        mean_speed_PXperS = (np.mean(df_section_swing_old['speed_PXperS']) + np.mean(df_section_stance['speed_PXperS'])) / 2.0
                        cranial_bA = [i for i in list(df_section_swing_old["cranial_bA"])] + [j for j in list(df_section_stance["cranial_bA"])]
                        prox_bA = [i for i in list(df_section_swing_old["prox_bA"])] + [j for j in list(df_section_stance["prox_bA"])]
                        tip_bA = [i for i in list(df_section_swing_old["tip_bA"])] + [j for j in list(df_section_stance["tip_bA"])]
                        prox_dist = [i for i in list(df_section_swing_old["prox_dist"])] + [j for j in list(df_section_stance["prox_dist"])]
                        dist_bA = [i for i in list(df_section_swing_old["dist_bA"])] + [j for j in list(df_section_stance["dist_bA"])]
                        cranial_caudal = [i for i in list(df_section_swing_old["cranial_caudal"])] + [j for j in list(df_section_stance["cranial_caudal"])]
                        amplitude_Spine_A = [i for i in list(df_section_swing_old["amplitude_Spine_A"])] + [j for j in list(df_section_stance["amplitude_Spine_A"])]
                        amplitude_Spine_B = [i for i in list(df_section_swing_old["amplitude_Spine_B"])] + [j for j in list(df_section_stance["amplitude_Spine_B"])]
                        amplitude_Spine_C = [i for i in list(df_section_swing_old["amplitude_Spine_C"])] + [j for j in list(df_section_stance["amplitude_Spine_C"])]
                        amplitude_Tail_A = [i for i in list(df_section_swing_old["amplitude_Tail_A"])] + [j for j in list(df_section_stance["amplitude_Tail_A"])]
                        amplitude_Tail_B = [i for i in list(df_section_swing_old["amplitude_Tail_B"])] + [j for j in list(df_section_stance["amplitude_Tail_B"])]
                        amplitude_Tail_C = [i for i in list(df_section_swing_old["amplitude_Tail_C"])] + [j for j in list(df_section_stance["amplitude_Tail_C"])]
                        amplitude_Tail_Tip = [i for i in list(df_section_swing_old["amplitude_Tail_Tip"])] + [j for j in list(df_section_stance["amplitude_Tail_Tip"])]


                        # write data from df_section_swing_old as swing phase and data from df_section_stance as stance phase of one step to new_step_row
                        # only do in this if loop because this gives complete steps
                        new_step_row = [speciesID, runNum, direction, footpair, res_phase, mean_body_deflection,
                                        mean_speed_PXperS,
                                        cranial_bA, prox_bA, tip_bA, prox_dist, dist_bA, cranial_caudal,
                                        amplitude_Spine_A, amplitude_Spine_B, amplitude_Spine_C,
                                        amplitude_Tail_A, amplitude_Tail_B, amplitude_Tail_C, amplitude_Tail_Tip,
                                        svl, tailLength, bodyMass, tailMass, BCOMhip, TCOMhip]

                        #print("\n==> new_step_row: \n", new_step_row, "\n")

                        # append new_step_row to data frame:
                        df_length = len(step_wise_df)
                        step_wise_df.loc[df_length] = new_step_row

                    df_section_swing_old = df_section_swing_new

    print(step_wise_df)
    # save results:
    step_wise_df.to_csv(os.path.join(summary_folder, "step_wise_summary_tails.csv"), header=True, index=False)

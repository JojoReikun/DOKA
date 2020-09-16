def footprint_alignment_parameter(**kwargs):
    """
    The footprint alignment parameter is defined as:
    "the mean standard deviation of the projection of the fore, mid and hind legs onto the body displacement axis"
    it therefore measures how well the insects conform to the "follow-the-leader" coordination pattern

    In an FTL gait, all legs tend to place at the footprints made by the legs ahead of them.

    :Return: results dataframe with 6 key pair values, the value for each key is just one number
    that is, the average footprint alignment across all frames for a given leg

    """

    import numpy as np
    import statistics
    import math
    import pandas as pd
    import scipy as signal
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    # get kwargs:
    df_result_current = kwargs.get('df_result_current')
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    filename = kwargs.get("filename")
    animal = kwargs.get("animal")
    likelihood = kwargs.get("likelihood")

    feet = animal_settings.get_list_of_feet(animal)
    scorer = data.columns[1][0]

    ### CALCULATION:
    results = {}
    indexes_data = []
    signs_data = []
    counter = 0


    indexes = [col for col in df_result_current.columns if ("phase_indexes" in col)]
    signs = [col for col in df_result_current.columns if ("phase_signs" in col)]

    # these dictionaries will store the x and y coordinates of the AEP  positions in the global frame
    # i.e the frame in deep lab cut, not a coordinate system at the coxa of the foot of interest

    aep_global = {}
    # using just the aep positions for now, should I average over all the values of the stance phase
    # and use that instead?

    b, a = signal.butter(3, 0.1, btype='lowpass', analog=False) # check different types
    # check b and a values, a = frequency, b = polynomial order

    aep_global = {}
    head_global = {}
    abdomen_global = {}
    aep_idx = {}

    for foot in feet:

        for col in indexes:
            if foot in col:
                indexes_data = df_result_current[col]

        for col in signs:
            if foot in signs:
                signs_data = df_result_current[col]

        for i in range(len(indexes_data)):
            # need to add two onto the coordinates to get the correct aep and pep indexes in terms of the raw data
            indexes_data[i] = indexes_data[i] + 2

            if signs_data[i] < 0:
                counter += 1

        # therefore at this point, you have the indexes of AEP and PEP values for a given foot
        # and also sign information, to determine which of these indexes refer to AEP

        # giving warning that it cannot find the filtfilt method?
        # is the type of foot_lpx a list?
        foot_lpx = signal.filtfilt(b, a, (data.loc[:, (scorer, foot, "x")]))
        foot_lpy = signal.filtfilt(b, a, (data.loc[:, (scorer, foot, "y")]))

        aep_global["aep_x_{}".format(foot)] = np.full((counter,), np.NAN)
        aep_global["aep_y_{}".format(foot)] = np.full((counter,), np.NAN)
        aep_idx[foot] = np.full((counter,), np.NAN)

        # read in all frames (x) differences: if moving forward = pos, if moving backwards = neg
        i = 0
        for row in range(len(indexes_data)):

            if signs_data < 0:

                # should I still check for the likelihood?

                # means the insect is transitioning from swing to stance phase, so will be AEP
                aep_global["aep_x_{}".format(foot)][i] = (foot_lpx[indexes_data[row]])
                aep_global["aep_y_{}".format(foot)][i] = (foot_lpy[indexes_data[row]])
                aep_idx[foot][i] = indexes_data[row]
                i += 1
            else:
                continue

        # now collecting the data for head and abdomen

        head_global["head_x_{}".format(foot)] = np.full((counter,), np.NAN)
        head_global["head_y_{}".format(foot)] = np.full((counter,), np.NAN)

        abdomen_global["ab_x_{}".format(foot)] = np.full((counter,), np.NAN)
        abdomen_global["ab_y_{}".format(foot)] = np.full((counter,), np.NAN)

        i = 0

        for row in range(len(indexes_data)):

            if (foot == "l1" or foot == "r1"):

                if signs_data[row] < 0:

                    head_global["head_x_{}".format(foot)][i] = (data.loc[indexes_data[row]]['scorer', 'head', 'x'])
                    head_global["head_y_{}".format(foot)][i] = (data.loc[indexes_data[row]]['scorer', 'head', 'y'])

                    abdomen_global["ab_x_{}".format(foot)][i] = (data.loc[indexes_data[row]]['scorer', 'abdomen', 'x'])
                    abdomen_global["ab_y_{}".format(foot)][i] = (data.loc[indexes_data[row]]['scorer', 'abdomen', 'y'])
                    i += 1

                else:
                    continue

    # at this point, there should now be:
    # 1.) aep_global, with keys corresponding to values of x and y coordinates for ALL feet AEP values
    # 2.) head_global, with keys corresponding to values of x and y coordinates for t
    # 3.) aep_idx, with keys corresponding to indexes for the occurrences of AEP, to give
    # an indication of sequencing in time

    # need to find the the first occurring AEP values for the middle and hind legs AFTER the occurrence of
    # the first recorded foreleg AEP
    # then add 1 and 2 respectively to find the correct clusters for the footprint alignment parameter

    leg_side = ['l', 'r']
    leg_no = ['1', '2', '3']

    for side in leg_side:

        first_index = aep_idx[side + '1'][0]
        # idx of the the first recorded aep of the foreleg on a given side

        for i in range(counter):
            if first_index < aep_idx[side + '2'][i]:
                start_mid = i + 1
                break
            else:
                continue

        for i in range(counter):
            if first_index < aep_idx[side + '3'][i]:
                start_hind = i + 2
                break
            else:
                continue

        # METHOD TO DETERMINE THE FOOTPRINT ALIGNMENT PARAMETER:
        # should I be low passing the head/abdomen data too?

        i = 0
        start_fore = 0
        starters = [start_fore, start_mid, start_hind]
        rel_disps= []
        footprint_ap = {}


        while ((i <= len(aep_idx[side + '1'])) and (i <= len(aep_idx[side + '2'])) and (i <= len(aep_idx[side + '3']))):

            # using the 0th index for the fore leg, the start_mid index for the mid leg, and the start_hind index for the hind
            # need to form vectors with the common point as the head

            f_h_vector = {}
            footprint_ap[side] = []

            j = 1
            for start in starters:
                f_h_vector["fh" + str(j)] = (
                    aep_global["aep_x_" + side + str(j)][start + i] - head_global["head_x_" + side + '1'][start + i],
                    aep_global["aep_y_" + side + str(j)][start + i] - head_global["head_y" + side + '1'][start + i])

            h_a_vector = (head_global["head_x_" + side + '1'] - abdomen_global["ab_x_" + side + '1'],
                          head_global["head_y_" + side + '1'] - abdomen_global["ab_y_" + side + '1'])

            # find the dot product between the vectors

            for j in range(1, 4):

                angle = auxiliaryfunctions.py_angle_betw_2vectors(f_h_vector["fh" + str(j)], h_a_vector)
                angle = 180 - angle

                # this angle needs to be signed!
                # calculate the Euclidean distance between the head point and AEP point

                distance = np.sqrt((f_h_vector["fh" + str(j)][0]) ** 2 + (f_h_vector["fh" + str(j)][1]) ** 2)
                d = (math.cos(angle))*(distance/conv_factor)  # need to add in the conversion factor!
                rel_disps.append(d)

            # at this point, should now have the distances of the AEP values in a given cluster
            # from the reference point of the head (from the frame with AEP foreleg)
            # and this distance is parallel to the body axis

            std = statistics.stdev(rel_disps)
            footprint_ap[side].append(std)

    # at this point, should now have a dictionary called footprint_ap, which contains the
    # standard deviation of the mean of different AEP clusters

    results = {'footprint_al_ref' + key: value for (key, value) in footprint_ap.items()}

    return results



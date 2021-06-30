def toe_angles(**kwargs):
    import os
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    #print("TOE ANGLE CALCULATION")
    stance_length_threshold = 4

    data = kwargs.get("data")
    config = kwargs.get("config")
    likelihood = kwargs.get("likelihood")
    data_rows_count = kwargs.get("data_rows_count")
    df_result_current = kwargs.get('df_result_current')
    animal = kwargs.get('animal')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    #print(cfg['labels'])

    feet = animal_settings.get_list_of_feet(animal)
    scorer = data.columns[1][0]

    calc_toe_angles = ToeAngleCalculation()
    calc_toe_angles.detect_toe_angle_labels(cfg, feet)
    results = calc_toe_angles.calculate_toe_angles(data, scorer, likelihood, feet, data_rows_count, df_result_current, stance_length_threshold)

    return results


class ToeAngleCalculation:
    """
    class to calculate toe angles. Looks for all available toe angles, because it can be either 4 or 5 for lizards.
    """
    def __init__(self):
        self.toe_labels_available = {}
        self.toe_vectors = {}
        self.toe_angles = {}

    def detect_toe_angle_labels(self, cfg, feet):
        """
        determines for very foot how many and which toe labels are available that follow the pattern: foot_toe
        :return: dictionary with the feet as keys and the respective toe labels as values
        """
        for foot in feet:
            toe_labels = [label for label in cfg['labels'] if "{}_t".format(foot.lower()) in label]
            #print('toe labels: ', toe_labels)
            #toe_labels = toe_labels.sort(key=lambda x: x.rsplit("_", 1)[0])
            sorting_order_5 = ["ti", "ti1", "tm", "to1", "to"]
            sorting_order_4 = ["ti", "ti1", "to1", "to"]
            if len(toe_labels) == 4:
                toe_labels_sorted = [label for x in sorting_order_4 for label in toe_labels if label == "{}_{}".format(foot.lower(), x)]
            elif len(toe_labels) == 5:
                toe_labels_sorted = [label for x in sorting_order_5 for label in toe_labels if label == "{}_{}".format(foot.lower(), x)]
            else:
                print("less or more than 4 or 5 toes available... not a lizard? Or is it Peter Pettigrew?")
            #print('toe labels sorted: ', toe_labels_sorted)
            self.toe_labels_available['{}'.format(foot).lower()] = toe_labels_sorted
        #print(self.toe_labels_available)
        return

    def calculate_toe_angles(self, data, scorer, likelihood, feet, data_rows_count, df_result_current, stance_length_threshold):
        """
        calculated the toe angles foot wise and toe pair wise by using the dict key to build vectors from there
        to every label/toe
        :param
        :return:
        """
        from lizardanalysis.utils import auxiliaryfunctions
        import numpy as np

        data.rename(columns=lambda x: x.lower(), inplace=True)
        feet = [foot.lower() for foot in feet]
        scorer = scorer.lower()
        # TODO: Do this for mid stance instead of frame-wise:

        max_stance_phase_count = 1000
        active_columns = []
        for foot in feet:
            active_columns.append("stepphase_{}".format(foot.upper()))

        results = {}

        # find the needed coordinates for toes and feet in the data and stores the toe vectors (foot <-> toe) in dict
        for foot, column in zip(feet, active_columns):
            column = column.strip('')

            number_of_toes = len(self.toe_labels_available)     # 3 (4 toes) or 4 (5 toes)
            print("number of toes: ", number_of_toes)
            toe_angles_label = {}

            # print("foot   ---   ", foot)
            toe_vectors_label = {}
            # -----> loops through the available toes:
            for label in self.toe_labels_available['{}'.format(foot.lower())]:
                # print("label  --  ", label)

                # -----> Loops through stance phases of current foot
                toe_vectors_stance = {}
                for i in range(1, max_stance_phase_count):

                    toe_vectors_tmp = []
                    cell_value = loop_encode(i)
                    df_stance_section = df_result_current[df_result_current[column] == cell_value]
                    # print("LENGTH OF STANCE PHASE SECTION DF: ", len(df_stance_section))
                    if len(df_stance_section) == 0:
                        break
                    # print(df_stance_section)
                    df_stance_section_indices = list(df_stance_section.index.values)


                    # only includes strides longer than the threshold
                    if len(df_stance_section_indices) > stance_length_threshold:
                        beg_end_tuple = (df_stance_section_indices[0], df_stance_section_indices[-1])


                        for j in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                            # only take the frames with good enough likelihood:
                            foot_likelihood = data.loc[j, (scorer, "{}".format(foot), "likelihood")]
                            toe_likelihood = data.loc[j, (scorer, label, "likelihood")]
                            if foot_likelihood >= likelihood and toe_likelihood >= likelihood:
                                foot_coordinates = ((data.loc[j, (scorer, "{}".format(foot), "x")],
                                                     data.loc[j, (scorer, "{}".format(foot), "y")]))
                                toe_coordinates = ((data.loc[j, (scorer, label, "x")],
                                                    data.loc[j, (scorer, label, "y")]))
                                # builds the vectors for the toes:
                                toe_vectors_tmp.append((foot_coordinates[0] - toe_coordinates[0],
                                                        foot_coordinates[1] - toe_coordinates[1]))

                            else:
                                toe_vectors_tmp.append((np.nan, np.nan))

                        # stores all the beg_end_tuple and a list of all toe vectors for current label for every index of current stance phase
                        toe_vectors_stance[i] = (beg_end_tuple, toe_vectors_tmp)

                toe_vectors_label[label] = toe_vectors_stance

            # calculate angles between neighbour toes:
            toepair_angles = {}  # filled with toe-pair name, and the dict for all stances with the angles for all pairs
            for toe_nr in range(1, number_of_toes):           #TODO: test +1, all toe pairs now??
                # toe_vectors_label_items = tuple of ('toe_label', dict --> toe_vectors_stance)
                toe_vectors_label_items = [item for item in toe_vectors_label.items()]
                #for item in toe_vectors_label_items:
                    #print("items of toe_vectors_label: ", item)
                toe_one = toe_vectors_label_items[toe_nr-1]     # tuple
                name_toe_one = toe_vectors_label_items[toe_nr-1][0]
                toe_two = toe_vectors_label_items[toe_nr]       # tuple
                name_toe_two = toe_vectors_label_items[toe_nr][0]
                #print("toe_one: ", toe_one)
                toepair_angles_stance = {}  # filled with phase nr and respective angles for phase of current toe-pair
                # -----> loop through stance phases (key of toe_vectors_label_items[1]:
                toe_one_phases = [key for key in toe_one[1].keys()]     # should be equal for all toes
                for phase in toe_one_phases:
                    beg_end_tuple_toe_one = toe_one[1][phase][0]
                    beg_end_tuple_toe_two = toe_two[1][phase][0]
                    #print("begendtuple: ", beg_end_tuple_toe_one)
                    beg_end_tuple_current_phase_toe_one = beg_end_tuple_toe_one
                    beg_end_tuple_current_phase_toe_two = beg_end_tuple_toe_two
                    if beg_end_tuple_current_phase_toe_one != beg_end_tuple_current_phase_toe_two:
                        print("ERROR! beg_end_tuple of both toes should be the same!!!")
                    vlist1 = toe_one[1][phase][1]
                    vlist2 = toe_two[1][phase][1]
                    #print("vlist1: ", vlist1)
                    tmp_angles = []     # angles for phase
                    for v1, v2 in zip(vlist1, vlist2):
                        tmp_angles.append(auxiliaryfunctions.py_angle_betw_2vectors(v1, v2))
                    toepair_angles_stance[phase] = (beg_end_tuple_current_phase_toe_one, tmp_angles)

                toepair_angles["{}-{}".format(name_toe_one, name_toe_two)] = toepair_angles_stance
            #print("toepair_angles: ", toepair_angles)

            # now we have all angles for all stance phases for all toe_pairs and we have to calculate the midstance mean
            # -----> loops through the toe pairs:
            for toe_pair, all_angles_stance_wise_dict in toepair_angles.items():
                #print("\ntoe_pair: ", toe_pair)
                results[toe_pair] = np.full((data_rows_count,), np.nan)
                # -----> loops through the stance phases of the current toe pair:
                for stancephase in all_angles_stance_wise_dict.keys():
                    beg_end_tuple_res = all_angles_stance_wise_dict[stancephase][0]
                    toe_angles_res = all_angles_stance_wise_dict[stancephase][1]
                    length_of_stancephase = beg_end_tuple_res[1] - beg_end_tuple_res[0]
                    #print("length of stancephase: ", length_of_stancephase)
                    # find the three mean indices of the stancephase:
                    # always set the stance_length_threshold to 3 which is necessary to calc the mid stance mean
                    if stance_length_threshold < 4:
                        stance_length_threshold = 4
                    else:
                        if length_of_stancephase > stance_length_threshold:  # only include strides longer than at least 5 frames
                            # calculate the mid stance toe angle
                            if length_of_stancephase % 2 == 0:
                                mid_stance_index = int(length_of_stancephase / 2.0)
                                #print("mid stance index %2 == 0: ", mid_stance_index)
                                mean_value = calc_mean_midstance_toe_angles(toe_angles_res, mid_stance_index)
                            else:
                                mid_stance_index = int((length_of_stancephase / 2) + 0.5)
                                #print("mid stance index %2 != 0: ", mid_stance_index)
                                mean_value = calc_mean_midstance_toe_angles(toe_angles_res, mid_stance_index)
                        else:
                            mean_value = np.nan

                        #print("mean value: ", mean_value)

                        # fill mean toe angle into results for respective rows of current stancephase for current toe_pair
                        for row in range(beg_end_tuple_res[0], beg_end_tuple_res[1] + 1):
                            if isinstance(mean_value, np.ndarray):
                                # in some cases toe_angle returned as [nan nan], if that occurs, return value is changed to nan
                                mean_value = np.nan
                            results[toe_pair][row] = mean_value

        results = {'mid_stance_toe_angles_mean_' + key: value for (key, value) in results.items()}
        #print("results: ", results)
        return results


def calc_mean_midstance_toe_angles(toe_angles, mid_stance_index):
    """ calculated the mean of the three tow angles at midstance"""
    import numpy as np
    #print("\nlength of toe_angles: ", len(toe_angles))
    if len(toe_angles) > 2:
        mean_value = np.mean([toe_angles[mid_stance_index - 1],
                              toe_angles[mid_stance_index],
                              toe_angles[mid_stance_index + 1]])
    else:
        mean_value = np.nan

    if  mean_value > 90.:
        mean_value = 180. - mean_value
    return mean_value


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stance000{}'.format(i).encode()
    #print("-----> stance phase cell value :", cell_value)
    return cell_value
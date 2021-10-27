from pathlib import Path
from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis.utils import animal_settings


def toe_alignment_angles(**kwargs):
    """
    This function calculates the angle of each toe (vector: foot-toe) to the body axis.
    This toe alignment angle indicates the individual toes orientation and could show which toe acts the most.
    """

    print("TOE ALIGNMENT ANGLE CALCULATION")
    stance_length_threshold = 4

    data = kwargs.get("data")
    config = kwargs.get("config")
    likelihood = kwargs.get("likelihood")
    data_rows_count = kwargs.get("data_rows_count")
    df_result_current = kwargs.get('df_result_current')
    animal = kwargs.get('animal')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    # print(cfg['labels'])

    feet = animal_settings.get_list_of_feet(animal)
    scorer = data.columns[1][0]

    angles = ToeAlignmentAngleCalculation()
    angles.detect_toe_angle_labels(cfg, feet)
    results = angles.calculate_toe_alignment_angles(data, scorer, likelihood, feet, data_rows_count, df_result_current,
                                                   stance_length_threshold)

    return results


class ToeAlignmentAngleCalculation:
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
            self.toe_labels_available['{}'.format(foot).lower()] = toe_labels_sorted
        return

    def calculate_toe_alignment_angles(self, data, scorer, likelihood, feet, data_rows_count, df_result_current, stance_length_threshold):
        """
        calculates the toe alignment angles foot wise using the dict key to build vectors from there
        to every label/toe. Toe alignment angles are calculated mid stance using the atan function.
        Body axis is always put in as the first vector, therefore polarity indicates the side which the toe is on.
        :param
        :return:
        """
        from lizardanalysis.utils import auxiliaryfunctions
        import numpy as np

        data.rename(columns=lambda x: x.lower(), inplace=True)
        feet = [foot.lower() for foot in feet]
        scorer = scorer.lower()

        max_stance_phase_count = 1000
        active_columns = []
        for foot in feet:
            active_columns.append("stepphase_{}".format(foot.upper()))

        results = {}

        # find the needed coordinates for toes and feet in the data and stores the toe vectors (foot <-> toe) in dict
        for foot, column in zip(feet, active_columns):
            column = column.strip('')

            number_of_toes = len(self.toe_labels_available)     # 3 (4 toes) or 4 (5 toes)
            #print("number of toes: ", number_of_toes+1)
            toe_angles_label = {}

            # print("foot   ---   ", foot)
            toe_vectors_label = {}
            toe_alignment_angles_foot = {}  # {"label": individual_toe_alignment_angles}

            # -----> loops through the available toes:
            for label in self.toe_labels_available['{}'.format(foot.lower())]:
                individual_toe_alignment_angles = []   # stores the beg_end_tuple and the respective angle as a tuple

                result_label = foot + "_" + label
                results[result_label] = np.full((data_rows_count,), np.nan)

                # -----> Loops through stance phases of current foot
                for i in range(1, max_stance_phase_count):
                    toe_vectors_tmp = []
                    cell_value = loop_encode(i)
                    df_stance_section = df_result_current[df_result_current[column] == cell_value]
                    # print("LENGTH OF STANCE PHASE SECTION DF: ", len(df_stance_section))
                    if len(df_stance_section) == 0:
                        break
                    df_stance_section_indices = list(df_stance_section.index.values)


                    # only includes strides longer than the threshold
                    if len(df_stance_section_indices) > stance_length_threshold:
                        beg_end_tuple = (df_stance_section_indices[0], df_stance_section_indices[-1])

                        # get mid stance indices:
                        if (beg_end_tuple[1] - beg_end_tuple[0]) % 2 == 0:
                            mid_stance_index = int(beg_end_tuple[0] + ( (beg_end_tuple[1]-beg_end_tuple[0]) / 2.0))
                        else:
                            mid_stance_index = int(beg_end_tuple[0] + ( (beg_end_tuple[1]-beg_end_tuple[0]) / 2.0) + 0.5)
                        #print("mid stance index: ", mid_stance_index)

                        # only take the frames with good enough likelihood:
                        foot_likelihood = data.loc[mid_stance_index, (scorer, "{}".format(foot), "likelihood")]
                        toe_likelihood = data.loc[mid_stance_index, (scorer, label, "likelihood")]
                        if foot_likelihood >= likelihood and toe_likelihood >= likelihood:
                            foot_coordinates = ((data.loc[mid_stance_index, (scorer, "{}".format(foot), "x")],
                                                    data.loc[mid_stance_index, (scorer, "{}".format(foot), "y")]))
                            toe_coordinates = ((data.loc[mid_stance_index, (scorer, label, "x")],
                                                    data.loc[mid_stance_index, (scorer, label, "y")]))

                            # builds the vectors for the toes:
                            toe_vector = (foot_coordinates[0] - toe_coordinates[0],
                                                        foot_coordinates[1] - toe_coordinates[1])
                            #print("toe_vector: ", toe_vector)

                            # build the body axis vector:
                            bodyaxis_vector = auxiliaryfunctions.calc_body_axis_toes(data, mid_stance_index, scorer)
                            #print("body axis vector: ", bodyaxis_vector)

                            # calculate the angle between the toe vector and the body axis vector using atan:
                            toe_alignment_angle = auxiliaryfunctions.py_angle_betw_2vectors_atan(bodyaxis_vector, toe_vector)

                        else:
                            toe_alignment_angle = (np.nan, np.nan)

                        # stores all the beg_end_tuple and a list of all toe vectors for current label for every index of current stance phase
                        individual_toe_alignment_angles.append( (beg_end_tuple, toe_alignment_angle) )

                        #####
                        # fill in the toe alignment angles into results:
                        for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                            if type(toe_alignment_angle) is tuple:
                                toe_alignment_angle = np.nan
                            #print("toe_alignment_angle: ", toe_alignment_angle)
                            results[result_label][row] = toe_alignment_angle

                toe_alignment_angles_foot[label] = individual_toe_alignment_angles

            #print("FOOT: ", foot, "\ntoe_alignment_angles_foot: ", toe_alignment_angles_foot)

        results = {'toe_alignment_angles_' + key: value for (key, value) in results.items()}
        #print("results: ", results)
        return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stance000{}'.format(i).encode()
    #print("-----> stance phase cell value :", cell_value)
    return cell_value
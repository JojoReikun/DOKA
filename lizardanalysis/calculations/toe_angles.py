def toe_angles(**kwargs):
    import os
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    print("TOE ANGLE CALCULATION")

    data = kwargs.get("data")
    config = kwargs.get("config")
    likelihood = kwargs.get("likelihood")
    data_rows_count = kwargs.get("data_rows_count")

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    #print(cfg['labels'])

    feet = ["FL", "FR", "HR", "HL"]
    scorer = data.columns[1][0]

    calc_toe_angles = ToeAngleCalculation()
    calc_toe_angles.detect_toe_angle_labels(cfg, feet)
    toe_angles = calc_toe_angles.calculate_toe_angles(data, scorer, likelihood, feet, data_rows_count)

    return toe_angles


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

    def calculate_toe_angles(self, data, scorer, likelihood, feet, data_rows_count):
        """
        calculated the toe angles foot wise and toe pair wise by using the dict key to build vectors from there
        to every label/toe
        :param toe_angles_available:
        :return:
        """
        from lizardanalysis.utils import auxiliaryfunctions
        import numpy as np

        data.rename(columns=lambda x: x.lower(), inplace=True)
        feet = [foot.lower() for foot in feet]
        scorer = scorer.lower()
        # find the needed coordinated for toes and feet in the data and stores the toe vectors (foot <-> toe) in dict
        for foot in feet:
            #print("foot   ---   ", foot)
            foot_toe_vectors = {}
            foot_toe_angles = {}
            for label in self.toe_labels_available['{}'.format(foot.lower())]:
                #print("label  --  ", label)
                toe_vectors_tmp = []
                for row in range(data_rows_count):
                    foot_coordinates = ((data.loc[row, (scorer, "{}".format(foot), "x")],
                                        data.loc[row, (scorer, "{}".format(foot), "y")]))
                    toe_coordinates = ((data.loc[row, (scorer, label, "x")],
                                        data.loc[row, (scorer, label, "y")]))
                    toe_vectors_tmp.append((foot_coordinates[0] - toe_coordinates[0],
                                           foot_coordinates[1] - toe_coordinates[1]))
                self.toe_vectors[label] = toe_vectors_tmp       # stores all toe vectors for all feet
                foot_toe_vectors[label] = toe_vectors_tmp       # stores toe vectors for one foot

            # calculate toe angles
            foot_toe_vector_keys = [key for key in foot_toe_vectors.keys()]
            #print("keys: ", foot_toe_vector_keys)
            for j in range(1, len(foot_toe_vector_keys)):
                toe_pair_angles = []
                #print("test key: ", foot_toe_vector_keys[j])
                # print({k: len(v) for k, v in foot_toe_vectors.items()})
                for k in range(len(foot_toe_vectors[foot_toe_vector_keys[j]])):
                    #print("j-1: ", foot_toe_vector_keys[j-1], foot_toe_vectors[foot_toe_vector_keys[j-1]][k])
                    vector1 = foot_toe_vectors[foot_toe_vector_keys[j-1]][k]
                    #print("j: ", foot_toe_vector_keys[j], foot_toe_vectors[foot_toe_vector_keys[j]][k])
                    vector2 = np.transpose(foot_toe_vectors[foot_toe_vector_keys[j]][k])
                    toe_angle = auxiliaryfunctions.py_angle_betw_2vectors(vector1, vector2)
                    if toe_angle >= 90.0:
                        toe_pair_angles.append(180.0 - toe_angle)
                    else:
                        toe_pair_angles.append(toe_angle)
                self.toe_angles["{}-{}".format(foot_toe_vector_keys[j-1], foot_toe_vector_keys[j])] = toe_pair_angles

        # print("TOE PAIR ANGLES: ",
        #       "{" + "\n".join("{!r}: {!r}".format(k, v) for k, v in self.toe_angles.items()) + "}")
        # print("SUMMARY: \n",
        #       "{" + "\n".join(
        #           "{!r}: {!r}, {!r}".format(k, np.nanmean(v), np.nanstd(v)) for k, v in self.toe_angles.items()) + "}")

        #print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in self.toe_vectors.items()) + "}")

        return self.toe_angles
def wrist_angles(**kwargs):
    """
        Loops through all feet/stepphase columns and in each column through all stance phases and for every stance phase
        through all stance phase frames. For every frame:
        1st) determines vector between inner and outer toe --> toe vector
        2nd) rotates the toe vector by 90 deg so it's perpendicular to 1st --> wrist vector
        3rd) calculate the angle between wrist vector and body axis for all frames, also calculate the mean
        """
    # TODO: if no stance is > 4 frames, column will not be generated, causes trouble for R script combine --> fix

    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    filename = kwargs.get('filename')

    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]
    max_stance_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    #print("active_columns: ", active_columns)

    ##################################################################################################
    results = {}
    # -----> Loops through feet
    for foot, column in zip(feet, active_columns):
        mean_mid_stance_angles = []  # takes the 3 mid stance indices and calculated the mean angle
        std_mid_stance_values = []

        #print("\n LOOPS THROUGH FEET ---> FOOT: ", foot)
        column = column.strip('')
        # print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)

        # -----> Loops through stance phases of foot
        for i in range(1, max_stance_phase_count):
            #print("\n LOOPS THROUGH STANCE PHASES ---> Stance_{} ".format(i))
            inner_toe_coordinates = []
            outer_toe_coordinates = []
            foot_coordinates = []
            toe_vectors = []
            wrist_vectors = []
            body_axes = []

            cell_value = loop_encode(i)
            df_stance_section = df_result_current[df_result_current[column] == cell_value]
            # print("LENGTH OF STANCE PHASE SECTION DF: ", len(df_stance_section))
            if len(df_stance_section) == 0:
                break
            # print(df_stance_section)
            df_stance_section_indices = list(df_stance_section.index.values)
            if len(df_stance_section_indices) > 0:
                beg_end_tuple = (df_stance_section_indices[0], df_stance_section_indices[-1])
                #print(beg_end_tuple)

                # -----> Loops through stance phase frame of current stance phase
                for i in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                    # adds respective coord tuples to lists --> [(x,y), (x1,y1), ...]
                    inner_toe_coordinates.append((data.loc[i, (scorer, "{}_ti".format(foot), "x")],
                                                  data.loc[i, (scorer, "{}_ti".format(foot), "y")]))
                    outer_toe_coordinates.append((data.loc[i, (scorer, "{}_to".format(foot), "x")],
                                                  data.loc[i, (scorer, "{}_to".format(foot), "y")]))
                    foot_coordinates.append((data.loc[i, (scorer, "{}".format(foot), "x")],
                                             data.loc[i, (scorer, "{}".format(foot), "y")]))
                    body_axes.append(calc_body_axis(data, i, scorer))

                # 1st) toe vector (Start - End => vector points towards start (outer toe))
                for i_item, o_item in zip(inner_toe_coordinates, outer_toe_coordinates):
                    # toe_vectors.append(((i_item[0] - o_item[0]), (i_item[1] - o_item[1])))        # config = 2
                    toe_vectors.append(((o_item[0] - i_item[0]), (o_item[1] - i_item[1])))
                #print("toe vectors {}: ".format(foot), toe_vectors)

                # 2nd) rotate toe_vector to get wrist_vector. Differentiate cases: FR&HL => rotate CW(y, -x), FL&HR => CCW(-y, x)
                for toe_vector in toe_vectors:
                    # mirror toe_vector along x-axis
                    toe_vector = (toe_vector[0], toe_vector[1] * (-1))
                    if foot == "FR" or foot == "HL":
                        toe_vector = (toe_vector[1], toe_vector[0] * (-1))
                        # print("CW rotated toe_vector: ", toe_vector)
                        wrist_vectors.append(toe_vector)
                    elif foot == "FL" or foot == "HR":
                        toe_vector = (toe_vector[1] * (-1), toe_vector[0])
                        # print("CCW rotated toe_vector: ", toe_vector)
                        wrist_vectors.append(toe_vector)
                #print("wirst vectors {}: ".format(foot), wrist_vectors)

                # 3rd) calculate the angle between the wrist_vector and the body axis for every frame
                wrist_angles = []
                for wrist_vector, body_axis in zip(wrist_vectors, body_axes):
                    wrist_angle = auxiliaryfunctions.py_angle_betw_2vectors(body_axis, wrist_vector)
                    # if foot == "FL":
                    #     wrist_angle = 90.0 - wrist_angle
                    # elif foot == "HL":
                    #     wrist_angle = 270.0 - wrist_angle
                    wrist_angles.append(wrist_angle)
                #print("length of wrist_angles: ", len(wrist_angles))

                # calculate the mid stance wrist angle (only of stance phases which are at least 4 frames long
                if len(wrist_angles) <= 3:
                    #print("NAN \n")
                    mean_value, std_value = np.NAN, np.NAN
                elif len(wrist_angles) % 2 == 0:
                    mid_stance_index = int(len(wrist_angles) / 2.0)
                    #print("mid stance index %2==0: ", mid_stance_index)
                    mean_value, std_value = calc_mean_and_std_wrist_angles(wrist_angles, mid_stance_index)
                else:
                    mid_stance_index = int((len(wrist_angles) / 2) + 0.5)
                    #print("mid stance index %2!=0: ", mid_stance_index)
                    mean_value, std_value = calc_mean_and_std_wrist_angles(wrist_angles, mid_stance_index)
                #print("mid_stance_angle: ", mean_value, " --- ", foot)
                #print("std: ", std_value, " --- ", foot)
                mean_mid_stance_angles.append(mean_value)
                std_mid_stance_values.append(std_value)

            for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                results[foot][row] = mean_value

        #print("mean mid stance angles --- {} ".format(foot), mean_mid_stance_angles)
        #print("std mid stance values --- {} ".format(foot), std_mid_stance_values)
    # rename dictionary keys of results
    # TODO: save std as another column, or put mean and std in same cell
    results = {'mid_stance_wrist_angles_mean_' + key: value for (key, value) in results.items()}

    #print("results: ", results)
    return results


def loop_encode(i):
    cell_value = 'stance000{}'.format(i).encode()
    #print("-----> stance phase cell value :", cell_value)
    return cell_value


def calc_body_axis(df, index, scorer):
    """calculates the body axis vector of the gecko for the passed index: START = Hip, END = Shoulder
    returns a vector (x,y)"""
    body_axis_vector = ((df.loc[index, (scorer, "Shoulder", "x")] - df.loc[index, (scorer, "Hip", "x")]),
                        (df.loc[index, (scorer, "Shoulder", "y")] - df.loc[index, (scorer, "Hip", "y")]))
    return body_axis_vector


def calc_mean_and_std_wrist_angles(wrist_angles, mid_stance_index):
    import numpy as np
    mean_value = np.mean([wrist_angles[mid_stance_index - 1],
                          wrist_angles[mid_stance_index],
                          wrist_angles[mid_stance_index + 1]])
    std_value = np.std([wrist_angles[mid_stance_index - 1],
                        wrist_angles[mid_stance_index],
                        wrist_angles[mid_stance_index + 1]])
    return mean_value, std_value


def setdiff_sorted(array1, array2, assume_unique=False):
    import numpy as np
    ans = np.setdiff1d(array1, array2, assume_unique).tolist()
    if assume_unique:
        return sorted(ans)
    return ans

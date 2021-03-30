def stride_length(**kwargs):
    """
    Stride length = distance covered by body during one step (swing + stance)
    """
    # TODO: include distance from stance
    import numpy as np
    import pandas as pd
<<<<<<< HEAD
    pd.set_option('display.max_columns', None)  # for printing the df in console
=======
    from lizardanalysis.utils import animal_settings
    pd.set_option('display.max_columns', None)
>>>>>>> gui

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
<<<<<<< HEAD
    likelihood = kwargs.get('likelihood')
=======
    animal = kwargs.get('animal')
>>>>>>> gui

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    max_stride_phase_count = 1000
    active_columns = []

    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    # print("active_columns: ", active_columns)

    results = {}
    for foot, column in zip(feet, active_columns):
        # print("\n----------- FOOT: ", foot)
        column = column.strip('')
        # print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        for i in range(1, max_stride_phase_count):
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            # print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                # print(beg_end_tuple)

                # filter for likelihood of labels:
                likelihood_shoulder_begin = data.loc[beg_end_tuple[0]][scorer, "Shoulder", 'likelihood']
                likelihood_shoulder_end = data.loc[beg_end_tuple[1]][scorer, "Shoulder", 'likelihood']
                likelihood_hip_begin = data.loc[beg_end_tuple[0]][scorer, "Hip", 'likelihood']
                likelihood_hip_end = data.loc[beg_end_tuple[1]][scorer, "Hip", 'likelihood']
                if likelihood_shoulder_begin >= likelihood and likelihood_shoulder_end >=0 \
                        and likelihood_hip_begin >= 0 and likelihood_hip_end >= 0:
                    # calculate the euclidean distance between last coord and current coord of shoulder and hip -> mean
                    xdiff_shoulder = data.loc[beg_end_tuple[1]][scorer, "Shoulder", 'x'] - data.loc[beg_end_tuple[0]][
                        scorer, "Shoulder", 'x']
                    ydiff_shoulder = data.loc[beg_end_tuple[1]][scorer, "Shoulder", 'y'] - data.loc[beg_end_tuple[0]][
                        scorer, "Shoulder", 'y']
                    distance_shoulder = np.sqrt(xdiff_shoulder ** 2 + ydiff_shoulder ** 2)
                    xdiff_hip = data.loc[beg_end_tuple[1]][scorer, "Hip", 'x'] - data.loc[beg_end_tuple[0]][
                        scorer, "Hip", 'x']
                    ydiff_hip = data.loc[beg_end_tuple[1]][scorer, "Hip", 'y'] - data.loc[beg_end_tuple[0]][
                        scorer, "Hip", 'y']
                    distance_hip = np.sqrt(xdiff_hip ** 2 + ydiff_hip ** 2)
                else:
                    distance_shoulder = np.NAN
                    distance_hip = np.NAN
            else:
                distance_shoulder = np.NAN
                distance_hip = np.NAN

            distance = get_distance_average(distance_shoulder, distance_hip)

            for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                results[foot][row] = distance
            # print("distance: ", distance)

    # rename dictionary keys of results
    results = {'stride-length_' + key: value for (key, value) in results.items()}
    # print("\n \n -------------------- results FINAL: \n", results)

    return results


def loop_encode(i):
    cell_value = 'swing000{}'.format(i).encode()
    return cell_value

    return 0


def get_distance_average(dist1, dist2):
    import numpy as np
    if np.isnan(dist1) == True and np.isnan(dist2) == False:
        distance = dist2
    elif np.isnan(dist1) == False and np.isnan(dist2) == True:
        distance = dist1
    elif np.isnan(dist1) == True and np.isnan(dist2) == True:
        distance = np.NaN
    else:
        distance = (dist1 + dist2) / 2.0
    return distance
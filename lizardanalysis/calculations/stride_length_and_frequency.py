def stride_length_and_frequency(**kwargs):
    """
    Stride length = distance covered by body during one step (swing + stance) in px
    Stride frequency = number of strides per second (determined with the framerate defined in the config file by the user)
    """

    print("stride length and stride frequency")
    import numpy as np
    import pandas as pd

    #pd.set_option('display.max_columns', None)  # for printing the df in console

    from lizardanalysis.utils import animal_settings, auxiliaryfunctions
    pd.set_option('display.max_columns', None)


    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')
    config = kwargs.get('config')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    max_stride_phase_count = 1000
    active_columns = []

    # get the framerate defined in the config file:
    cfg = auxiliaryfunctions.read_config(config)
    framerate = cfg['framerate']

    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    # print("active_columns: ", active_columns)

    step_phase_lengths = []
    stride_lengths = []

    results = {}
    for foot, column in zip(feet, active_columns):
        # print("\n----------- FOOT: ", foot)
        column = column.strip('')
        # print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)


        for i in range(1, max_stride_phase_count):
            # this looks for all stride phases of the current foot
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]

            if len(df_stride_section) == 0:
                break

            # print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)

            # exclude all step phases which are 0 or longer than 1/10 of framerate
            if len(df_stride_section_indices) <= float(framerate) / 100 or len(df_stride_section_indices) > float(framerate) / 10:
                break

            step_phase_lengths.append(len(df_stride_section_indices))

            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])

                # filter for likelihood of labels:
                likelihood_shoulder_begin = data.loc[beg_end_tuple[0]][scorer, "Shoulder", 'likelihood']
                likelihood_shoulder_end = data.loc[beg_end_tuple[1]][scorer, "Shoulder", 'likelihood']
                likelihood_hip_begin = data.loc[beg_end_tuple[0]][scorer, "Hip", 'likelihood']
                likelihood_hip_end = data.loc[beg_end_tuple[1]][scorer, "Hip", 'likelihood']

                # only includes strides where the shoulder to hip of the lizard are fully accurately tracked
                if likelihood_shoulder_begin >= likelihood and likelihood_shoulder_end >= likelihood \
                        and likelihood_hip_begin >= likelihood and likelihood_hip_end >= likelihood:
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

            if i > 1:
                # saves the distance to results for the current foot, for stride1 beg until stride 2 begin
                for row in range(prev_beg_end_tuple[0], beg_end_tuple[0] + 1):
                    results[foot][row] = distance
                stride_lengths.append(distance)

                #stride_lengths.append(abs(prev_beg_end_tuple[0] - (beg_end_tuple[0] + 1)))


            prev_beg_end_tuple = beg_end_tuple

    # calculate the stride frequency for the entire run - could include it in loop above to get frequ. stepphase wise
    stride_frequency = np.round(framerate/np.mean(stride_lengths), 2)
    #print("stride_frequency: ", stride_frequency)
    #print("stride length: ", stride_lengths)
    #print("step phase lengths: ", step_phase_lengths)

    frequency_list = np.array(data_rows_count * [stride_frequency], dtype=np.string_)
    frequency_list = [decode(freq) for freq in frequency_list]

    # rename dictionary keys of results
    results = {'stride-length_' + key: value for (key, value) in results.items()}
    # print("\n \n -------------------- results FINAL: \n", results)

    # add stride frequency to results
    results['stride_frequency'] = frequency_list

    return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stance000{}'.format(i).encode()
    #print("-----> stance phase cell value :", cell_value)
    return cell_value


def decode(byte_object):
    decoded = byte_object.decode("ASCII")
    return decoded


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

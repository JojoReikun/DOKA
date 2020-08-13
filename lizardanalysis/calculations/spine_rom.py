def spine_rom(**kwargs):
    """
    calculates the spine ROM (average betw. shoulder and hip ROM) for every stride for every foot.
    takes the average of the shoulder ROM (shoulder-spine vector to body-axis)
    and the hip ROM (hip-spine vector to body-axis).
    ROM is always defined as the maximum ROM angle of the stride - minimum ROM angle of the stride.
    :return:
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    #print('SPINE ROM CALCULATION')
    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    max_stride_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))

    results = {}

    for foot, column in zip(feet, active_columns):
        #print("\n----------- FOOT: ", foot)
        column = column.strip('')
        #print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        shoulder_rom_list = []
        hip_rom_list = []

        for i in range(1, max_stride_phase_count):
            #print('\nstride phase i: ', i)
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            #print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            # only include strides longer than 5 frames:
            if len(df_stride_section_indices) > 5:
                shoulder_rom_list_stride = []
                hip_rom_list_stride = []
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                #print(beg_end_tuple)
                # calculate the vectors: Spine-Shoulder and Spine-Hip
                for j in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                    shoulder_foot_likelihood_begin = data.loc[j, (scorer, "Shoulder_{}".format(foot), "likelihood")]
                    knee_foot_likelihood_begin = data.loc[j, (scorer, "{}_knee".format(foot), "likelihood")]
                    shoulder_foot_likelihood_end = data.loc[j, (scorer, "Shoulder_{}".format(foot), "likelihood")]
                    knee_foot_likelihood_end = data.loc[j, (scorer, "{}_knee".format(foot), "likelihood")]
                    #print("likelihoods: ", shoulder_foot_likelihood_begin, knee_foot_likelihood_begin, shoulder_foot_likelihood_end, knee_foot_likelihood_end)

                    # filters data points of labels for likelihood
                    if shoulder_foot_likelihood_begin >= likelihood and knee_foot_likelihood_begin >= likelihood and\
                            shoulder_foot_likelihood_end >= likelihood and knee_foot_likelihood_end >= likelihood:
                        spine_shoulder_vector = ((data.loc[j, (scorer, "Spine", "x")] - data.loc[j, (scorer, "Shoulder", "x")]),
                                          (data.loc[j, (scorer, "Spine", "y")] - data.loc[j, (scorer, "Shoulder", "y")]))
                        spine_hip_vector = ((data.loc[j, (scorer, "Spine", "x")] - data.loc[j, (scorer, "Hip", "x")]),
                                    (data.loc[j, (scorer, "Spine", "y")] - data.loc[j, (scorer, "Hip", "y")]))

                        # calculate the angles from both vectors to body-axis
                        body_axis = calc_body_axis(data, j, scorer)
                        # rotate body axis by 90 degree CW so a crossing via body axis doesn't occur:
                        body_axis_rotated = (body_axis[1], body_axis[0] * (-1))
                        shoulder_rom_i = auxiliaryfunctions.py_angle_betw_2vectors(spine_shoulder_vector, body_axis_rotated)
                        hip_rom_i = auxiliaryfunctions.py_angle_betw_2vectors(spine_hip_vector, body_axis_rotated)

                        shoulder_rom_list_stride.append(shoulder_rom_i)
                        hip_rom_list_stride.append(hip_rom_i)

                    else:
                        # appends nan if likelihood is too bad to include
                        shoulder_rom_list_stride.append(np.nan)
                        hip_rom_list_stride.append(np.nan)
                # print('max: ', max(shoulder_rom_list_stride), '\n',
                #       'min: ', min(shoulder_rom_list_stride), '\n',
                #       'res: ', max(shoulder_rom_list_stride)-min(shoulder_rom_list_stride))
                # make sure max() and min() can operate, hence length of lists > 0
                if len(shoulder_rom_list_stride) > 0 and len(hip_rom_list_stride) > 0:
                    shoulder_rom = max(shoulder_rom_list_stride) - min(shoulder_rom_list_stride)
                    hip_rom = max(hip_rom_list_stride) - min(hip_rom_list_stride)
                else:
                    shoulder_rom = 0
                    hip_rom = 0

                # write spine ROMs as average(shoulder and hip ROM) to result df only if ROMs > 0
                # ROMs = 0 if only 1 or less values were calculated for the stride
                if shoulder_rom > 0 and hip_rom > 0:
                    for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                        results[foot][row] = (shoulder_rom + hip_rom)/2.

                # debug
                # print('stride: ', i,
                #       '\nshoulder_ROM: ', shoulder_rom,
                #       '\nhip_ROM: ', hip_rom,
                #       '\naverage: ', (shoulder_rom + hip_rom) / 2.)

                # debug
                shoulder_rom_list.append(shoulder_rom)
                hip_rom_list.append(hip_rom)

        #debug
        mean_shoulder_rom = np.nanmean(shoulder_rom_list)
        mean_hip_rom = np.nanmean(hip_rom_list)
        std_shoulder_rom = np.nanstd(shoulder_rom_list)
        std_hip_rom = np.nanstd(hip_rom_list)
        # print('foot: ', foot,
        #         'mean_shoulder: ', mean_shoulder_rom,
        #         'std_shoulder: ', std_shoulder_rom,
        #         'mean_hip: ', mean_hip_rom,
        #         'std_hip: ', std_hip_rom)

    # rename dictionary keys of results
    results = {'spineROM_' + key: value for (key, value) in results.items()}

    return results


def calc_body_axis(df, index, scorer):
    """calculates the body axis vector of the gecko for the passed index: START = Hip, END = Shoulder
    returns a vector (x,y)"""
    body_axis_vector = ((df.loc[index, (scorer, "Shoulder", "x")] - df.loc[index, (scorer, "Hip", "x")]),
                        (df.loc[index, (scorer, "Shoulder", "y")] - df.loc[index, (scorer, "Hip", "y")]))
    return body_axis_vector


def loop_encode(i):
    cell_value = 'swing000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value
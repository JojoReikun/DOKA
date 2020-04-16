def limb_rom(**kwargs):
    """
    Calculates the angle between the limb vector (knee - shoulder) for every limb/foot and the body axis.
    To determine the Range of Motion, the angle at the beginning of a stride phase is subtracted from the angle at the
    end of the stride phase.
    :return:
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    #print('LIMB ROM CALCULATION')
    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    likelihood = kwargs.get('likelihood')

    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]
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
        limb_rom_foot = []

        for i in range(1, max_stride_phase_count):
            #print('stride phase i: ', i)
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            #print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                #print(beg_end_tuple)
                limb_vector_begin = ((data.loc[beg_end_tuple[0], (scorer, "Shoulder_{}".format(foot), "x")]
                                      - data.loc[beg_end_tuple[0], (scorer, "{}_knee".format(foot), "x")]),
                                     (data.loc[beg_end_tuple[0], (scorer, "Shoulder_{}".format(foot), "y")]
                                      - data.loc[beg_end_tuple[0], (scorer, "{}_knee".format(foot), "y")]))

                limb_vector_end = ((data.loc[beg_end_tuple[1], (scorer, "Shoulder_{}".format(foot), "x")]
                                    - data.loc[beg_end_tuple[1], (scorer, "{}_knee".format(foot), "x")]),
                                   (data.loc[beg_end_tuple[1], (scorer, "Shoulder_{}".format(foot), "y")]
                                    - data.loc[beg_end_tuple[1], (scorer, "{}_knee".format(foot), "y")]))

                limb_rom_angle_begin = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_begin,
                                                                                 auxiliaryfunctions.calc_body_axis(data,
                                                                                                                   beg_end_tuple[
                                                                                                                       0],
                                                                                                                   scorer))
                limb_rom_angle_end = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_end,
                                                                               auxiliaryfunctions.calc_body_axis(data,
                                                                                                                 beg_end_tuple[
                                                                                                                     1],
                                                                                                                 scorer))
                if limb_rom_angle_begin > 0.0 and limb_rom_angle_end > 0.0:
                    limb_rom = abs(limb_rom_angle_end - limb_rom_angle_begin)
                else:
                    limb_rom = 0.0

                #print('limbROM: ', limb_rom)

            if limb_rom > 0.0:
                for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                    results[foot][row] = limb_rom

        #print('limb ROM foot: ', limb_rom_foot)
        # mean_rom_foot = np.mean(limb_rom_foot)
        # std_rom_foot = np.std(limb_rom_foot)
        #print('foot: ', foot,
        #      'mean: ', mean_rom_foot,
        #      'std: ', std_rom_foot)

    # rename dictionary keys of results
    results = {'limbROM_' + key: value for (key, value) in results.items()}

    return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stride000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value
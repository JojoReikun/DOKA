def center_limb_rom_angle(**kwargs):
    """
    calculates the centre limb range of motion angle which is the angle between the axis at 1/2 of ROM
    and the perpendicular to the body axis. Or in other words: The angle the ROM starts from.
    :param kwargs:
    :return: dictionary with column names as keys and the corresponding values. The 4 key-value pairs represent the
    results for the CROM angle for every foot.
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    use_3_midstride = True

    print('CROM CALCULATION')

    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')

    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]
    max_stride_phase_count = 1000

    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))

    results = {}
    for foot, column in zip(feet, active_columns):
        #print("----- foot, column: ", foot, column)
        column = column.strip('')
        results[foot] = np.full((data_rows_count,), np.NAN)

        for i in range(1, max_stride_phase_count):
            #print('----- stride phase i: ', i)
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            df_stride_section_indices = list(df_stride_section.index.values)
            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                stride_length_in_frames = beg_end_tuple[1] - beg_end_tuple[0]

                # calculate CROMs if strides are at least 4 frames:
                if stride_length_in_frames <= 3:
                    #print("NAN \n")
                    CROM_midstride = np.NAN
                elif stride_length_in_frames % 2 == 0:
                    mid_stride_index = beg_end_tuple[0] + int(stride_length_in_frames / 2.0)
                    #print("midstride index: ", mid_stride_index)
                    CROM_midstride = calc_CROM_angle(data, mid_stride_index, scorer, foot)
                    if use_3_midstride:
                        CROM_midstride_minus = calc_CROM_angle(data, int(mid_stride_index - 1), scorer, foot)
                        CROM_midstride_mid = calc_CROM_angle(data, int(mid_stride_index), scorer, foot)
                        CROM_midstride_plus = calc_CROM_angle(data, int(mid_stride_index + 1), scorer, foot)
                        CROM_midstride = (CROM_midstride_minus + CROM_midstride_mid + CROM_midstride_plus)/3.
                else:
                    mid_stride_index = beg_end_tuple[0] + int((stride_length_in_frames / 2.0) + 0.5)
                    #print("midstride index: ", mid_stride_index)
                    CROM_midstride = calc_CROM_angle(data, mid_stride_index, scorer, foot)
                    if use_3_midstride:
                        CROM_midstride_minus = calc_CROM_angle(data, int(mid_stride_index - 1), scorer, foot)
                        CROM_midstride_mid = calc_CROM_angle(data, int(mid_stride_index), scorer, foot)
                        CROM_midstride_plus = calc_CROM_angle(data, int(mid_stride_index + 1), scorer, foot)
                        CROM_midstride = (CROM_midstride_minus + CROM_midstride_mid + CROM_midstride_plus) / 3.

            for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                results[foot][row] = CROM_midstride

    # rename dictionary keys of results
    results = {'CROM_' + key: value for (key, value) in results.items()}
    print("mean and std FL: ", np.nanmean(results["CROM_FL"]), np.nanstd(results["CROM_FL"]))
    print("mean and std FR: ", np.nanmean(results["CROM_FR"]), np.nanstd(results["CROM_FR"]))
    print("mean and std HR: ", np.nanmean(results["CROM_HR"]), np.nanstd(results["CROM_HR"]))
    print("mean and std HL: ", np.nanmean(results["CROM_HL"]), np.nanstd(results["CROM_HL"]))

    return results


def calc_CROM_angle(data, mid_stride_index, scorer, foot):
    from lizardanalysis.utils import auxiliaryfunctions
    body_axis = auxiliaryfunctions.calc_body_axis(data, mid_stride_index, scorer)
    perpendicular = (body_axis[1] * (-1), body_axis[0])  # rotate body axis by 90 CCW
    shoulder_midstride = (data.loc[mid_stride_index, (scorer, "Shoulder_{}".format(foot), "x")],
                          data.loc[mid_stride_index, (scorer, "Shoulder_{}".format(foot), "y")])
    knee_midstride = (data.loc[mid_stride_index, (scorer, "{}_knee".format(foot), "x")],
                      data.loc[mid_stride_index, (scorer, "{}_knee".format(foot), "y")])
    limb_vector = (shoulder_midstride[0] - knee_midstride[0],
                   shoulder_midstride[1] - knee_midstride[1])
    CROM_midstride = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector, perpendicular)
    if CROM_midstride >= 90.:
        CROM_midstride = 180. - CROM_midstride
    #print("CROM: ", CROM_midstride)
    return CROM_midstride


def loop_encode(i):
    cell_value = 'stride000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value
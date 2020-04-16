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

    #print('CROM CALCULATION')

    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    filename = kwargs.get('filename')

    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]
    max_stride_phase_count = 1000

    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))

    # debug:
    direction = df_result_current.loc[1]["direction_of_climbing"]
    # print("filename: ", filename,
    #       "\ndirection: ", direction)

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

                # calculate the limb ROM angles to then get CROM
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
                                                                                                    beg_end_tuple[0],
                                                                                                    scorer))
                limb_rom_angle_end = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_end,
                                                                                   auxiliaryfunctions.calc_body_axis(data,
                                                                                                  beg_end_tuple[1],
                                                                                                  scorer))
                if limb_rom_angle_begin > 0.0 and limb_rom_angle_end > 0.0:
                    limb_rom = abs(limb_rom_angle_end - limb_rom_angle_begin)
                else:
                    limb_rom = 0.0

                # CROM @ 1/2 ROM:
                if stride_length_in_frames <= 3:
                    CROM_midrom = 0.0
                else:
                    """
                    CROM calculated to bodyaxis ("lower angle"), 90 - CROM to get angle in relation to perpendicular
                    of bodyaxis, hence positive values will be retracted, negative values protracted for direction UP
                    """
                    if np.isnan(limb_rom_angle_begin) == False and np.isnan(limb_rom_angle_begin) == False:
                        CROM_midrom = 90.0 - (limb_rom_angle_end - (limb_rom/2.0))
                    else:
                        CROM_midrom = np.nan
                #print("CROM: ", CROM_midrom)


                # Maximum pro- or retraction:
                # 90 - limb_rom_angle_end

            # debug:
            # print("ROM start: ", limb_rom_angle_begin,
            #       "\nCROM_mid ROM: ", CROM_midrom,
            #       "\nROM end: ", limb_rom_angle_end,
            #       "\nROM: ", limb_rom,
            #       "\n---------------------------------")

            for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                results[foot][row] = CROM_midrom

    # rename dictionary keys of results
    results = {'CROM_' + key: value for (key, value) in results.items()}
    # print("mean and std FL: ", np.nanmean(results["CROM_FL"]), np.nanstd(results["CROM_FL"]))
    # print("mean and std FR: ", np.nanmean(results["CROM_FR"]), np.nanstd(results["CROM_FR"]))
    # print("mean and std HR: ", np.nanmean(results["CROM_HR"]), np.nanstd(results["CROM_HR"]))
    # print("mean and std HL: ", np.nanmean(results["CROM_HL"]), np.nanstd(results["CROM_HL"]))

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
    return CROM_midstride


def calc_CROM_angle_bodyaxis(data, mid_stride_index, scorer, foot):
    # used
    from lizardanalysis.utils import auxiliaryfunctions
    body_axis = auxiliaryfunctions.calc_body_axis(data, mid_stride_index, scorer)
    shoulder_midstride = (data.loc[mid_stride_index, (scorer, "Shoulder_{}".format(foot), "x")],
                          data.loc[mid_stride_index, (scorer, "Shoulder_{}".format(foot), "y")])
    knee_midstride = (data.loc[mid_stride_index, (scorer, "{}_knee".format(foot), "x")],
                      data.loc[mid_stride_index, (scorer, "{}_knee".format(foot), "y")])
    limb_vector = (shoulder_midstride[0] - knee_midstride[0],
                   shoulder_midstride[1] - knee_midstride[1])
    CROM_midstride = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector, body_axis)
    return CROM_midstride


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stride000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value
def lizards_feet_width_and_height(**kwargs):
    """
    calculates the vertical and horizontal distance between the FR and HL foot during mid-stance.
    The distances are calculated along the x and y axis of the video, hence if the lizard climbs at an angle the
    widths and heights might deviate. Use the body_axis_deflection_angle calculation first to get the lizards deflection
    from the vertical and use this as an indicator if values should be excluded in post-analysis.
    This script filters for deflections <= 15 deg if body_axis_deflection_angle is included in selected calculations.
    :param kwargs:
    :return:
    """

    print("spreading")

    # TODO: do the width for fore and hind feet individually

    ### imports
    import numpy as np
    import pandas as pd
    from lizardanalysis.utils import animal_settings, auxiliaryfunctions

    # -------------------- only includes stride lengths longer (>) than... (TODO: make config parameter)
    threshold_stride_len = 4
    # --------------------

    ### setup
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')
    filename = kwargs.get('filename')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    forefeet = [foot for foot in feet if "F" in foot]
    #print("forefeet: ", forefeet)
    max_step_phase_count = 1000

    filter_deflection = False

    if "body_deflection_angle" in df_result_current.columns:
        filter_deflection = True
    #print("filter_deflection = ", filter_deflection)

    active_columns = []
    for foot in forefeet:
        active_columns.append("stepphase_{}".format(foot))

    ##################################################################################################
    results = {}
    result_columns = ["mean_footpair_width", "mean_footpair_height", "mean_footpair_width_F", "mean_footpair_width_H"]
    # generate 4 result columns for result dataframe which will contain widths and heights
    for col in result_columns:
        results[col] = np.full((data_rows_count,), np.NAN)

    stride_lengths = []
    # -----> Loops through feet
    for foot, column in zip(forefeet, active_columns):
        mid_stance_widths_F = []  # takes the 3 mid stance indices and calculated the mean angle
        mid_stance_widths_H = []  # takes the 3 mid stance indices and calculated the mean angle
        mid_stance_heights = []  # takes the 3 mid stance indices and calculated the mean angle
        mid_stance_widths = []  # takes the 3 mid stance indices and calculated the mean angle

        # create one loop for foot = FR (+ foot pair HL) & for for the opposite:
        if foot == "FR":
            hindfoot = "HL"
            forefootpair = "FL"
            hindfootpair = "HR"
            hindfoot_column = "stepphase_{}".format(hindfoot)
            column = column.strip('')
        elif foot == "FL":
            hindfoot = "HR"
            forefootpair = "FR"
            hindfootpair = "HL"
            hindfoot_column = "stepphase_{}".format(hindfoot)

        column = column.strip('')

        for i in range(1, max_step_phase_count):

            cell_value = loop_encode(i)
            # finds the segment in the dataframe where the step phase equals the current step phase in the loop
            df_stance_section = df_result_current[df_result_current[column] == cell_value]

            if len(df_stance_section) == 0:
                break

            df_stance_section_indices = list(df_stance_section.index.values)  # contains all frames of stride phase
            if len(df_stance_section_indices) > 0:
                stance_length = len(df_stance_section_indices)
                #print(i, ": stance length {}|{}: ".format(foot, hindfoot), stance_length)

                beg_end_tuple = (df_stance_section_indices[0], df_stance_section_indices[-1])


                # get the middle of the stance:
                if stance_length % 2 == 0:
                    mid_stance_index = beg_end_tuple[1] - stance_length / 2
                else:
                    mid_stance_index = int((beg_end_tuple[1] - stance_length / 2.0) + 0.5)

                # check if the body deflection of lizard is less than or equal to 15 deg:
                deflection = df_stance_section.loc[mid_stance_index, "body_deflection_angle"]
                if filter_deflection and deflection <= 15.0:
                    # check the likelihood for the foot label at the mid-stance index:
                    forefoot_likelihood = data.loc[mid_stance_index, (scorer, foot, "likelihood")]
                    hindfoot_likelihood = data.loc[mid_stance_index, (scorer, hindfoot, "likelihood")]
                    forefootpair_likelihood = data.loc[mid_stance_index, (scorer, forefootpair, "likelihood")]

                    if forefoot_likelihood >= likelihood and hindfoot_likelihood >= likelihood and forefootpair_likelihood >= likelihood:
                        # get the foot coordinates for fore- and hindfoot at the mid-stance index:
                        fore_foot_coords = (data.loc[mid_stance_index, (scorer, foot, "x")],
                                            data.loc[mid_stance_index, (scorer, foot, "y")])
                        hind_foot_coords = (data.loc[mid_stance_index, (scorer, hindfoot, "x")],
                                            data.loc[mid_stance_index, (scorer, hindfoot, "y")])
                        fore_foot_pair_coords = (data.loc[mid_stance_index, (scorer, forefootpair, "x")],
                                            data.loc[mid_stance_index, (scorer, forefootpair, "y")])
                        hind_foot_pair_coords = (data.loc[mid_stance_index, (scorer, hindfootpair, "x")],
                                            data.loc[mid_stance_index, (scorer, hindfootpair, "y")])
                    else:
                        fore_foot_coords = (np.nan, np.nan)
                        hind_foot_coords = (np.nan, np.nan)
                        fore_foot_pair_coords = (np.nan, np.nan)
                        hind_foot_pair_coords = (np.nan, np.nan)

                    # calculate the width and height
                    # the lizards run/climb along the x-axis, therefore width = y and height = x
                    height = abs(fore_foot_coords[0] - hind_foot_coords[0])
                    width = abs(fore_foot_coords[1] - hind_foot_coords[1])
                    width_F = abs(fore_foot_coords[1] - fore_foot_pair_coords[1])
                    width_H = abs(hind_foot_coords[1] - hind_foot_pair_coords[1])

                    mid_stance_heights.append(round(height, 2))
                    mid_stance_widths.append(round(width, 2))
                    mid_stance_widths_F.append(round(width_F, 2))
                    mid_stance_widths_H.append(round(width_H, 2))

                else:
                    print(i, ": the lizard does not climbed aligned to vertical {} ... {}".format(deflection, filename))

    mean_width = np.mean(mid_stance_widths)
    mean_height = np.mean(mid_stance_heights)
    mean_width_F = np.mean(mid_stance_widths_F)
    mean_width_H = np.mean(mid_stance_widths_H)

    #print("mean width and height: ", mean_width, mean_height)

    for row in range(data_rows_count):
        results[result_columns[0]][row] = mean_width
        results[result_columns[1]][row] = mean_height
        results[result_columns[2]][row] = mean_width_F
        results[result_columns[3]][row] = mean_width_H

    #print(results)

    return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stance000{}'.format(i).encode()
    #print("-----> stance phase cell value :", cell_value)
    return cell_value
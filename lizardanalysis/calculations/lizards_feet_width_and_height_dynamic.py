def lizards_feet_width_and_height_dynamic(**kwargs):
    """
    calculates the vertical and horizontal distance between the FR and HL foot over the entire stance frame-wise.
    The distances are calculated along the x and y axis of the video, hence if the lizard climbs at an angle the
    widths and heights might deviate. Use the body_axis_deflection_angle calculation first to get the lizards deflection
    from the vertical and use this as an indicator if values should be excluded in post-analysis.
    This script filters for deflections <= 15 deg if body_axis_deflection_angle is included in selected calculations.
    :param kwargs:
    :return:
    """

    print("dynamic width and height of feet")

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
    max_step_phase_count = 1000

    # Interestingly the scorer is all lower case in here, which is why cells can't be located.
    # Move calculation up in order (in animal_settings.py).
    #print("SCORER: ", scorer)

    filter_deflection = False

    if "body_deflection_angle" in df_result_current.columns:
        filter_deflection = True
    # print("filter_deflection = ", filter_deflection)

    forefeet = ["FL", "FR"]

    active_columns = []
    for foot in forefeet:
        active_columns.append("stepphase_{}".format(foot))

    ##################################################################################################
    results = {}
    result_columns = ["dyn_footpair_width_FL", "dyn_footpair_height_FL",
                      "dyn_footpair_width_FR", "dyn_footpair_height_FR"]
    # generate 4 result columns for result dataframe which will contain widths and heights
    for col in result_columns:
        results[col] = np.full((data_rows_count,), np.NAN)

    stride_lengths = []
    # -----> Loops through feet, looks at one stepphase column at the time
    for foot, column in zip(forefeet, active_columns):
        #print(f"\n1) <------------------ column: {column} ----------------->\n")
        # column = column.strip('')

        # create one loop for foot = FR (+ foot pair HL) & for for the opposite:
        if foot == "FR":
            hindfoot = "HL"
            column = column.strip('')

        elif foot == "FL":
            hindfoot = "HR"
            column = column.strip('')

        for i in range(1, max_step_phase_count):
            stance_heights = []  # adds value for each frame for current stance phase to array
            stance_widths = []

            cell_value = loop_encode(i)
            # finds the segment in the dataframe where the step phase equals the current step phase in the loop
            #print(f"2) column: {column}, cell_value: {cell_value}")
            #print("df result current of column: \n", df_result_current[column], "\n")
            df_stance_section = df_result_current[df_result_current[column] == cell_value]
            #print("stance section: \n", df_stance_section[column])

            if len(df_stance_section) == 0:
                #print("stance section is length 0... break")
                break

            else:
                df_stance_section_indices = list(df_stance_section.index.values)  # contains all frames of stance phase
                stance_length = len(df_stance_section_indices)
                # print(i, ": stance length {}|{}: ".format(foot, hindfoot), stance_length)

                #print(f"3) column: {column}, foot: {foot}, cell_value: {cell_value}, stance section: {df_stance_section_indices}\n")

                beg_end_tuple = (df_stance_section_indices[0], df_stance_section_indices[-1])

                for frame in df_stance_section_indices:
                    # check if the body deflection of lizard is less than or equal to 15 deg:
                    deflection = df_stance_section.loc[frame, "body_deflection_angle"]
                    if filter_deflection and deflection <= 15.0:
                        # check the likelihood for the foot label at index:
                        forefoot_likelihood = data.loc[frame, (scorer, foot, "likelihood")]
                        hindfoot_likelihood = data.loc[frame, (scorer, hindfoot, "likelihood")]

                        if forefoot_likelihood >= likelihood and hindfoot_likelihood >= likelihood:
                            # get the foot coordinates for fore- and hindfoot at the mid-stance index:
                            fore_foot_coords = (data.loc[frame, (scorer, foot, "x")],
                                                data.loc[frame, (scorer, foot, "y")])
                            hind_foot_coords = (data.loc[frame, (scorer, hindfoot, "x")],
                                                data.loc[frame, (scorer, hindfoot, "y")])

                            # calculate the width and height
                            # the lizards run/climb along the x-axis, therefore width = y and height = x
                            # distance between attached feet in direction of climbing, needed for dynamic of stride calculations
                            height = abs(fore_foot_coords[0] - hind_foot_coords[0])
                            width = abs(fore_foot_coords[1] - hind_foot_coords[1])

                            stance_heights.append(round(height, 2))
                            stance_widths.append(round(width, 2))

                            if height > 0.0 and width > 0.0:
                                # ADD THE RESULT VALUE TO SPECIFIC ROW IN RESULTS
                                if foot == "FL":
                                    results["dyn_footpair_width_FL"][frame] = width
                                    results["dyn_footpair_height_FL"][frame] = height
                                else:
                                    results["dyn_footpair_width_FR"][frame] = width
                                    results["dyn_footpair_height_FR"][frame] = height

                        else:
                            # if deflection too large or likelihood of feet too bad:
                            fore_foot_coords = (np.nan, np.nan)
                            hind_foot_coords = (np.nan, np.nan)

                    else:
                        #print(i, ": the lizard does not climbed aligned to vertical {} ... {}".format(deflection, filename))
                        continue

                #print(f"column: {column}, cell_value: {cell_value}, heights: {stance_heights}, widths: {stance_widths}")

    return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stance000{}'.format(i).encode()
    # print("-----> stance phase cell value :", cell_value)
    return cell_value

def tail_kinematics(**kwargs):
    """
    calculates the tail angular amplitude, velocity and acceleration of the TCOM relative to the body axis.
    The average TCOM location of the lizards is ~30% (get correct value).
    Given that we have 4 labels along the tail (Tail_A, Tail_B, Tail_C, Tail_Tip), where A is 25% tailLength, B 50%,
    C 75% and Tip 100%, the rough TCOM label is between Tail_A and Tail_B.
    We did not use the exact TCOM position in percent to average this, because the label positions on the tail jump
    a bit during tracking.
    :return: tail_angular_amplitude, tail_angular_velocity, tail_angular_acceleration
    """
    ### IMPORTS
    from lizardanalysis.utils import auxiliaryfunctions
    import pandas as pd
    import numpy as np

    print("tail kinematics")

    ### SETUP
    config = kwargs.get('config')
    likelihood = kwargs.get('likelihood')
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    scorer = data.columns[1][0]

    tail_kinematic_params = ["tail_angular_amplitude", "tail_angular_velocity", "tail_angular_acceleration"]
    results = {}
    for param in tail_kinematic_params:
        results[param] = np.full((data_rows_count,), np.NAN)

    ### Calculations

    # estimate the TCOM label position
    tcom_x, tcom_y = auxiliaryfunctions.estimate_TCOM_label_coords(data.loc[:, (scorer, 'Tail_A', "x")],
                                                                   data.loc[:, (scorer, 'Tail_A', 'y')],
                                                                   data.loc[:, (scorer, 'Tail_B', 'x')],
                                                                   data.loc[:, (scorer, 'Tail_B', 'y')])

    # for every frame
    for index in range(len(tcom_x)):
        # build a TCOM vector
        likelihood_hip = data.loc[index, (scorer, "Hip", "likelihood")]
        likelihood_tail_a = data.loc[index, (scorer, "Tail_A", "likelihood")]
        likelihood_tail_b = data.loc[index, (scorer, "Tail_B", "likelihood")]
        if likelihood_hip >= likelihood and likelihood_tail_a >= likelihood and likelihood_tail_b >= likelihood:
            tcom_vector = ((data.loc[index, (scorer, "Hip", "x")] - tcom_x[index]),
                           (data.loc[index, (scorer, "Hip", "y")] - tcom_y[index]))
            print("TCOM vector: ", tcom_vector)
        else:
            tcom_vector = (np.nan, np.nan)

        # get the body axis vector
        body_axis_vector = auxiliaryfunctions.calc_body_axis(data, index, scorer)

        # calculate the angle between the two
        # TODO: find out which values mean which (+ vs -)
        angle_deg = auxiliaryfunctions.py_angle_betw_2vectors_atan(body_axis_vector, tcom_vector)

        # add angle to results dataframe
        results[tail_kinematic_params[0]][index] = angle_deg
    print("angular amplitudes: ", results[tail_kinematic_params[0]])
    print("length of amplitudes: ", len(results[tail_kinematic_params[0]]))

    # calculate the anglular velocity from amplitude list
    dy = np.diff(results[tail_kinematic_params[0]])
    np.append(dy, np.nan)
    for index, val in enumerate(dy):
        results[tail_kinematic_params[1]][index] = val

    # calculate the angular acceleration from velocity list
    ddy = np.diff(results[tail_kinematic_params[1]])
    np.append(ddy, np.nan)
    for index, val in enumerate(ddy):
        results[tail_kinematic_params[2]][index] = val

    print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in results.items()) + "}")

    return results
def knee_and_elbow_angles(**kwargs):
    """
    calculates the knee and elbow angles for every frame.
    Knee angle: angle between limb vector (Shoulder_foot<->foot_knee) and foot vector (foot_knee<->foot)
    :param kwargs: different parameters needed for calculation
    :return: results dataframe with 4 key value pairs (list of frame-wise angles for every foot)
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    #print('KNEE AND ELBOW ANGLE CALCULATION')
    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    likelihood = kwargs.get('likelihood')
    filename = kwargs.get('filename')
    animal = kwargs.get('animal')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)

    results = {}

    for foot in feet:
        results[foot] = np.full((data_rows_count,), np.NAN)

        for i in range(data_rows_count):
            # test for likelihoods:
            foot_likelihood = data.loc[i][scorer, foot, "likelihood"]
            shoulder_foot_likelihood = data.loc[i][scorer, "Shoulder_{}".format(foot), "likelihood"]
            knee_foot_likelihood = data.loc[i][scorer, "{}_knee".format(foot), "likelihood"]

            # get limb vector (shoulder - shoulder_foot or hip - shoulder_foot)
            # only calculate if likelihoods of involved tracking points are good enough else nan
            if shoulder_foot_likelihood >= likelihood and knee_foot_likelihood >= likelihood:
                limb_vector = ((data.loc[i, (scorer, "Shoulder_{}".format(foot), "x")]
                                - data.loc[i, (scorer, "{}_knee".format(foot), "x")]),
                               (data.loc[i, (scorer, "Shoulder_{}".format(foot), "y")]
                                - data.loc[i, (scorer, "{}_knee".format(foot), "y")]))
                # print("limb vector: ", limb_vector)
            else:
                limb_vector = (np.nan, np.nan)

            # get foot vector:
            # only calculate if likelihoods of involved tracking points are good enough else nan
            if foot_likelihood >= likelihood and knee_foot_likelihood >= likelihood:
                foot_vector = ((data.loc[i, (scorer, "{}_knee".format(foot), "x")]
                                - data.loc[i, (scorer, foot, "x")]),
                               (data.loc[i, (scorer, "{}_knee".format(foot), "y")]
                                - data.loc[i, (scorer, foot, "y")]))
            else:
                foot_vector = (np.nan, np.nan)

            # calculate the shoulder/hip angle
            knee_angle = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector, foot_vector)
            #print("Foot: ", foot, "knee_angle: ", knee_angle)

            # print("shoulder angle: ", shoulder_angle)

            results[foot][i] = 180.0 - knee_angle

    # rename dictionary keys of results
    results = {'knee_angle_' + key: value for (key, value) in results.items()}

    return results

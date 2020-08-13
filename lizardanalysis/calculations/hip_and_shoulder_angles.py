def hip_and_shoulder_angles(**kwargs):
    """
    calculates the shoulder and hip angles for every frame.
    Shoulder angle: angle between shoulder vector (FORE: Shoulder<->Shoulder_foot  or   HIND: Hip<->Shoulder_foot)
    and limb vector (Shoulder_foot<->foot_knee)
    :param kwargs: different parameters needed for calculation
    :return: results dataframe with 4 key value pairs (list of frame-wise angles for every foot)
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    #print('HIP AND SHOULDER ANGLE CALCULATION')
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
            shoulder_likelihood = data.loc[i][scorer, "Shoulder", "likelihood"]
            shoulder_foot_likelihood = data.loc[i][scorer, "Shoulder_{}".format(foot), "likelihood"]
            knee_foot_likelihood = data.loc[i][scorer, "{}_knee".format(foot), "likelihood"]
            hip_likelihood = data.loc[i][scorer, "Hip", "likelihood"]

            # get shoulder vector (shoulder - shoulder_foot or hip - shoulder_foot)
            if foot == "FR" or foot == "FL":
                # only calculate if likelihoods of involved tracking points are good enough else nan
                if shoulder_likelihood >= likelihood and shoulder_foot_likelihood >= likelihood:
                    shoulder_vector = ((data.loc[i, (scorer, "Shoulder", "x")]
                                        - data.loc[i, (scorer, "Shoulder_{}".format(foot), "x")]),
                                       (data.loc[i, (scorer, "Shoulder", "y")]
                                        - data.loc[i, (scorer, "Shoulder_{}".format(foot), "y")]))
                    #print("shoulder vector: ", shoulder_vector)
                else:
                    shoulder_vector = (np.nan, np.nan)
            else:   # use HIP
                # only calculate if likelihoods of involved tracking points are good enough else nan
                if hip_likelihood >= likelihood and shoulder_foot_likelihood >= likelihood:
                    shoulder_vector = ((data.loc[i, (scorer, "Hip", "x")]
                                        - data.loc[i, (scorer, "Shoulder_{}".format(foot), "x")]),
                                       (data.loc[i, (scorer, "Hip", "y")]
                                        - data.loc[i, (scorer, "Shoulder_{}".format(foot), "y")]))
                    #print("hip vector: ", shoulder_vector)
                else:
                    shoulder_vector = (np.nan, np.nan)
            # get limb vector (shoulder_foot - foot_knee)
            if shoulder_foot_likelihood >= likelihood and knee_foot_likelihood >= likelihood:
                limb_vector = ((data.loc[i, (scorer, "Shoulder_{}".format(foot), "x")]
                                - data.loc[i, (scorer, "{}_knee".format(foot), "x")]),
                               (data.loc[i, (scorer, "Shoulder_{}".format(foot), "y")]
                                - data.loc[i, (scorer, "{}_knee".format(foot), "y")]))
                #print("limb vector: ", limb_vector)
            else:
                limb_vector = (np.nan, np.nan)
            #print("shoulder vector, limb vector: ", shoulder_vector, limb_vector)
            # calculate the shoulder/hip angle
            shoulder_angle = auxiliaryfunctions.py_angle_betw_2vectors(shoulder_vector, limb_vector)

            #print("shoulder angle: ", shoulder_angle)

            results[foot][i] = 180.0 - shoulder_angle

    # rename dictionary keys of results
    results = {'shoulder_angle_' + key: value for (key, value) in results.items()}

    return results
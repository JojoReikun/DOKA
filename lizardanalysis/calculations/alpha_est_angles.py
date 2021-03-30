def alpha_est_angles(**kwargs):
    """
    calculates the rom angle for every frame
    rom angle: angle between the body (i.e. head - abdomen) and
    the vector formed between the coxa and tarsus labels
    therefore, elevation/depression at the trochanter is ignored.

    the angle is based on the rotation about the coxa, therefore the vector stops at the coxa,
    not the thorax

    :param kwargs: different parameters need for calculation
    :return: results dataframe with 6 key value pairs (list of frame-wise angles for every foot)
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    likelihood = kwargs.get('likelihood')
    filename = kwargs.get('filename')
    animal = kwargs.get('animal')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)

    # results will be stored into a key value pair dictionary
    results = {}

   # SHOULD I PASS THROUGH A LOW PASS FILTER FIRST?

    for foot in feet:
        # creating a key for each foot, and the the corresponding value is currently an array filled with data_rows_count
        # many NANs
        results[foot] = np.full((data_rows_count),np.NAN)
        #is the extra comma needed here?

        for i in range(data_rows_count):

            foot_chars = list(foot)

            # this will split the foot into the letter l or r, and then number 1,2, or 3, stored in an array
            femur_likelihood = data.loc[i][scorer,foot, "likelihood"]
            coxa_likelihood = data.loc[i][scorer, "{}b{}".format(foot_chars[0],foot_chars[1]), "likelihood"]

            if femur_likelihood >= likelihood and coxa_likelihood >= likelihood:
                femur_vector = ((data.loc[i, (scorer, foot ,"x" )]
                 - data.loc[i][scorer, f"{foot_chars[0]}b{foot_chars[1]}", "x" ]),
                                 (data.loc[i][ scorer, foot , "y"]
                                    - data.loc[i][scorer, "{}b{}".format(foot_chars[0],foot_chars[1]),"y"]))

            else:
                femur_vector = (np.NAN, np.NAN)

            head_likelihood = data.loc[i][scorer, "head", "likelihood"]
            abdomen_likelihood = data.loc[i][scorer, "abdomen", "likelihood"]
             # can just use the whole body vector under the assumption that the body is rigid
            # i.e. no relative movement of the thoraxes

            if head_likelihood >= likelihood and abdomen_likelihood >= likelihood:
                body_vector = ((data.loc[i][scorer, "head", "x"]-data.loc[i][ scorer, "abdomen", "x"]),
                             - (data.loc[i][scorer,"head", "y"]- data.loc[i][ scorer,"abdomen", "y"]))

            # therefore at this point there should be a vector between the femur and coxa,
            # and a vector that runs along the body
                # these two vectors will be used to calculate the angle between the femur and the body

            else:
                body_vector = (np.NAN, np.NAN)

            rom_est = auxiliaryfunctions.py_angle_betw_2vectors(body_vector, femur_vector)



            results[foot][i] = 180.0 - rom_est

            #rename dictionary keys of results
    results = {"alpha_angle_" + key: value for (key,value) in results.items()}
    return results

def tail_biomech_angles(**kwargs):
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    #print('tail_angles')

    # for lizards:
    tail_angles = ['cranial_bA', 'prox_bA', 'tip_bA', 'prox_dist', 'dist_bA', 'cranial_caudal']
    # dictionary to define which label points are needed for building the vectors
    tail_angle_vector_points = {'cranial_bA': ['Hip', 'Shoulder', 'Spine'],
                                'prox_bA': ['Hip', 'Shoulder', 'Tail_middle'],
                                'tip_bA': ['Hip', 'Shoulder', 'Tail_tip'],
                                'prox_dist': ['Hip', 'Tail_middle', 'Tail_tip'],
                                'dist_bA': ['Tail_middle', 'Tail_tip', 'Hip', 'Shoulder'],
                                'cranial_caudal': ['Hip', 'Shoulder', 'Spine']}
    # dictionary to define vectors and needed labels
    tail_angle_vectors = {'cranial_bA': (['Shoulder', 'Spine'], ['Shoulder', 'Hip']),
                          'prox_bA': (['Hip', 'Tail_middle'], ['Shoulder', 'Hip']),
                          'tip_bA': (['Hip', 'Tail_tip'], ['Shoulder', 'Hip']),
                          'prox_dist': (['Hip', 'Tail_middle'], ['Tail_middle', 'Tail_tip']),
                          'dist_bA': (['Tail_middle', 'Tail_tip'], ['Shoulder', 'Hip']),
                          'cranial_caudal': (['Shoulder', 'Spine'], ['Spine', 'Hip'])}

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')

    scorer = data.columns[1][0]

    results = {}

    for angle in tail_angles:
        results[angle] = np.full((data_rows_count,), np.NAN)

    for row in range(1, data_rows_count):

        likelihood_boolean = {}
        for angle in tail_angles:
            nr_of_labels = len(tail_angle_vector_points[angle])
            #print('angle: ', angle)

            # likelihood:
            for n in range(nr_of_labels):
                #print(n)
                #print(tail_angle_vector_points[angle][n])
                if data.loc[row][scorer, tail_angle_vector_points[angle][n], 'likelihood'] >= likelihood:
                    likelihood_boolean[tail_angle_vector_points[angle][n]] = "TRUE"
                else:
                    likelihood_boolean[tail_angle_vector_points[angle][n]] = "FALSE"
            #print("likelihood_boolean: ", likelihood_boolean)

            # build the segment vectors if likelihood is good enough, otherwise fill with nan
            # 1st vector:
            if likelihood_boolean[tail_angle_vectors[angle][0][0]] == "TRUE" and likelihood_boolean[
                tail_angle_vectors[angle][0][1]] == "TRUE":
                vector_1 = ((data.loc[row, (scorer, tail_angle_vectors[angle][0][0], "x")] - data.loc[
                            row, (scorer, tail_angle_vectors[angle][0][1], "x")]),
                            (data.loc[row, (scorer, tail_angle_vectors[angle][0][0], "y")] - data.loc[
                            row, (scorer, tail_angle_vectors[angle][0][1], "y")]))
            else:
                vector_1 = (np.nan, np.nan)

            # 2nd vector:
            if likelihood_boolean[tail_angle_vectors[angle][1][0]] == "TRUE" and likelihood_boolean[
                tail_angle_vectors[angle][1][1]] == "TRUE":
                vector_2 = ((data.loc[row, (scorer, tail_angle_vectors[angle][1][0], "x")] - data.loc[
                            row, (scorer, tail_angle_vectors[angle][1][1], "x")]),
                            (data.loc[row, (scorer, tail_angle_vectors[angle][1][0], "y")] - data.loc[
                            row, (scorer, tail_angle_vectors[angle][1][1], "y")]))
            else:
                vector_2 = (np.nan, np.nan)

            # calculate the angle between the vectors:
            angle_deg = auxiliaryfunctions.py_angle_betw_2vectors_atan(vector_1, vector_2)
            results[angle][row] = angle_deg

    #print("results: ", results)
    return results

def body_axis_deflection_angle(**kwargs):
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')

    scorer = data.columns[1][0]
    #auxiliaryfunctions.strip_scorer_column_counter(data, scorer)

    results = {}
    results['body_deflection_angle'] = np.full((data_rows_count,), np.NAN)

    # create dictionary and save tuples with nose coordinates for every data_row
    body_axes = []
    likelihoods = []
    for i in range(data_rows_count):
        body_axes.append(auxiliaryfunctions.calc_body_axis(data, i, scorer))
        shoulder_likelihood = data.loc[i, (scorer, "Shoulder", "likelihood")]
        hip_likelihood = data.loc[i, (scorer, "Hip", "likelihood")]
        likelihoods.append((shoulder_likelihood, hip_likelihood))
        i += 1

    #print("length of body axes, length of data_rows_count: ", len(body_axes), data_rows_count)

    for j in range(data_rows_count):
        deflection_angle = auxiliaryfunctions.calculate_gravity_deflection_angle(body_axes[j])
        #print("deflection_angle OLD: ", deflection_angle)
        if deflection_angle >= 90.:
            #print("likelihood_shoulder, likelihood_hip, deflection_angle: ", likelihoods[j], 180. - deflection_angle)
            results['body_deflection_angle'][j] = (180. - deflection_angle)
        else:
            #print("likelihood_shoulder, likelihood_hip, deflection_angle: ", likelihoods[j], deflection_angle)
            results['body_deflection_angle'][j] = (deflection_angle)

    #print("mean deflection: ", np.nanmean(results['body_deflection_angle']))

    return results
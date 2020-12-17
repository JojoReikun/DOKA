def point_amplitudes_to_bA(**kwargs):
    """
    calculates the distance from the label to the body axis to use these amplitudes to look at undulatory motion of
    trunk and tail of lizards.
    :param kwargs:
    :return:
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    likelihood = kwargs.get('likelihood')

    scorer = data.columns[1][0]

    # define list of points for which to get frame-wise amplitude to body axis
    points = ['Spine', 'Tail_middle', 'Tail_tip']

    # ceate empty result dict
    results = {}
    for point in points:
        results[point] = np.full((data_rows_count,), np.NAN)

    # create dict to store likelihood values for "shoulder", "hip", and point
    for row in range(1, data_rows_count):
        for point in points:
            if data.loc[row][scorer, point, 'likelihood'] >= likelihood:
                # get the perpendicular dist to the body axis
                dist = auxiliaryfunctions.get_perpendicular_dist_to_vector(point, data, row, scorer)
                results[point][row] = dist
            else:
                results[point][row] = np.nan

    # rename dictionary keys of results
    results = {'amplitude_' + key: value for (key, value) in results.items()}

    return results
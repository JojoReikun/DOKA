def com_speed_stick(**kwargs):
    """
    calculates the framewise body speed of the spider in mm/s
    :param kwargs:
    :return:
    """
    from lizardanalysis.utils import auxiliaryfunctions
    import numpy as np
    from pathlib import Path

    data = kwargs.get("data")
    data_rows_count = kwargs.get("data_rows_count")
    config = kwargs.get('config')
    likelihood = kwargs.get('likelihood')
    filename = kwargs.get('filename')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)

    scorer = data.columns[1][0]
    framerate = cfg['framerate']
    plotting = False

    results = {"com_speed_stick": np.full((data_rows_count,), 0.0, dtype='float')}

    # find conversion factor for stick insect:
    # conv_fac = auxiliaryfunctions.find_conversion_factor_for_stick(filename)

    # create dictionary and save tuples with the metathorax coordinates for every data_row
    t3_coords = {}
    for i in range(data_rows_count):
        t3_coords[i] = (data.loc[i][scorer, 't3', 'x'], data.loc[i][scorer, 't3', 'y'])

    body_speeds = []
    for row, coord in zip(range(1, len(t3_coords)), t3_coords):
        t3_likelihood = data.loc[row][scorer, 't3', 'likelihood']
        t3_rowminusone_likelihood = data.loc[row - 1][scorer, 't3', 'likelihood']

        # only include tracking points with a likelihood >= limit
        # calculate nose speed
        if t3_likelihood >= likelihood and t3_rowminusone_likelihood >= likelihood:
            # calculate eucledean distance for every frame and save it to correct index in result dataframe
            xdiff = abs(t3_coords[row][0] - t3_coords[row - 1][0])
            ydiff = abs(t3_coords[row][1] - t3_coords[row - 1][1])
            distance_calib = np.sqrt(xdiff ** 2 + ydiff ** 2)  # remember to change back to distance

            # calibrate distance with conversion factor
            # distance_calib = distance / conv_fac
            results["com_speed_stick"][row] = auxiliaryfunctions.calculate_speed(distance_calib, framerate)
        else:
            results["com_speed_stick"][row] = np.nan

        # rename dictionary keys of results
        results = {key + '_MMperS': value for (key, value) in results.items()}

        # print('results: ', results)

        return results

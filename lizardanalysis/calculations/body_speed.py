from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis.utils import animal_settings

def body_speed(**kwargs):
    """
    calculates the framewise body speed of the spider in mm/s
    :param kwargs:
    :return:
    """
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

    results = {}
    results["body_speed"] = np.full((data_rows_count,), 0.0, dtype='float')

    # find conversion factor for spider:
    conv_fac = auxiliaryfunctions.find_conversion_factor_for_spider(filename)

    # create dictionary and save tuples with body coordinates for every data_row
    body_coords = {}
    for i in range(data_rows_count):
        body_coords[i] = (data.loc[i][scorer, 'Body', 'x'], data.loc[i][scorer, 'Body', 'y'])
        i += 1

    body_speeds = []
    for row, coord in zip(range(1, len(body_coords)), body_coords):
        body_likelihood = data.loc[row][scorer, 'Body', 'likelihood']
        body_rowminusone_likelihood = data.loc[row-1][scorer, 'Body', 'likelihood']

        # only include tracking points with a likelihood >= limit
        # calculate nose speed
        if body_likelihood >= likelihood and body_rowminusone_likelihood >= likelihood:
            # calculate eucledean distance for every frame and save it to correct index in result dataframe
            xdiff = abs(body_coords[row][0] - body_coords[row - 1][0])
            ydiff = abs(body_coords[row][1] - body_coords[row - 1][1])
            distance = np.sqrt(xdiff ** 2 + ydiff ** 2)

            # calibrate distance with conversion factor
            distance_calib = distance / conv_fac
            results["body_speed"][row] = calculate_speed(distance_calib, framerate)
        else:
            results["body_speed"][row] = np.nan

    # rename dictionary keys of results
    results = {key + '_MMperS': value for (key, value) in results.items()}

    #print('results: ', results)

    return results


def calculate_speed(distance_calib, framerate):
    # calculate the speed in mm/second
    speed = distance_calib/framerate
    retval = speed
    return retval
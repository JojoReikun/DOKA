import numpy as np

# TODO: calculate frame wise for step-phases not average over all! Or do both in 2 different functions
def climbing_speed_framewise(**kwargs):
    """
        Uses the Nose tracking point to determine the climbing speed for every frame
        Take the eucledean distance covered between two frames
        :return: dictionary with function name (key) and list (len=data_rows_count) of climbing speeds in px/s
        for every frame for every foot
        #TODO: Add conversion factor for px in m
    """
    import os
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    config = kwargs.get('config')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    framerate = cfg['framerate']

    scorer = data.columns[1][0]

    results = {}
    results['speed'] = np.full((data_rows_count,), np.NAN)

    # create dictionary and save tuples with nose coordinates for every data_row
    nose_coords = {}
    for i in range(data_rows_count):
        nose_coords[i] = (data.loc[i][scorer, 'Nose', 'x'], data.loc[i][scorer, 'Nose', 'y'])
        i += 1
    #print('nose coordinates: ', nose_coords)

    for j, coord in zip(range(1, len(nose_coords)), nose_coords):
    #calculate eucledean distance for every frame and save it to correct index in result dataframe
        xdiff = abs(nose_coords[j][0] - nose_coords[j - 1][0])
        ydiff = abs(nose_coords[j][1] - nose_coords[j - 1][1])
        distance = np.sqrt(xdiff ** 2 + ydiff ** 2)
        results['speed'][j] = round(distance*framerate, 2)    # *framerate for px/s
        # copy second row into first row and second last into last row of each array
        results['speed'][0] = results['speed'][1]
        results['speed'][-1] = results['speed'][-2]
    # rename dictionary keys of results
    results = {key + '_PXperS': value for (key, value) in results.items()}
    #print('results speed: ', results)

    return results
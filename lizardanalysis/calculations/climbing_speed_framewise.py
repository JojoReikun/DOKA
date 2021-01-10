import numpy as np


# TODO: calculate frame wise for step-phases not average over all! Or do both in 2 different functions
def climbing_speed_framewise(**kwargs):
    """
        Uses the Hip tracking point to determine the climbing speed for every frame
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
    likelihood = kwargs.get('likelihood')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    framerate = cfg['framerate']

    scorer = data.columns[1][0]

    results = {}
    results['speed'] = np.full((data_rows_count,), np.NAN)

    # create dictionary and save tuples with nose coordinates for every data_row
    nose_coords = {}
    hip_coords = {}
    for i in range(data_rows_count):
        nose_coords[i] = (data.loc[i][scorer, 'nose', 'x'], data.loc[i][scorer, 'nose', 'y'])
        hip_coords[i] = (data.loc[i][scorer, 'Hip', 'x'], data.loc[i][scorer, 'Hip', 'y'])
        i += 1
    #print('nose coordinates: ', nose_coords)

    bad_likelihood_counter_nose = []
    bad_likelihood_counter_hip = []
    nose_speeds = []
    hip_speeds = []
    for j, coord in zip(range(1, len(nose_coords)), nose_coords):
        nose_likelihood = data.loc[j][scorer, 'nose', 'likelihood']
        hip_likelihood = data.loc[j][scorer, 'Hip', 'likelihood']
        # only include tracking points with a likelihood >= limit
        # calculate nose speed
        if nose_likelihood >= likelihood:
            # calculate eucledean distance for every frame and save it to correct index in result dataframe
            xdiff = abs(nose_coords[j][0] - nose_coords[j - 1][0])
            ydiff = abs(nose_coords[j][1] - nose_coords[j - 1][1])
            distance = np.sqrt(xdiff ** 2 + ydiff ** 2)
            nose_speeds.append(round(distance * framerate, 2))  # *framerate for px/s
        else:
            bad_likelihood_counter_nose.append(1)
            nose_speeds.append(np.nan)

        # calculate hip speed
        if hip_likelihood >= likelihood:
            xdiff = abs(hip_coords[j][0] - hip_coords[j - 1][0])
            ydiff = abs(hip_coords[j][1] - hip_coords[j - 1][1])
            distance = np.sqrt(xdiff ** 2 + ydiff ** 2)
            hip_speeds.append(round(distance * framerate, 2))  # *framerate for px/s
        else:
            bad_likelihood_counter_hip.append(1)
            hip_speeds.append(np.nan)

    #print('nose_speeds: ', nose_speeds,
    #      '\nhip_speeds: ', hip_speeds,)

    # results
    average_speeds = []
    for i in range(len(nose_speeds)):
    # TODO: change to account for case when nose == Nan
        if np.isnan(hip_speeds[i]) == True:
            average_speed = nose_speeds[i]
        else:
            average_speed = (nose_speeds[i] + hip_speeds[i])/2.0
        average_speeds.append(average_speed)

        results['speed'][i] = average_speed

    #print('average_speeds: ', average_speeds)

    #print('exluded frames for bad likelihood: ',
    #      '\nNose: ', len(bad_likelihood_counter_nose), 'Hip: ', len(bad_likelihood_counter_hip))

    # copy second row into first row and second last into last row of each array
    results['speed'][0] = results['speed'][1]
    results['speed'][-1] = results['speed'][-2]

    # rename dictionary keys of results
    results = {key + '_PXperS': value for (key, value) in results.items()}
    #print('results speed: ', results)

    return results
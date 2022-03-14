import numpy as np


# TODO: calculate frame wise for step-phases not average over all! Or do both in 2 different functions
def climbing_speed_framewise_splitaxes(**kwargs):
    """
        Uses the Nose and the Hip tracking point to determine the climbing speed for every frame
        Take the eucledean distance in x and y covered between two frames, speerated by the different axes (x and y).
        the resulting mean speed of the two points is the climbing speed framewise returned for each axis.
        :return: dictionary with function name (key) and list (len=data_rows_count) of climbing speeds in px/s
        for every frame for every foot
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
    results['speed_x'] = np.full((data_rows_count,), np.NAN)
    results['speed_y'] = np.full((data_rows_count,), np.NAN)

    # create dictionary and save tuples with nose coordinates for every data_row
    nose_coords = {}
    hip_coords = {}
    for i in range(data_rows_count):
        nose_coords[i] = (data.loc[i][scorer, 'Nose', 'x'], data.loc[i][scorer, 'Nose', 'y'])
        hip_coords[i] = (data.loc[i][scorer, 'Hip', 'x'], data.loc[i][scorer, 'Hip', 'y'])
        i += 1
    #print('nose coordinates: ', nose_coords)

    bad_likelihood_counter_nose = []
    bad_likelihood_counter_hip = []
    nose_speeds_x = []
    nose_speeds_y = []
    hip_speeds_x = []
    hip_speeds_y = []
    for j, coord in zip(range(1, len(nose_coords)), nose_coords):
        nose_likelihood = data.loc[j][scorer, 'Nose', 'likelihood']
        hip_likelihood = data.loc[j][scorer, 'Hip', 'likelihood']
        # only include tracking points with a likelihood >= limit
        # calculate nose speed in x and y direction seperately
        if nose_likelihood >= likelihood:
            # calculate eucledean distance for every frame and save it to correct index in result dataframe
            xdiff = abs(nose_coords[j][0] - nose_coords[j - 1][0])
            ydiff = abs(nose_coords[j][1] - nose_coords[j - 1][1])

            nose_speeds_x.append(round(xdiff * framerate, 2))  # *framerate for px/s
            nose_speeds_y.append(round(ydiff * framerate, 2))  # *framerate for px/s
        else:
            bad_likelihood_counter_nose.append(1)
            nose_speeds_x.append(np.nan)
            nose_speeds_y.append(np.nan)

        # calculate hip speed in x and y direction seperately
        if hip_likelihood >= likelihood:
            xdiff = abs(hip_coords[j][0] - hip_coords[j - 1][0])
            ydiff = abs(hip_coords[j][1] - hip_coords[j - 1][1])

            hip_speeds_x.append(round(xdiff * framerate, 2))  # *framerate for px/s
            hip_speeds_y.append(round(ydiff * framerate, 2))  # *framerate for px/s
        else:
            bad_likelihood_counter_hip.append(1)
            hip_speeds_x.append(np.nan)
            hip_speeds_y.append(np.nan)

    # results
    average_speeds_x = []
    average_speeds_y = []
    for i in range(len(nose_speeds_x)):
        if np.isnan(hip_speeds_x[i]) == True:
            average_speed_x = nose_speeds_x[i]
            average_speed_y = nose_speeds_y[i]
        else:
            average_speed_x = (nose_speeds_x[i] + hip_speeds_x[i])/2.0
            average_speed_y = (nose_speeds_y[i] + hip_speeds_y[i])/2.0
        average_speeds_x.append(average_speed_x)

        results['speed_x'][i] = average_speed_x
        results['speed_y'][i] = average_speed_y

    #print('average_speeds: ', average_speeds)

    #print('exluded frames for bad likelihood: ',
    #      '\nNose: ', len(bad_likelihood_counter_nose), 'Hip: ', len(bad_likelihood_counter_hip))

    # copy second row into first row and second last into last row of each array
    results['speed_x'][0] = results['speed_x'][1]
    results['speed_y'][0] = results['speed_y'][1]
    results['speed_x'][-1] = results['speed_x'][-2]
    results['speed_y'][-1] = results['speed_y'][-2]

    # rename dictionary keys of results
    results = {key + '_PXperS': value for (key, value) in results.items()}
    #print('results speed: ', results)

    return results
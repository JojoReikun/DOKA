import numpy as np

# TODO: calculate frame wise for step-phases not average over all! Or do both in 2 different functions
def climbing_speed(**kwargs):
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
    feet = ["FR", "FL", "HR", "HL"]

    result = {}
    # create dictionary and save tuples with nose coordinates for every data_row
    nose_coords = {}
    for i, row in zip(len(data_rows_count), data_rows_count):
        nose_coords[i] = (data[row][scorer, 'Nose', 'x'], data[row][scorer, 'Nose', 'y'])
    print('nose coordinates: ', nose_coords)

    for foot in feet:
        #calculate eucledean distance for every frame and save it to correct index for foot in result dataframe


    # TODO: calculate climbing speed and write results to new column in dataframe
    # mgs: changed this to use a numpy array
    # speed_list = []
    # for i in range(data_rows_count):
    #     speed_list.append(long_range_speed)
    #speed_list = np.zeros((data_rows_count, )) + long_range_speed
    # return {__name__.rsplit('.', 1)[1]: speed_list}
    return 0
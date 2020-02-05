def climbing_speed(data, clicked, data_row_count, config):
    """
        Uses the Nose tracking point to determine the climbing speed.
        Takes the absolute value of the distance in pixels covered in 1/10 of the frames,
        3x rather in the middle of the run and then takes the mean.
    """
    import os
    from pathlib import Path
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    current_path = os.getcwd()
    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    framerate = cfg['framerate']

    first_speed_start = int((data_row_count/2) - 30)
    second_speed_start = int((data_row_count/2) - 5)
    third_speed_start = int((data_row_count/2) + 20)
    long_range_speed_start = int((data_row_count/2)) - int((framerate/5))
    long_range_speed_end = int((data_row_count/2)) + int((framerate/5))


    scorer = data.columns[1][0]

    # TODO: filter columns of used labels for likelihood BEFORE calculation
    likelihood = 0.90
    # nose_coords = data[scorer, 'Nose']
    # nose_coords = nose_coords[nose_coords.likelihood >= 0.90]

    nose_coords = data[scorer, 'Nose', 'x']
    first_speed = abs(nose_coords.iloc[first_speed_start] - nose_coords.iloc[first_speed_start + int((framerate/10))])
    print("first speed (px/10tel sec): ", first_speed)
    second_speed = abs(nose_coords.iloc[second_speed_start] - nose_coords.iloc[second_speed_start + int((framerate/10))])
    print("second speed (px/10tel sec): ", second_speed)
    third_speed = abs(nose_coords.iloc[third_speed_start] - nose_coords.iloc[third_speed_start + int((framerate/10))])
    print("third speed (px/10tel sec): ", third_speed)

    long_range_speed_2and1halftel = abs(nose_coords.iloc[long_range_speed_start] - nose_coords.iloc[long_range_speed_end])


    mean_speed = (np.mean(first_speed+second_speed+third_speed))*10
    long_range_speed = int(long_range_speed_2and1halftel*2.5)
    print("mean speed (px/sec): ", mean_speed)
    print("long range speed (px/sec): ", long_range_speed)

    #TODO: calculate climbing speed and write results to new column in dataframe
    speed_list = []
    for i in range(data_row_count):
        speed_list.append(long_range_speed)
    return {__name__.rsplit('.', 1)[1]: speed_list}
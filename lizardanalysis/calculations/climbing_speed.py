def climbing_speed(data, clicked, data_row_count, config):
    """
        Uses the Nose tracking point to determine the climbing speed.
        Takes the absolute value of the distance in pixels covered in a certain range of the frames taken from the middle of the run.
        (data_row_count/2) +/- (framerate/speed_interval)
    """
    import os
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    current_path = os.getcwd()
    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    framerate = cfg['framerate']

    speed_interval = 5
    long_range_speed_start = int((data_row_count/2)) - int((framerate/speed_interval))
    long_range_speed_end = int((data_row_count/2)) + int((framerate/speed_interval))
    #TODO: test if +/- int((framerate/speed_interval)) creates start/end out of bounds

    scorer = data.columns[1][0]

    # TODO: filter columns of used labels for likelihood BEFORE calculation
    likelihood = 0.90
    # nose_coords = data[scorer, 'Nose']
    # nose_coords = nose_coords[nose_coords.likelihood >= 0.90]

    nose_coords = data[scorer, 'Nose', 'x']

    long_range_speed_2and1halftel = abs(nose_coords.iloc[long_range_speed_start] - nose_coords.iloc[long_range_speed_end])

    long_range_speed = int(long_range_speed_2and1halftel*(speed_interval/2.))

    print("long range speed (px/sec): ", long_range_speed)

    #TODO: calculate climbing speed and write results to new column in dataframe
    speed_list = []
    for i in range(data_row_count):
        speed_list.append(long_range_speed)
    return {__name__.rsplit('.', 1)[1]: speed_list}
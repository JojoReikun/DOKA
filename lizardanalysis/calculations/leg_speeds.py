from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis.utils import animal_settings

def leg_speeds(**kwargs):
    """
    calculates the speed in mm/s for every leg frame-wise using the distance difference between two consecutive frames.
    :param kwargs:
    :return:
    """
    import numpy as np
    from pathlib import Path

    data = kwargs.get("data")
    data_rows_count = kwargs.get("data_rows_count")
    config = kwargs.get('config')
    animal = kwargs.get('animal')
    likelihood = kwargs.get('likelihood')
    filename = kwargs.get('filename')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)

    framerate = cfg['framerate']
    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    resolution = (1280, 1024)

    plotting = False

    results = {}
    for foot in feet:
        results[foot] = np.full((data_rows_count,), 0.0, dtype='float')

        # find conversion factor for spider:
        conv_fac = auxiliaryfunctions.find_conversion_factor_for_spider(filename)

    for row in range(1, data_rows_count):
        # print('---------- ROW: ', row)
        for foot in feet:
            # filter for likelihood:
            row_likelihood = data.loc[row][scorer, f"{foot}", "likelihood"]
            rowminusone_likelihood = data.loc[row-1][scorer, f"{foot}", "likelihood"]

            if row_likelihood >= likelihood and rowminusone_likelihood >= likelihood:
                # calculate the euclidean distance between last coord and current coord of foot
                xdiff = data.loc[row][scorer, f"{foot}", 'x'] - data.loc[row-1][scorer, f"{foot}", 'x']
                ydiff = data.loc[row][scorer, f"{foot}", 'y'] - data.loc[row-1][scorer, f"{foot}", 'y']
                distance = np.sqrt(xdiff**2 + ydiff**2)

                # calibrate distance with conversion factor
                distance_calib = distance / conv_fac

            else:
                distance_calib = np.nan

            # get the current phase of the step for every foot, calling the respective class instance function
            results[foot][row] = calculate_speed(distance_calib, framerate)

    # rename dictionary keys of results
    results = {'speed_' + key: value for (key, value) in results.items()}

    if plotting:
        plot_speeds(results, data_rows_count)
    return results


def calculate_speed(distance_calib, framerate):
    # calculate the speed in mm/second
    speed = distance_calib/framerate
    retval = speed
    return retval


def plot_speeds(results, data_rows_count):
    import pandas as pd
    import matplotlib.pyplot as plt

    df_plot = pd.DataFrame(columns=results.keys(), index=range(data_rows_count))
    for key in results:
        #df_plot[key] = [float(s.decode().strip('"')) for s in results[key]]
        df_plot[key] = [float(s) for s in results[key]]
    print(df_plot)

    df_plot.plot(linewidth=1)
    plt.show()
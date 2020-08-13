import pandas as pd
import numpy as np
from numpy import array
import math


def direction_of_running(**kwargs):
    """
        Uses the Head tracking point to determine the direction of climbing.
        Depending on the clicked value, which determines the configuration of the lizard climbing direction in the videos:
            - RIGHT: = increasing x
            - LEFT: = decreasing x
        :param data: pandas DataFrame with the current DLC results read in from csv
        :return direction of running as string "RIGHT" or "LEFT"
    """
    data = kwargs.get("data")
    data_row_count = kwargs.get("data_rows_count")

    scorer = data.columns[1][0]
    #print('scorer: ', scorer)

    #TODO: filter columns of used labels for likelihood BEFORE calculation
    likelihood = 0.90
    #nose_coords = data[scorer, 'Nose']
    #nose_coords = nose_coords[nose_coords.likelihood >= 0.90]

    head_coords = data[scorer, 'Head', 'x']
    #print(nose_coords.head())


    if head_coords.iloc[-1] > head_coords.iloc[0]:
        direction = "RIGHT"
    elif head_coords.iloc[-1] < head_coords.iloc[0]:
        direction = "LEFT"
    else:
        direction = "Direction can't be determined"

    direction_list = np.array(data_row_count*[direction], dtype=np.string_)
    direction_list = [direction_encode_and_strip(direction) for direction in direction_list]
    return {__name__.rsplit('.', 1)[1]: direction_list}


def direction_encode_and_strip(bytestring):
    # get rid of b"..." for direction
    if bytestring == b'RIGHT':
        direction = "RIGHT"
    elif bytestring == b'LEFT':
        direction = "LEFT"
    else:
        print("no known direction found")
        direction = "UNKNOWN"
    return direction
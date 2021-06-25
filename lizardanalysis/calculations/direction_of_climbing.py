import pandas as pd
import numpy as np
from numpy import array
import math


def direction_of_climbing(**kwargs):
    """
        Uses the Nose tracking point to determine the direction of climbing.
        When starting a new project the user gets the option to define how the direction of climbing should be determined:
        - direction of movement in the video (2 variants, see below)
        - extract from filename, clicked = 3
        Depending on the clicked value, which determines the configuration of the lizard climbing direction in the videos:
            - if clicked = 1: direction UP = increasing x
            - if clicked = 2: direction UP = decreasing x
        :param data: pandas DataFrame with the current DLC results read in from csv
        :param clicked: passed clicked value from gui determining configuration of direction of climbing
        :return direction of climbing as string "UP" or "DOWN"
    """
    # print("DIRECTION OF CLIMBING")
    # define necessary **kwargs:
    data = kwargs.get('data')
    clicked = kwargs.get('clicked')
    data_rows_count = kwargs.get('data_rows_count')

    # print('clicked value in function: ', clicked)

    scorer = data.columns[1][0]
    # print('scorer: ', scorer)

    # nose_coords = data[scorer, 'Nose']
    # nose_coords = nose_coords[nose_coords.likelihood >= 0.90]

    # TODO: make spelling of labels independent on first letter being lower or upper case
    nose_coords = data[scorer, 'Nose', 'x']
    # print(nose_coords.head())

    if clicked == 1:
        if nose_coords.iloc[-1] > nose_coords.iloc[0]:
            direction = "UP"
            #direction = "DOWN"  # for waterdragons
        elif nose_coords.iloc[-1] < nose_coords.iloc[0]:
            direction = "DOWN"
            #direction = "UP"    # for waterdragons
        else:
            direction = "Direction can't be determined"

    elif clicked == 2:
        if nose_coords.iloc[-1] < nose_coords.iloc[0]:
            direction = "UP"
        elif nose_coords.iloc[-1] > nose_coords.iloc[0]:
            direction = "DOWN"
        else:
            direction = "Direction can't be determined"

    elif clicked == 3:
        # look for "up" or "down" in filename - case insensitive

    else:
        print('no such video configuration defined')
        return

    # __name__.rsplit('.', 1)[1] = 'direction_of_climbing' (same as in checked_calculations)
    # print('\n direction: ', {__name__.rsplit('.', 1)[1]: direction})

    # mgs: changed this to use numpy array (much more efficient)
    direction_list = np.array(data_rows_count * [direction], dtype=np.string_)
    direction_list = [direction_encode_and_strip(direction) for direction in direction_list]
    # print(direction_list)
    return {__name__.rsplit('.', 1)[1]: direction_list}


def direction_encode_and_strip(bytestring):
    # get rid of b"..." for direction
    if bytestring == b'UP':
        direction = "UP"
    elif bytestring == b'DOWN':
        direction = "DOWN"
    else:
        print("no known direction found")
        direction = "UNKNOWN"
    return direction
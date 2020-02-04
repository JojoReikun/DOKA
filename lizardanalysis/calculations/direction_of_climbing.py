import pandas as pd
import numpy as np
from numpy import array
import math


def direction_of_climbing(data, clicked):
    """
        Uses the Nose tracking point to determine the direction of climbing.
        Depending on the clicked value, which determines the configuration of the lizard climbing direction in the videos:
            - if clicked = 1: direction UP = increasing x
            - if clicked = 2: direction UP = decreasing x
        :param data: pandas DataFrame with the current DLC results read in from csv
        :param clicked: passed clicked value from gui determining configuration of direction of climbing
        :return direction of climbing as string "UP" or "DOWN"
    """
    # TODO: this is only for testing. __call__() error : takes from 1 to 2 positional arguments, 4 given => parse clicked and likelihood

    print('clicked value in function: ', clicked)

    scorer = data.columns[1][0]
    #print('scorer: ', scorer)

    #TODO: filter columns of used labels for likelihood BEFORE calculation
    likelihood = 0.90
    #nose_coords = data[scorer, 'Nose']
    #nose_coords = nose_coords[nose_coords.likelihood >= 0.90]

    nose_coords = data[scorer, 'Nose', 'x']
    #print(nose_coords.head())

    if clicked == 1:
        if nose_coords.iloc[-1] > nose_coords.iloc[0]:
            direction = "UP"
        elif nose_coords.iloc[-1] < nose_coords.iloc[0]:
            direction = "DOWN"
        else:
            direction = "Direction can't be determined"

    elif clicked == 2:
        if nose_coords.iloc[-1] < nose_coords.iloc[0]:
            direction = "UP"
        elif nose_coords.iloc[-1] > nose_coords.iloc[0]:
            direction = "DOWN"
        else:
            direction = "Direction can't be determined"

    else:
        print('no such video configuration defined')
        return

    # print('test_print: calculating direction_of_climbing')
    print('\n direction: ', direction)

    return {__name__.rsplit('.', 1)[1]: direction}
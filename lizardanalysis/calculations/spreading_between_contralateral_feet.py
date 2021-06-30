from lizardanalysis.utils import animal_settings
import numpy as np


def calc_spreading(**kwargs):
    """
    This function calculated the spreading between contralateral feet at TIME
    Return: Distance in px between forefeet and between hindfeet
    """

    likelihood = kwargs.get('likelihood')
    data = kwargs.get("data")
    data_rows_count = kwargs.get("data_rows_count")
    filename = kwargs.get("filename")
    animal = kwargs.get("animal")

    feet = animal_settings.get_list_of_feet(animal)
    # only use the feet on the right to calculate distance to left counterpart
    right_feet = [foot for foot in feet if "R" in foot]
    print("right feet: ", right_feet)
    scorer = data.columns[1][0]

    results = {}

    for foot in feet:
        results[foot] = np.full((data_rows_count,), np.NAN)
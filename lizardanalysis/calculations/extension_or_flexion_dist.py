### IMPORTS:
import numpy as np
from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis.utils import animal_settings


def extension_or_flexion_dist(**kwargs):
    """
    calculates the distance between leg tip and leg base frame-wise.
    :param kwargs:
    :return:
    """

    ### SETUP:
    data = kwargs.get("data")
    data_rows_count = kwargs.get("data_rows_count")
    filename = kwargs.get("filename")
    animal = kwargs.get("animal")
    likelihood = kwargs.get("likelihood")


    feet = animal_settings.get_list_of_feet(animal)
    feet_bases = ['Lb1', 'Lb2', 'Lb3', 'Lb4', 'Rb1', 'Rb2', 'Rb3', 'Rb4']
    scorer = data.columns[1][0]

    ### CALCULATION:
    results = {}
    for foot in feet:
        results[foot] = np.full((data_rows_count,), 0.0, dtype='float')

    # find conversion factor for spider:
    conv_fac = auxiliaryfunctions.find_conversion_factor_for_spider(filename)

    for row in range(data_rows_count):
        for foot, base in zip(feet, feet_bases):
            # determine likelihood of leg tip and leg base point:
            tip_likelihood = data.loc[row][scorer, f"{foot}", "likelihood"]
            base_likelihood = data.loc[row][scorer, f"{base}", "likelihood"]

            # -------
            # calculate the absolute euclidean distance between leg tip and leg base for the current row:
            if tip_likelihood >= likelihood and base_likelihood >= likelihood:
                tip = (data.loc[row][scorer, f"{foot}", 'x'], data.loc[row][scorer, f"{foot}", 'y'])
                base = (data.loc[row][scorer, f"{base}", 'x'], data.loc[row][scorer, f"{base}", 'y'])
                distance = np.sqrt((base[0]-tip[0]) ** 2 + (base[1]-tip[1]) ** 2)

                # calibrate distance with conversion factor
                distance_calib = distance/conv_fac

            else:
                distance_calib = np.nan

            # saves distance for current frame in result dict
            results[foot][row] = distance_calib

    # rename dictionary keys of results
    results = {'ext-flex-dist_' + key: value for (key, value) in results.items()}

    return results

#
# def find_conversion_factor_for_spider(filename):
#     # calibrate distance: convert px to mm:
#     # dictionary: Spider (Lxx,Lyy):factor in px/mm
#     conversion_factors = {(62, 76): 2.57,
#                           (77, 91): 2.56,
#                           (92, 111): 2.58,
#                           (112, 126): 2.58}
#     spidername = filename.split(sep="_")[0]
#     spidernumber = int(''.join(list(filter(str.isdigit, spidername))))
#     print(f"spidername: {spidername}, spidernumber: {spidernumber}")
#
#     conv_fac = np.nan
#     for i in range(len(conversion_factors.keys())):
#         key = list(conversion_factors.keys())[i]
#         if spidernumber in range(key[0], key[1]):  # assign correct converion factor to spider
#             conv_fac = conversion_factors[key]
#             print(f"spidernumber: {spidernumber}, conv_fac: {conv_fac}")
#
#     if conv_fac == np.nan:
#         print(f"no conversion factor was found for this spidernumber: {spidernumber}")
#         conv_fac = 1.0
#
#     return conv_fac

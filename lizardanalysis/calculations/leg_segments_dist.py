### IMPORTS:
import numpy as np
from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis.utils import animal_settings

def leg_segments_dist(**kwargs):
    """
        for spiders:
        calculates the absolute distance for the two leg segments (e.g.: Lb1-Lm1, Lm1-L1) frame-wise.
        Spider leg extension works through femoral depression towards the substrate (trochanter-femur joint - muscles)
        and increase in ventral angles of the femur-patella and the tibia-metatarsal joint (hydraulics).
        The distance between Lb1-Lm1 is representative for the femoral depression, whereas the distance between
        Lm1-L1 represents the increase of the ventral angles of the other two joints.
        :param kwargs:
        :return: dictionary with the distances between Base and middle & middle and foot tip for each leg
        """
    ### SETUP:
    data = kwargs.get("data")
    data_rows_count = kwargs.get("data_rows_count")
    filename = kwargs.get("filename")
    animal = kwargs.get("animal")
    likelihood = kwargs.get("likelihood")

    feet = animal_settings.get_list_of_feet(animal)
    feet_bases = ['Lb1', 'Lb2', 'Lb3', 'Lb4', 'Rb1', 'Rb2', 'Rb3', 'Rb4']
    feet_middles = ['Lm1', 'Lm2', 'Lm3', 'Lm4', 'Rm1', 'Rm2', 'Rm3', 'Rm4']
    scorer = data.columns[1][0]

    ### CALCULATION:
    results = {}
    for foot in feet:
        results[f'inner_segm_{foot}'] = np.full((data_rows_count,), 0.0, dtype='float')
        results[f'outer_segm_{foot}'] = np.full((data_rows_count,), 0.0, dtype='float')

    # find conversion factor for spider:
    conv_fac = auxiliaryfunctions.find_conversion_factor_for_spider(filename)

    for row in range(data_rows_count):
        for foot, base, middle in zip(feet, feet_bases, feet_middles):
            # determine likelihood of leg tip and leg base point:
            tip_likelihood = data.loc[row][scorer, f"{foot}", "likelihood"]
            #tip_rowminusone_likelihood = data.loc[row - 1][scorer, f"{foot}", "likelihood"]
            base_likelihood = data.loc[row][scorer, f"{base}", "likelihood"]
            #base_rowminusone_likelihood = data.loc[row - 1][scorer, f"{base}", "likelihood"]
            middle_likelihood = data.loc[row][scorer, f"{middle}", "likelihood"]
            #middle_rowminusone_likelihood = data.loc[row - 1][scorer, f"{middle}", "likelihood"]

            # calculate the euclidean distance between leg tip and leg middle => outer segment:
            if tip_likelihood >= likelihood and middle_likelihood >= likelihood:
                    #and tip_rowminusone_likelihood >= likelihood and middle_rowminusone_likelihood >= likelihood:
                tip = (data.loc[row][scorer, f"{foot}", 'x'], data.loc[row][scorer, f"{foot}", 'y'])
                centre = (data.loc[row][scorer, f"{middle}", 'x'], data.loc[row][scorer, f"{middle}", 'y'])
                distance_outerSegm = np.sqrt((centre[0] - tip[0]) ** 2 + (centre[1] - tip[1]) ** 2)

                # calibrate distance with conversion factor
                distance_calib_outerSegm = distance_outerSegm / conv_fac

            else:
                distance_calib_outerSegm = np.nan

            # calculate the euclidean distance between leg middle and leg base => inner segment:
            if base_likelihood >= likelihood and middle_likelihood >= likelihood:
                    #and base_rowminusone_likelihood >= likelihood and middle_rowminusone_likelihood >= likelihood:
                centre = (data.loc[row][scorer, f"{middle}", 'x'], data.loc[row][scorer, f"{middle}", 'y'])
                coxa = (data.loc[row][scorer, f"{base}", 'x'], data.loc[row][scorer, f"{base}", 'y'])
                distance_innerSegm = np.sqrt((coxa[0] - centre[0]) ** 2 + (coxa[1] - centre[1]) ** 2)

                # calibrate distance with conversion factor
                distance_calib_innerSegm = distance_innerSegm / conv_fac

            else:
                distance_calib_innerSegm = np.nan

            # saves distance for current frame in result dict
            results[f'inner_segm_{foot}'][row] = distance_calib_innerSegm
            results[f'outer_segm_{foot}'][row] = distance_calib_outerSegm

    #print("results segment distances: ", results)
    return results
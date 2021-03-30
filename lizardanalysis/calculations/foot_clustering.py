def footprint_clustering(**kwargs):
    """
    The vector sum of standard deviations from the mean for all AEPs or PEPs
    calculated for each leg (Figure 3D).
    Small footprint clustering value ==> the AEP coordinates, relative to the fly body were similar for all
    the AEP steps in the video.
    """

    import numpy as np
    import statistics
    #from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    # get kwargs:
    df_result_current = kwargs.get('df_result_current')
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    filename = kwargs.get("filename")
    animal = kwargs.get("animal")
    likelihood = kwargs.get("likelihood")

    feet = animal_settings.get_list_of_feet(animal)
    scorer = data.columns[1][0]

    # shouldn't matter where the AEP/PEP are relative to in these instances?
    # it will change the value of the mean, but the standard deviation should stay the same?

    feet = animal_settings.get_list_of_feet(animal)
    scorer = data.columns[1][0]

    ### CALCULATION:
    results = {}
    position = ["AEP", "PEP"]

    for pos in position:
        for foot in feet:
            results[foot] = np.full((data_rows_count,), 0.0, dtype='float')

        # read in rows with 'ext-flex-dist_{foot}':
        aep_columns_list = [col for col in df_result_current.columns if (pos in col)]
        pep_columns_list = [col for col in df_result_current.columns if (pos in col)]

        # read the columns one by one and calculate the subsequent diff in distances:
        for col, foot in zip(aep_columns_list, feet):

            # test if foot is in column name, and separating by x and y coordinates:
            if foot + "_x" in col:
                current_x_col = df_result_current[col]
            else:
                print("No x coordinates for the AEP values of foot {} found.")
                break

            if foot + "_y" in col:
                current_y_col = df_result_current[col]

            else:
                print("No y coordinates for the AEP values of foot {} found.")
                break

            # now have two different arrays, one that contains the x coordinates of AEP for a
            # they are already relative to the same point, the coxa, assuming that the relative coordinates
            # labelled for a given coxa do not change significantly for the video duration

            std_deviation_x = statistics.stdev(current_x_col)
            std_deviation_y = statistics.stdev(current_y_col)
            av_std_dev = np.sqrt(std_deviation_x ** 2 + std_deviation_y ** 2)
            results[foot+"_"+pos] = av_std_dev

        results = {'clustering' + key: value for (key, value) in results.items()}



        return results
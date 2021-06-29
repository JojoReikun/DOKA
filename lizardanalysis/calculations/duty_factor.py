def duty_factor(**kwargs):
    """
    calculates the fraction of the stepping cycle the a given leg/foot spends in stance phase
    - For walking, typical values are
    - For running, typical values are

    :return: results dataframe with 4, 6, or 8 key value pairs (list of frame-wise angles for every foot)
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')
    df_result_current = kwargs.get('df_result_current')

    # scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)

    # results will be stored into a key value pair dictionary
    results = {}
    phase_counter = {}
    stride_vs_stance = {"stride": 0, "stance": 0, "stride_frames": 0, "stance_frames": 0}

    # obtain all columns from the current results dataframe relating to step_phase
    step_phase_list = [col for col in df_result_current.columns if ('step_phase_' in col)]

    # read the columns one by one and calculate the subsequent diff in distances:
    for col, foot in zip(step_phase_list, feet):
        # test if foot is in column name:
        if foot in col:
            current_col = df_result_current[col]

            for i in range(len(current_col)):
                if current_col[i] in phase_counter:
                    phase_counter[current_col[i]] += 1
                else:
                    phase_counter[current_col[i]] = 1

            phase_counter.pop("b\'nan\'")  # need to check if it's just the NAN that comes up when loaded as a df

            # deleting the first and last elements of the dictionary also, because you don't know if they were complete
            # stride/stance phases, therefore they could skew the calculation of the duty factor

            i = 0
            keys_to_delete = []
            for key in phase_counter.keys():

                if i == 1 or i == len(
                        phase_counter) - 1:  # assuming you want to remove the second element from the dictionary
                    keys_to_delete.append(key)

                i = i + 1

            for key in keys_to_delete:

                if key in phase_counter:
                    del phase_counter[key]

            # need to count how many swing phases and how many stance phases there are
            # then need to find the average number of frames for a given swing or stance phase
            # frame is a suitable covariant for time, as a frame has a fixed time interval
            # finally calculate the stance/stance+stride

        for key, value in phase_counter.items():

            if "stride" in key:
                stride_vs_stance["stride"] += 1
                stride_vs_stance["stride_frames"] += value

            elif "stance" in key:
                stride_vs_stance["stance"] += 1
                stride_vs_stance["stance_frames"] += value

            else:
                print("Unrecognised phase type remains in dictionary; will be excluded.")

        average_swing = stride_vs_stance["stride_frames"] / stride_vs_stance["stride"]
        average_stance = stride_vs_stance["stance_frames"] / stride_vs_stance["stance"]
        duty_f = average_stance / (average_swing + average_stance)

        results[foot] = duty_f


    results = {'average_duty_factor' + key: value for (key, value) in results.items()}

    return results

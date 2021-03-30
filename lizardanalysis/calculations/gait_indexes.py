def gait_indexes(**kwargs):

    """
    Identify the different gait types:
    Tripod: 3 in stance, 3 in swing
    Tetrapod: 4 in stance, 2 in swing
    Metachronal: 5 in stance, 1 in swing
    Non-cannonical: anything that doesn't fall into the above categories

    :Return: Results dictionary with 4 key value pairs, defining the fraction of the video spent
    by the stick insect in the gait types above

    """

    import numpy as np
    import pandas as pd
    from lizardanalysis.utils import auxiliaryfunctions
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

    pre_results = {"tripod": 0, "tetrapod": 0, "metachronal": 0, "non-cannonical": 0}
    step_phases = {}
    results = {"tripod": 0, "tetrapod": 0, "metachronal": 0, "non-cannonical": 0}

    for foot in feet:

        step_phase_columns_list = [col for col in df_result_current.columns if ('stepphase_' in col)]

        # read the columns one by one and calculate the subsequent diff in distances:
        for col, foot in zip(step_phase_columns_list, feet):
            # test if foot is in column name:
            # should be 6 different columns
            if foot in col:
                current_col = df_result_current[col]
                step_phases[foot] = current_col

    # should now have a dictionary which contains all of the step phase data for all the feet

    counter = len(step_phases[feet[0]])
    calc_check = True

    for i in range(counter):

        swing = 0
        stance =0

        for foot in feet:

            if step_phases[foot][i] == "NAN":
                calc_check = False
                break
            else:
                continue

        if calc_check:
            for f in feet:

                if step_phases[f][i] == "swing":
                    swing +=1

                elif step_phases[f][i] == "stance":
                    stance +=1

            if stance == 3 and swing == 3:
                pre_results["tripod"] +=1

            elif stance == 4 and swing == 2:
                pre_results["tetrapod"] +=1

            elif stance == 5 and swing == 1:
                pre_results["metachronal"] += 1

            else:
                pre_results["non-cannonical"] += 1

        else:
            continue

   total_instances = pre_results["tripod"] + pre_results["tetrapod"] + pre_results["metachronal"] + pre_results["non-cannonical"]

   results["tripod"] = pre_results["tripod"]/total_instances
   results["tetrapod"] = pre_results["tetrapod"]/total_instances
   results["metachronal"] = pre_results["metachronal"]/total_instances
   results["non-cannonical"] = pre_results["non-cannonical"]/total_instances


  return results




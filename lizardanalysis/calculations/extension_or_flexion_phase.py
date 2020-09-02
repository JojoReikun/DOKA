def extension_or_flexion_phase(**kwargs):
    import numpy as np
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

    ### CALCULATION:
    results = {}
    for foot in feet:
        results[foot] = np.full((data_rows_count,), 0.0, dtype='float')

    # read in rows with 'ext-flex-dist_{foot}':
    ext_flex_columns_list = [col for col in df_result_current.columns if ('ext-flex-dist_' in col)]
    #print("ext_flex_columns_list ", ext_flex_columns_list)

    # read the columns one by one and calculate the subsequent diff in distances:
    for col, foot in zip(ext_flex_columns_list, feet):
        # test if foot is in column name:
        if foot in col:
            current_col = df_result_current[col]

            # calculate the distence between subsequent frames:
            diff_col = current_col.diff()

            # replace positve differences with 'ext' and negative with 'flex'
            # flex = dist between base and tip becomes smaller = df.diff() -> row - (row-1) = negative diff
            diff_col[diff_col > 0.0] = int(1)
            diff_col[diff_col <= 0.0] = int(0)
            diff_col[diff_col == 1] = 'ext'
            diff_col[diff_col == 0] = 'flex'

            #print("diff_col new ", diff_col)

            # write phase list into result dataframe:
            # saves distance for current frame in result dict
            results[foot] = diff_col
        else:
            print("foot does not match with current column name!")
            break

    results = {'ext-flex-phase_' + key: value for (key, value) in results.items()}

    return results

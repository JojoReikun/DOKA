def stride_length(**kwargs):
    import numpy as np
    import pandas as pd
    pd.set_option('display.max_columns', None)

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_row_count = kwargs.get('data_row_count')
    df_result_current = kwargs.get('df_result_current')

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    max_stride_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    # print("active_columns: ", active_columns)

    results = {}
    for foot, column in zip(feet, active_columns):
        # print("\n----------- FOOT: ", foot)
        column = column.strip('')
        # print("column :", column)
        results[foot] = np.full((data_row_count,), np.NAN)
        for i in range(1, max_stride_phase_count):
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            # print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                # print(beg_end_tuple)
                # calculate the euclidean distance between last coord and current coord of foot
                xdiff = data.loc[beg_end_tuple[1]][scorer, f"{foot}", 'x'] - data.loc[beg_end_tuple[0]][scorer, f"{foot}", 'x']
                ydiff = data.loc[beg_end_tuple[1]][scorer, f"{foot}", 'y'] - data.loc[beg_end_tuple[0]][scorer, f"{foot}", 'y']
                distance = np.sqrt(xdiff**2 + ydiff**2)
            else:
                distance = np.NAN
            for row in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                results[foot][row] = distance
            # print("distance: ", distance)

    # print("results: ", results)
    # rename dictionary keys of results
    results = {'stride-length_' + key: value for (key, value) in results.items()}
    # print("\n \n -------------------- results FINAL: \n", results)

    # TODO: last stride phase is not recognized for calculating the distance????
    return results


def loop_encode(i):
    cell_value = 'stride000{}'.format(i).encode()
    return cell_value
def wrist_angles(**kwargs):
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_row_count = kwargs.get('data_row_count')
    df_result_current = kwargs.get('df_result_current')

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    max_stance_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    print("active_columns: ", active_columns)

    ##################################################################################################
    results = {}
    for foot, column in zip(feet, active_columns):
        print("\n----------- FOOT: ", foot)
        column = column.strip('')
        print("column :", column)
        results[foot] = np.full((data_row_count,), np.NAN)

        list_of_wrist_angles = []
        inner_toe_coordinates = []
        outer_toe_coordinates = []
        foot_coordinates = []
        toe_vectors = []
        wrist_vectors = []
        body_axes = []

        for i in range(1, max_stance_phase_count):
            cell_value = loop_encode(i)
            df_stance_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stance_section) == 0:
                break
            print(df_stance_section)
            df_stance_section_indices = list(df_stance_section.index.values)
            if len(df_stance_section_indices) > 0:
                beg_end_tuple = (df_stance_section_indices[0], df_stance_section_indices[-1])
                print(beg_end_tuple)
                angles_stance = []
                for i in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                    # what it does in the other script:
                    # get the coordinates of inner and outer toe out of df for all stance phase frames [(x,y), (x1,y1), ...]
                    inner_toe_coordinates.append((data.loc[i, (scorer, "{}_ti".format(foot), "x")],
                                                  data.loc[i, (scorer, "{}_ti".format(foot), "y")]))
                    outer_toe_coordinates.append((data.loc[i, (scorer, "{}_to".format(foot), "x")],
                                                  data.loc[i, (scorer, "{}_to".format(foot), "y")]))
                    foot_coordinates.append((data.loc[i, (scorer, "{}".format(foot), "x")],
                                             data.loc[i, (scorer, "{}".format(foot), "y")]))
                    body_axes.append(calc_body_axis(data, i))
                # TODO: continue
                print("lengths: ", len(angles_stance), beg_end_tuple[1] - beg_end_tuple[0])

    return


def loop_encode(i):
    cell_value = 'stance000{}'.format(i).encode()
    print("cell value :", cell_value)
    return cell_value


def calc_body_axis(df, index, scorer):
    """calculates the body axis vector of the gecko for the passed index: START = Hip, END = Shoulder
    returns a vector (x,y)"""
    body_axis_vector = ((df.loc[index, (scorer, "Shoulder", "x")] - df.loc[index, (scorer, "Hip", "x")]),
                        (df.loc[index, (scorer, "Shoulder", "y")] - df.loc[index, (scorer, "Hip", "y")]))
    return body_axis_vector
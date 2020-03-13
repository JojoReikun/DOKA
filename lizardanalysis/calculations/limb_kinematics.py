def limb_kinematics(data, clicked, data_rows_count, config, filename, df_result_current):
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    max_stride_phase_count = 10
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    print("active_columns: ", active_columns)

    results = {}
    for foot, column in zip(feet, active_columns):
        print("\n----------- FOOT: ", foot)
        column = column.strip('')
        print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        list_of_angles = []

        for i in range(1, max_stride_phase_count):
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                print(beg_end_tuple)
                angles_stride = []

                for i in range(beg_end_tuple[0], beg_end_tuple[1]):
                    shoulder_coords = (data.loc[i, (scorer, "Shoulder_{}".format(foot), "x")],
                                       data.loc[i, (scorer, "Shoulder_{}".format(foot), "y")])
                    knee_coords = (data.loc[i, (scorer, "{}_knee".format(foot), "x")],
                                   data.loc[i, (scorer, "{}_knee".format(foot), "y")])
                    vector = np.array([(knee_coords[0] - shoulder_coords[0]), (knee_coords[1] - shoulder_coords[1])])
                    # calculates the angle between the vector (Foot_shoulder - knee) and the vector body axis (Shoulder - Hip)
                    angles_stride.append(auxiliaryfunctions.py_angle_betw_2vectors(vector, calc_body_axis(data, i, scorer)))
                print("lengths: ", len(angles_stride), beg_end_tuple[1] - beg_end_tuple[0])

                j = 0
                for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                    results[foot][row] = angles_stride[row-(row-j)]
                    print("row : ", row, "row2 : ", row-(row-j))
                    j+=1
                list_of_angles.append(angles_stride)

    print("results: ", results)

    return


def loop_encode(i):
    cell_value = 'stride000{}'.format(i).encode()
    print("cell value :", cell_value)
    return cell_value


def calc_body_axis(df, index, scorer):
    """calculates the body axis vector of the gecko for the passed index: START = Hip, END = Shoulder
    returns a vector (x,y)"""
    body_axis_vector = ((df.loc[index, (scorer, "Shoulder", "x")] - df.loc[index, (scorer, "Hip", "x")]),
                        (df.loc[index, (scorer, "Shoulder", "y")] - df.loc[index, (scorer, "Hip", "y")]))
    return body_axis_vector
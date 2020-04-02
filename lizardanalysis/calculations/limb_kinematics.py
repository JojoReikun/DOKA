import numpy as np


def limb_kinematics(**kwargs):
    from lizardanalysis.utils import auxiliaryfunctions

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    max_stride_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    #print("active_columns: ", active_columns)

    plotting_dynamics = False


    ##################################################################################################
    results = {}
    for foot, column in zip(feet, active_columns):
        #print("\n----------- FOOT: ", foot)
        column = column.strip('')
        #print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        list_of_angles = []

        for i in range(1, max_stride_phase_count):
            #print('----- stride phase i: ', i)
            cell_value = loop_encode(i)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            # print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            if len(df_stride_section_indices) > 0:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                #print(beg_end_tuple)
                angles_stride = []

                for j in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                    #print('stride index j: ', j)
                    shoulder_coords = (data.loc[j, (scorer, "Shoulder_{}".format(foot), "x")],
                                       data.loc[j, (scorer, "Shoulder_{}".format(foot), "y")])
                    knee_coords = (data.loc[j, (scorer, "{}_knee".format(foot), "x")],
                                   data.loc[j, (scorer, "{}_knee".format(foot), "y")])
                    vector = np.array([(knee_coords[0] - shoulder_coords[0]), (knee_coords[1] - shoulder_coords[1])])
                    # calculates the angle between the vector (Foot_shoulder - knee) and the vector body axis (Shoulder - Hip)
                    limb_rom_kin = auxiliaryfunctions.py_angle_betw_2vectors(vector, auxiliaryfunctions.calc_body_axis(data, j, scorer))
                    angles_stride.append(limb_rom_kin)
                    #print('limb ROM: ', limb_rom_kin)
                # print("lengths: ", len(angles_stride), beg_end_tuple[1] - beg_end_tuple[0])

                # fill angle values into result dataframe in the right columns and matching indices
                k = 0
                for row in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                    results[foot][row] = angles_stride[row-(row-k)]
                    # print("row : ", row, "row2 : ", row-(row-k))
                    k+=1

                list_of_angles.append(angles_stride)
        #print('list of angles: ', list_of_angles)

    # rename column names in result dataframe
    results = {'dynamics_' + key: value for (key, value) in results.items()}
    # print("results: ", results)

    if plotting_dynamics:
        for foot in feet:
            plot_single_file_with_fitted_curve_and_variance(results, foot, data_rows_count)

    return results


def loop_encode(i):
    cell_value = 'stride000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value


def plot_single_file_with_fitted_curve_and_variance(df, foot, data_rows_count):
    # TODO
    x_values = []
    y_values = []
    stride_angles = []
    for index in range(data_rows_count):
        if df.isnull(df.loc[index, 'dynamics_{}'.format(foot)]):
            pass
        else:
            stride_angles.append(df.loc[index, 'dynamics_{}'.format(foot)])
    print('stride angles: ', stride_angles)

        # normalize stride length
        #x_values.append(np.array(range(len(stride_angles))) / float(stride_indices[1] - stride_indices[0]))
        #y_values.append(stride_angles)
    x_values_list = [item for sublist in x_values for item in sublist]
    y_values_list = [item for sublist in y_values for item in sublist]
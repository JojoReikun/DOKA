import numpy as np


def limb_kinematics(**kwargs):
    from lizardanalysis.utils import auxiliaryfunctions
    from pathlib import Path

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    filename = kwargs.get('filename')
    config = kwargs.get('config')

    config_file = Path(config).resolve()

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    max_stride_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    #print("active_columns: ", active_columns)

    plotting_dynamics = False

    print('LIMB KINEMATICS, Plotting = {}'.format(str(plotting_dynamics)))


    ##################################################################################################
    results = {}
    for foot, column in zip(feet, active_columns):
        #print("\n----------- FOOT: ", foot)
        column = column.strip('')
        #print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        list_of_angles = []
        plot_dict = {}  # {'stride_phase':'stride0001', 'stride_indices':beg_end_tuple, 'dynamics_angles':[a1, a2, ...]}

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

                plot_dict['stride_phase'] = 'stride000{}'.format(i)
                plot_dict['stride_indices'] = beg_end_tuple
                dynamics_angles = []

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

                plot_dict['dynamics_angles'] = angles_stride

                # fill angle values into result dataframe in the right columns and matching indices
                k = 0
                for row in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                    results[foot][row] = angles_stride[row-(row-k)]
                    # print("row : ", row, "row2 : ", row-(row-k))
                    k+=1

                list_of_angles.append(angles_stride)
        #print('list of angles: ', list_of_angles)
        #print("plot dict: ", plot_dict)

        # -------------------------------------------------------- PLOTTING:
        if plotting_dynamics:
            plot_single_file_with_fitted_curve_and_variance(filename, plot_dict, foot, config_file)
        # -------------------------------------------------------- END PLOTTING

    # rename column names in result dataframe
    results = {'dynamics_' + key: value for (key, value) in results.items()}
    # print("results: ", results)

    return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stride000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value


def plot_single_file_with_fitted_curve_and_variance(filename, plot_dict, foot, config_file):
    import matplotlib as plt
    from scipy.optimize import curve_fit
    from uncertainties import ufloat
    import os
    import errno

    x_values = []
    y_values = []
    dynamics_angles = []
    for stride_tuple, dynamics_angles_list in zip(plot_dict['stride_indices'], plot_dict['dynamics_angles']):
        # normalize stride length
        x_values.append(np.array(range(len(dynamics_angles))) / float(stride_tuple[1] - stride_tuple[0]))
        y_values.append(dynamics_angles)
    x_values_list = [item for sublist in x_values for item in sublist]
    y_values_list = [item for sublist in y_values for item in sublist]

    if len(x_values_list)&len(y_values_list) > 0:
        # function used for curve fitting with parameters to be optimized
        func_dict = {
            'sigmoid': ( lambda x, a, b, c, d: d+(c/(1.0+np.exp(-a*(x-b)))), np.array( [-10., 0.4, 120., 60.]) ),
            'exponential': ( lambda x, a, b: a*np.exp(b*x), np.array([1., -1.]) ),
            'logarithmic': ( lambda x, a, b, c: a * np.log(x + b) + c, np.array([-100., 0.01, 10.]) ),
            'linear': ( lambda x, a, b: a*x+b, np.array([1., 1.]) )
        }
        # sets names and colours for plotting
        functions_list = ['linear', 'exponential', 'logarithmic', 'sigmoid']
        colors_list = ['#1500DD', '#9B022A', '#444444', '#5AA010']

        labels = []
        for func_name, color in zip(functions_list, colors_list):
            func = func_dict[func_name][0]
            fparams = func_dict[func_name][1]
            try:
                best_fit_ab, covar = curve_fit(func, x_values_list, y_values_list, p0=fparams)
            except RuntimeError as e:
                print("Cannot fit function ", func_name)
                continue
            # determines the variance band
            sigma_ab = np.sqrt(np.diagonal(covar))
            a = ufloat(best_fit_ab[0], sigma_ab[0])
            b = ufloat(best_fit_ab[1], sigma_ab[1])
            # if func_name == 'logarithmic':
            #    c = ufloat(best_fit_ab[2], sigma_ab[2])
            text_res = "Best fit parameters:\na = {}\nb = {}".format(a, b)
            print(text_res)
            # calculate fitted values at the locations of the data points
            y_fit_list = func(np.array(x_values_list), *best_fit_ab)
            # calculate residuals and RMSE to determine best fitting function
            rmse = np.sqrt( np.sum((np.array(y_values_list) - y_fit_list)**2) )
            print("RMSE = ", rmse)
            labels.append("{}: {:.2f}".format(func_name, rmse))

            # sets the plot style
            plt.style.use('seaborn-whitegrid')
            # plots the dynamic angles as scatter points
            plt.scatter(x_values_list, y_values_list, facecolor='silver',
                        edgecolor='black', s=12, alpha=1)
            plt.rcParams.update({'font.size': 12, 'axes.titlesize': 12, 'axes.labelsize': 12})
            plt.ylabel("{} dynamics angle in degree".format(foot))
            plt.xlabel("normalized stride length")
            plt.title(filename, fontsize=12, fontweight=0, color='grey', loc='left')

            # plotting the model ...
            hires_x = np.linspace(min(x_values_list), max(x_values_list), len(x_values_list))
            hires_y = func(hires_x, *best_fit_ab)
            plt.plot(hires_x, hires_y, '{}'.format(color), alpha=0.6)
            # ... and the variance band
            bound_upper = func(hires_x, *(best_fit_ab + sigma_ab))
            bound_lower = func(hires_x, *(best_fit_ab - sigma_ab))
            plt.fill_between(hires_x, bound_lower, bound_upper,
                             color='{}'.format(color), alpha=0.15)
            # plt.text(140, 800, text_res)
        plt.legend(labels, title="RMSE", fontsize=12)

        # export plot as pdf
        dynamics_folder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results",
                                                "limb_dynamics_curve_fitting")
        try:
            os.makedirs(dynamics_folder)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        plt.savefig(os.path.join(dynamics_folder, "dynamics{}{}.pdf".format(foot, filename), dpi=300))
        plt.clf()
        plt.close()

import numpy as np
# TODO: output RMSE values for every Gecko (mean for all feet, check std) in seperate result files


def limb_kinematics(**kwargs):
    #TODO: filter for likelihood
    from lizardanalysis.utils import auxiliaryfunctions
    from pathlib import Path
    import pandas as pd
    import os

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    filename = kwargs.get('filename')
    config = kwargs.get('config')
    likelihood = kwargs.get('likelihood')

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)

    save_rmse = cfg['save_rmse_values']

    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]
    max_stride_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))
    #print("active_columns: ", active_columns)

    plot_dynamics_footwise = False
    save_curve_fitting_plots = False
    print('LIMB KINEMATICS, Plot Dynamics = {}, Save Plots = {}, Save RMSE as csv = {}'.format(str(plot_dynamics_footwise),
                                                                                        str(save_curve_fitting_plots),
                                                                                        str(save_rmse)))
    ##################################################################################################
    results = {}
    rmse_sig = []
    rmse_lin = []
    rmse_exp = []
    rmse_log = []
    for foot, column in zip(feet, active_columns):
        #print("\n----------- FOOT: ", foot)
        column = column.strip('')
        #print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        list_of_angles = []
        plot_dict_gecko_foot = {}  # {'stride_phases':['stride0001', 'stride0002', ...],
                                # 'stride_indices':[beg_end_tuple1, beg_end_tuple2, ...],
                                # 'dynamics_angles':[[a1, a2, ...], [b1, b2, b3, ...], ...]}

        #create empty lists for plot_dict:
        stride_phases = []
        stride_indices = []
        dyn_angles = []

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
                bad_likelihood_counter = 0

                stride_phases.append('stride000{}'.format(i))
                stride_indices.append(beg_end_tuple)

                for j in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                    #print('stride index j: ', j)
                    # TODO: filter for likelihood of tracking points:
                    shoulder_foot_likelihood = data.loc[i][scorer, "Shoulder_{}".format(foot), "likelihood"]
                    knee_foot_likelihood = data.loc[i][scorer, "{}_knee".format(foot), "likelihood"]
                    #print("likelihoods: ", shoulder_foot_likelihood, knee_foot_likelihood)
                    if shoulder_foot_likelihood >= likelihood and knee_foot_likelihood >= likelihood:
                        shoulder_coords = (data.loc[j, (scorer, "Shoulder_{}".format(foot), "x")],
                                           data.loc[j, (scorer, "Shoulder_{}".format(foot), "y")])
                        knee_coords = (data.loc[j, (scorer, "{}_knee".format(foot), "x")],
                                       data.loc[j, (scorer, "{}_knee".format(foot), "y")])
                        vector = np.array(
                            [(knee_coords[0] - shoulder_coords[0]), (knee_coords[1] - shoulder_coords[1])])
                        # calculates the angle between the vector (Foot_shoulder - knee) and the vector body axis (Shoulder - Hip)
                        limb_rom_kin = auxiliaryfunctions.py_angle_betw_2vectors(vector,
                                                                                 auxiliaryfunctions.calc_body_axis(data,
                                                                                                                   j,
                                                                                                                   scorer))
                        angles_stride.append(limb_rom_kin)
                    else:
                        angles_stride.append(np.nan)
                        bad_likelihood_counter += 1

                # print("DEBUG: ", bad_likelihood_counter)
                # print("lengths: ", len(angles_stride), beg_end_tuple[1] - beg_end_tuple[0])

                dyn_angles.append(angles_stride)

                # fill angle values into result dataframe in the right columns and matching indices
                k = 0
                for row in range(beg_end_tuple[0], beg_end_tuple[1]+1):
                    results[foot][row] = angles_stride[row-(row-k)]
                    # print("row : ", row, "row2 : ", row-(row-k))
                    k+=1

                list_of_angles.append(angles_stride)
        #print('list of angles: ', list_of_angles)

        # fill plot_dict
        # {'phases': ["stride0001", ....], 'stride_ind': [(5,16),(27,44),...], 'dyn_angles': [[a1, a2, ...], [...]]}:
        plot_dict_gecko_foot["stride_phases"] = stride_phases
        plot_dict_gecko_foot["stride_indices"] = stride_indices
        plot_dict_gecko_foot["dynamics_angles"] = dyn_angles
        #print("plot dict: ", plot_dict_gecko_foot)

        # -------------------------------------------------------- PLOTTING:
        if plot_dynamics_footwise:
            rmse = plot_single_file_with_fitted_curve_and_variance(filename, plot_dict_gecko_foot, foot, config_file, save_curve_fitting_plots)
            #print("rmse: ", rmse)
            if len(rmse) > 0:
                #print("rmse_sig: ", float(rmse['sigmoidal']))
                rmse_sig.append(float(rmse['sigmoidal']))
                rmse_lin.append(float(rmse['linear']))
                rmse_log.append(float(rmse['logarithmic']))
                rmse_exp.append(float(rmse['exponential']))

    #print(rmse_sig, rmse_lin, rmse_exp, rmse_log)

    if plot_dynamics_footwise & save_rmse:
        dynamics_folder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results",
                                       "limb_dynamics_curve_fitting")
        rmse_file = os.path.join(dynamics_folder, "rmse.csv")
        rmse_values = [filename,
                       np.nanmean(rmse_sig), np.nanstd(rmse_sig),
                       np.nanmean(rmse_lin), np.nanstd(rmse_lin),
                       np.nanmean(rmse_exp), np.nanstd(rmse_exp),
                       np.nanmean(rmse_log), np.nanstd(rmse_log)]
        print("rmse values: ", rmse_values)

        auxiliaryfunctions.append_list_as_row_to_csv(rmse_file, rmse_values)

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


def plot_single_file_with_fitted_curve_and_variance(filename, plot_dict, foot, config_file, save_curve_fitting_plots):
    from scipy.optimize import curve_fit
    from uncertainties import ufloat

    x_values = []
    y_values = []
    for stride_tuple, dynamics_angles_list in zip(plot_dict['stride_indices'], plot_dict['dynamics_angles']):
        #print("stride tuple: ", stride_tuple)
        #print("dynamics angle list: ", dynamics_angles_list)
        # test if dynamics angles list contains nan and remove them
        length_before = len(dynamics_angles_list)
        dynamics_angles_list = [angle for angle in dynamics_angles_list if str(angle) != 'nan']
        length_after = len(dynamics_angles_list)
        # print(length_before, length_after, (stride_tuple[1]-stride_tuple[0]))

        if stride_tuple[1] - stride_tuple[0] >= 1:
            # TODO: improve filter for nans
            # normalize stride length
            x_values.append(np.array(range(len(dynamics_angles_list))) / float(stride_tuple[1] - stride_tuple[0]))
            y_values.append(dynamics_angles_list)
    # print("x_values: ", x_values,
    #       "y_values: ", y_values)
    x_values_list = [item for sublist in x_values for item in sublist]
    y_values_list = [item for sublist in y_values for item in sublist]
    #debug:
    #print("x, y lengths: ", len(x_values_list), len(y_values_list))
    if len(x_values_list) != len(y_values_list):
        print("x and y are not of equal length!")
    # print("x_values_list: ", x_values_list,
    #       "length: ", len(x_values_list),
    #       "\ny_values_list: ", y_values_list,
    #       "length: ", len(y_values_list))

    rmse_dict = {}
    if len(x_values_list) & len(y_values_list) > 5:
        print("CURVE FITTING ... {}".format(foot))
        # function used for curve fitting with parameters to be optimized
        func_dict = {
            'sigmoidal': ( lambda x, a, b, c, d: d+(c/(1.0+np.exp(-a*(x-b)))), np.array( [-10., 0.4, 120., 60.]) ),
            'exponential': ( lambda x, a, b: a*np.exp(b*x), np.array([1., -1.]) ),
            'logarithmic': ( lambda x, a, b, c: a * np.log(x + b) + c, np.array([-100., 0.01, 10.]) ),
            'linear': ( lambda x, a, b: a*x+b, np.array([1., 1.]) )
        }
        # sets names and colours for plotting
        functions_list = ['linear', 'exponential', 'logarithmic', 'sigmoidal']
        colors_list = ['#1500DD', '#9B022A', '#444444', '#5AA010']

        labels = []

        for func_name, color in zip(functions_list, colors_list):
            func = func_dict[func_name][0]
            fparams = func_dict[func_name][1]
            try:
                best_fit_ab, covar = curve_fit(func, x_values_list, y_values_list, p0=fparams)
            except RuntimeError as e:
                print("Cannot fit function ", func_name)
                # if function can't be fitted, sets the rmse value to nan
                rmse_dict[func_name] = np.nan
                continue
            # determines the variance band
            sigma_ab = np.sqrt(np.diagonal(covar))
            a = ufloat(best_fit_ab[0], sigma_ab[0])
            b = ufloat(best_fit_ab[1], sigma_ab[1])
            if func_name == 'logarithmic':
                c = ufloat(best_fit_ab[2], sigma_ab[2])
            text_res = "Best fit parameters:\na = {}\nb = {}".format(a, b)
            #print(text_res)

            # calculate fitted values at the locations of the data points
            y_fit_list = func(np.array(x_values_list), *best_fit_ab)
            # calculate residuals and RMSE to determine best fitting function
            rmse = np.sqrt( np.sum((np.array(y_values_list) - y_fit_list)**2) )
            #print("RMSE {} = ".format(func_name), rmse)
            labels.append("{}: {:.2f}".format(func_name, rmse))
            rmse_dict[func_name] = "{:.2f}".format(rmse)

    return rmse_dict


def plot_curve_fitting():
    import os
    import errno
    import matplotlib.pyplot as plt

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
    # print("dynamics folder: ", dynamics_folder)
    try:
        os.makedirs(dynamics_folder)
        # print("folder for curve_fitting plots created")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    if save_curve_fitting_plots:
        plt.savefig(os.path.join(dynamics_folder, "dynamics{}{}.pdf".format(foot, filename)))
    plt.clf()
    plt.close()
    return

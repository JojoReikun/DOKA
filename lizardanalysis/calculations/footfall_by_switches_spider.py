# TODO: extreme peaks = labels that jump?! -> write likelihood at those points -> exclude them BEFORE smoothing
# use scipy outlier and novelty detection!!!
# TODO: implement Fourier analysis to get frequency for smoothing/lp filter individually for every spider

def footfall_by_switches_spider(**kwargs):
    #TODO: make low-pass filter optional, if don't use, use footfall smooth directly
    import os.path
    import pandas as pd
    import errno
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings
    from lizardanalysis.utils import outlier_detection


    #print("footfall_by_switches")

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    config = kwargs.get('config')
    filename = kwargs.get('filename')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')

    config_file = Path(config).resolve()

    #config_file = Path(config).resolve()
    # result folder for footfall plots
    # create file path for foot fall pattern diagrams
    analysis_results_folder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results")

    try:
        os.makedirs(analysis_results_folder)
        print("folder for analysis results created")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    step_detection_folder = os.path.join(analysis_results_folder, "step_detection_folder")
    plotting_footfall_folder = os.path.join(analysis_results_folder, "footfall-pattern-diagrams")

    # TODO: instead of hard-coding the feet and the three points for body_motion,
    # TODO: let the user choose based on labels available in DLC result file: Choose feet & choose body motion
    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)

    ### -----------------------------------
    relative = False
    plotting_footfall_patterns = True
    filter_for_likelihood = False
    ### -----------------------------------

    # prepare plot title name = spidername
    filename_title = filename.split("_", 2)[:2]
    filename_title = filename_title[0] + filename_title[1]

    # define cut-off value -> crops X% of frames on each side of video:
    p_cut_off = 0.05

    # read in all the frames for hip, spine and shoulder (x) to get mean body motion
    body_motion = {"frame":[], "mean_motion_x":[]}
    hip_diff = 0
    shoulder_diff = 0
    for row in range(1, data_rows_count):
        # go through frames and extract the x-diff for body-axis labels; take the mean and store in dict
        if filter_for_likelihood:
            # filter for likelihood, add new shoulder_diff if likelihood is good, else use last value:
            if data.loc[row][scorer, "Tail", 'likelihood'] >= likelihood and data.loc[row-1][scorer, "Tail", 'likelihood'] >= 0:
                hip_diff = data.loc[row][scorer, "Tail", 'x'] - data.loc[row-1][scorer, "Tail", 'x']
            if data.loc[row][scorer, "Head", 'likelihood'] >= likelihood and data.loc[row-1][scorer, "Head", 'likelihood'] >= likelihood:
                shoulder_diff = data.loc[row][scorer, "Head", 'x'] - data.loc[row-1][scorer, "Head", 'x']
        else:   # take raw data as it is
            hip_diff = data.loc[row][scorer, "Tail", 'x'] - data.loc[row - 1][scorer, "Tail", 'x']
            shoulder_diff = data.loc[row][scorer, "Head", 'x'] - data.loc[row - 1][scorer, "Head", 'x']

        body_motion['frame'].append(row-1)
        body_motion['mean_motion_x'].append((hip_diff + shoulder_diff)/2.0)

    # one class instance and one result array for every foot, because every foot needs own counter
    calculators = {}
    results = {}

    # for every foot:
    foot_motions = {}
    rel_foot_motions = {}
    for foot in feet:
        foot_motions[f"{foot}"] = []
        rel_foot_motions[f"rel_{foot}"] = []
        # read in all frames (x) differences: if moving forward = pos, if moving backwards = neg
        foot_motion = 0
        for row in range(1, data_rows_count):
            # if likelihood is worse than set value, last foot_motion will be used
            if filter_for_likelihood:
                if data.loc[row][scorer, f"{foot}", 'likelihood'] >= likelihood and data.loc[row-1][scorer, f"{foot}", 'x'] >= likelihood:
                    foot_motion = data.loc[row][scorer, f"{foot}", 'x'] - data.loc[row-1][scorer, f"{foot}", 'x']
            else:
                foot_motion = data.loc[row][scorer, f"{foot}", 'x'] - data.loc[row - 1][scorer, f"{foot}", 'x']
            # foot motion
            foot_motions[f"{foot}"].append(foot_motion)
            # foot motion - body motion
            rel_foot_motions[f"rel_{foot}"].append(foot_motion - body_motion['mean_motion_x'][row-1])
        #print('foot_motions: ', foot_motions)

        # create dataframe with >> frame | body_motion | rel_foot_motion << for current foot
        dict_df = {'body_motion':body_motion['mean_motion_x'],
                   'foot_motion':foot_motions[f"{foot}"],
                   'rel_foot_motion':rel_foot_motions[f"rel_{foot}"]}

        # OUTLIER DETECTION on original foot data
        df_pred_all, df_pred_outliers = outlier_detection.detect_outliers(dict_df, foot, filename_title,
                                                                          step_detection_folder,
                                                                          exploration_plotting=True)

        df = pd.DataFrame.from_dict(dict_df)
        # print("df: ", df)

        # gets a dict with x-values and the sign for switch in swing and stance phases (after smoothing data)
        # change in sign: positive to body = swing, negative to body = stance
        intersections = smooth_and_plot(df, data_rows_count, p_cut_off, relative, foot, filename, step_detection_folder,
                                        df_pred_all, df_pred_outliers, filename_title)
        #print(f"intersections for foot {foot}: ", intersections)

        # initializes class instance for every foot and empty result dict to be filled with the swing and stance phases:
        calculators[foot] = StridesAndStances()
        # "S10" = string of 10 characters: stance/stride + counter 000n
        results[foot] = calculators[foot].determine_stride_phases(intersections, data_rows_count)

    # rename dictionary keys of results
    results = {'stepphase_' + key: value for (key, value) in results.items()}
    #print("results: ", results)

    if plotting_footfall_patterns:
        """ plots a foot fall pattern diagram for every DLC result csv file/every lizard run """
        plot_footfall_pattern(results, data_rows_count, filename, plotting_footfall_folder)

    return results


def smooth_and_plot(df, data_rows_count, p_cut_off, relative, foot, filename, step_detection_folder, df_pred_all,
                    df_pred_outliers, filename_title, plotting=True):
    """
    Smooths the raw input data from foot motion and body motion, using a Butterworth low-pass filter and a
    Savintzky-Golay smoothing algorithm. Then computes the intersection points betw. the smoothed body and foot curves.
    If relative is True, body motion is already subtracted from the foot motion, hence foot is relative to the x-axis.
    If relative is False, intersection between foot motion and body motion is determined.
    If plotting is True: plots the footfall and body motion curves, and the intersection points between the
    smoothed curve and the x-axis (switch betw. swing and stance phase)

    return: dictionary which contains a list with x-values (frames) of intersection points and responding signs +1 or -1
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal
    import os
    import errno
    # savgol filter smoothing window (must be odd!):
    smooth_wind = 13

    # determine p_cutoff position:
    x_cutoff_value = int(round(data_rows_count * p_cut_off, 0))

    # add low pass filter to cut off spikes in data:
    ######## Butterworth filter
    x = np.linspace(0, data_rows_count - 1, data_rows_count - 1)
    b, a = signal.butter(3, 0.2, btype='lowpass', analog=False)  # original 0.1

    x_cutoff = np.linspace(x_cutoff_value, data_rows_count - 1, int(data_rows_count - 1 - x_cutoff_value))

    if plotting == True:
        # initiate plot
        plt.figure()
        plt.axvline(x_cutoff_value, color='black', label='cutoff 0.05%')

    if relative == True:
        """
        Uses the footmotion from which body motion has been substracted, hence body-motion is the x-axis.
        Note: intersection points for the lizard standing won't be excluded with this method. Use relative==False.
        """
        # lowpass filter for foot motion
        rel_foot_motion_low_passed = signal.filtfilt(b, a, df['rel_foot_motion'])

        # smooth curves:
        # Savitzky-Golay filter
        y_foot_rel = df.loc[x_cutoff_value:, 'rel_foot_motion']
        y_foot_rel_lp = rel_foot_motion_low_passed[x_cutoff_value:]
        # smooth original foot motion without low pass filter
        y_foot_rel_smoothed = signal.savgol_filter(y_foot_rel, smooth_wind, 3)
        # smooth low-pass-filtered rel foot motion
        y_foot_rel_lp_smoothed = signal.savgol_filter(y_foot_rel_lp, smooth_wind, 3)

        # compute and plot intersection points:
        x_axis_f = np.zeros(data_rows_count - 1 - x_cutoff_value)
        idx = np.argwhere(np.diff(np.sign(x_axis_f - y_foot_rel_smoothed))).flatten()
        intersections_dict = {"idx":[], "sign":[]}
        for i in idx:
            intersections_dict["idx"].append(i)
            intersections_dict["sign"].append(np.sign(x_axis_f[i] - y_foot_rel_smoothed[i]))
        intersections_dict['idx'] = [b+x_cutoff_value for b in intersections_dict['idx']]
        #print("x intersections: ", intersections_dict)

        # remove intersection points when lizard has stopped walking:
        #intersections_dict = remove_standing_intersections(intersections_dict, x_axis_f, y_foot_rel_lp_smoothed)

        if plotting == True:
            df['rel_foot_motion'].plot(color='#f5c242')  # plot rel_foot
            plt.plot(x, rel_foot_motion_low_passed, color='green', label='rel_foot_motion low pass (lp) filter')
            plt.plot(x_cutoff, y_foot_rel_smoothed, color='red', label='rel_foot_motion_smoothed')
            plt.plot(x_cutoff, y_foot_rel_lp_smoothed, color='lightgreen', label='rel_foot_motion_lp_smoothed')
            plt.plot(x_cutoff[idx], x_axis_f[idx], 'ko')    # plot intersection points

            #TODO: plot df_pred
            num_plot_col = int(len(list(df_pred_all.columns))/3)
            columns_df_plot = list(df_pred_all.columns)
            print(columns_df_plot)
            for col, name in zip(range(num_plot_col), columns_df_plot):
                if name == "foot_motion":
                    print(name)
                    idx_plot = df_pred_all.index[df_pred_all[f'{name}_pred'] <= 0]
                    print("number of plotted outliers in foot_motion: ", len(idx_plot))
                    for idx in idx_plot:
                        plt.axvline(idx, alpha=0.5, linestyle='--', linewidth=0.3)

            for i in range(len(intersections_dict['idx'])):
                plt.annotate(intersections_dict['idx'][i],
                             (x_cutoff[intersections_dict['idx'][i]-x_cutoff_value] - 5, x_axis_f[intersections_dict['idx'][i]-x_cutoff_value] + 3))

    else:       # relative == False
        """
        Uses the foot motion and the body motion and computes the intersection points for the smoothed curves.
        Intersection points for the lizard standing (bodymotion -> 0) will get excluded by using a body-motion threshold
        of 10% of max(body_motion_lp_smoothed).
        """
        # lowpass filter for body motion
        body_motion_low_passed = signal.filtfilt(b, a, df['body_motion'])
        # lowpass filter for foot motion
        foot_motion_low_passed = signal.filtfilt(b, a, df['foot_motion'])

        # smooth curves with savgol filter:
        y_body = df.loc[x_cutoff_value:, 'body_motion']
        y_body_lp = body_motion_low_passed[x_cutoff_value:]
        y_foot = df.loc[x_cutoff_value:, 'foot_motion']
        y_foot_lp = foot_motion_low_passed[x_cutoff_value:]

        # smooth original body motion without low pass filter
        y_body_smoothed = signal.savgol_filter(y_body, smooth_wind, 3)
        # smooth low-pass-filtered body motion
        y_body_lp_smoothed = signal.savgol_filter(y_body_lp, smooth_wind, 3)
        # smooth original foot motion without low pass filter
        y_foot_smoothed = signal.savgol_filter(y_foot, smooth_wind, 3)
        # smooth low-pass-filtered rel foot motion
        y_foot_lp_smoothed = signal.savgol_filter(y_foot_lp, smooth_wind, 3)

        # compute and plot intersection points:
        # choose functions here which are used for intersections: here smoothed body (darkblue) and smoothed foot (red)
        y_foot_for_intersections = y_foot_smoothed
        idx = np.argwhere(np.diff(np.sign(y_body_lp_smoothed - y_foot_for_intersections))).flatten()
        intersections_dict = {"idx": [], "sign": []}
        max_body_motion = max([abs(max(y_body_lp_smoothed)), abs(min(y_body_lp_smoothed))])
        body_motion_stand = round(max_body_motion*0.1, 2)
        #print(f"max body motion: {max_body_motion}, 10%: {body_motion_stand}")
        for i in idx:
            # exclude all intersections which are within 0+-1% of max body motion (~standing)
            if abs(y_body_lp_smoothed[i]) >= body_motion_stand:
                intersections_dict["idx"].append(i)
                intersections_dict["sign"].append(np.sign(y_body_lp_smoothed[i] - y_foot_for_intersections[i]))
        intersections_dict['idx'] = [b + x_cutoff_value for b in intersections_dict['idx']]
        #print("x intersections: ", intersections_dict)

        # remove intersection points when lizard has stopped walking (usually in the end):
        #intersections_dict = remove_standing_intersections(intersections_dict, y_body_lp_smoothed, y_foot_lp_smoothed)

        if plotting == True:
            df['body_motion'].plot(color='#3089db')  # plot body motion
            df['foot_motion'].plot(color='#fca900')  # plot foot motion = orange
            df_pred_outliers['foot_motion'].plot(color='#5e3f00', label='foot_motion no outliers', linestyle=':',
                                                 linewidth=0.5)   # foot motion with outliers removed
            plt.plot(x, body_motion_low_passed, color='lightblue', label='body_motion low pass (lp) filter')
            plt.plot(x, foot_motion_low_passed, color='green', label='foot_motion low pass (lp) filter')
            plt.plot(x_cutoff, y_body_smoothed, color='#160578', label='body_motion_smoothed')
            plt.plot(x_cutoff, y_foot_smoothed, color='red', label='foot_motion_smoothed')
            plt.plot(x_cutoff, y_body_lp_smoothed, color='#9934b3', label='body_motion_lp_smoothed')
            plt.plot(x_cutoff, y_foot_lp_smoothed, color='lightgreen', label='foot_motion_lp_smoothed')
            plt.plot(x_cutoff[idx], y_body_lp_smoothed[idx], 'ko')  # plot intersection points

            # TODO: plot df_pred
            num_plot_col = int(len(list(df_pred_all.columns)) / 3)
            columns_df_plot = list(df_pred_all.columns)
            print(columns_df_plot)
            for col, name in zip(range(num_plot_col), columns_df_plot):
                if name == "foot_motion":
                    print(name)
                    idx_plot = df_pred_all.index[df_pred_all[f'{name}_pred'] <= 0]
                    print("number of plotted outliers in foot_motion: ", len(idx_plot))
                    for idx in idx_plot:
                        plt.axvline(idx, alpha=0.5, linestyle='--', linewidth=0.3)

            for i in range(len(intersections_dict['idx'])):
                plt.annotate(intersections_dict['idx'][i],
                             (x_cutoff[intersections_dict['idx'][i] - x_cutoff_value] - 5,
                              y_body_lp_smoothed[intersections_dict['idx'][i] - x_cutoff_value] + 3))

    if plotting == True:
        # set y-limits, add legend and display plots
        plt.axhline(0, color='black')
        plt.ylim(-30, 30)
        plt.legend()
        plt.xlabel('frames')
        plt.ylabel('dx/frame')
        plt.title(f"{filename_title}-{foot}")

        try:
            os.makedirs(step_detection_folder)
            # print("folder for curve_fitting plots created")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        if relative == True:
            plt.savefig(os.path.join(step_detection_folder, f"steps_{filename_title}_{foot}_rel.pdf"))
        else:
            plt.savefig(os.path.join(step_detection_folder, f"steps_{filename_title}_{foot}.pdf"))

        #plt.show()
        plt.clf()
        plt.close()
    return intersections_dict


def remove_standing_intersections(intersection_dict, foot_function, body_function):
    """
    NOT USED ATM
    """
    from scipy.integrate import quad
    # TODO: find functions for foot and body curves
    # use area underneath curve between intersection points.
    # If area smaller than 5% of the area before, remove index after that
    idxs = intersection_dict['idx']
    signs = intersection_dict['sign']
    areas = []
    for i in range(1,len(idxs)-1):
        # set integral limits
        a = idxs[i-1]
        b = idxs[i]
        if signs[i] > 0:    # if sign is positive, foot curve will be greater than body curve, hence integral(foot-body)
            f = foot_function
            g = body_function
        else:               # if sign is negative, body curve will be greater, hence integral(body-foot)
            f = body_function
            g = foot_function
        # calculate the area between the two curves: Intergal((f(x)-g(x))dx)
        area = quad((f - g), a, b)
        areas.append(area)
    # check subsequent area sizes to discard idx:

    return intersection_dict


class StridesAndStances:
    """
    class to detect stride and stance phases for current feet => initialize class instance for every foot.
    This method iterates through all frames, if the current frame is one of the intersection points, the sign of the
    point will be checked. If the sign is positive the phase will be set to swing and the swing_phase_counter increased
    by 1. All frames until the next intersection will be assigned that phase name and number.
    Rows before and after first and last index respectively will be filled with np.nan.
    """
    def __init__(self):
        import numpy as np
        self.stride_phase_counter = 0
        self.stance_phase_counter = 0
        self.phase = 'UNKNOWN'
        self.current_phase = np.nan

    def determine_stride_phases(self, intersection_dict, data_rows_count):
        """
        Function to detect the swing or stance phases using the intersection points and their signs.
        Return: list with one entry for every row.
        """
        import numpy as np

        # create empty list with length of data rows count:
        results = np.full((data_rows_count,), '', dtype='S10')
        index = 0
        for row in range(data_rows_count):
            # switch swing or stance depending on sign of intersection point
            if row in intersection_dict['idx']:
                index = intersection_dict['idx'].index(row)     # find the index in list of current idx
                sign = intersection_dict['sign'][index]         # find the respective sign
                # if sign is positive, the phase till next idx will be swing
                self.current_phase = self.assign_swing_or_stance(sign)
            # fill all rows until next idx with that swing or stance number
            results[row] = self.current_phase
        # fill all rows after last idx with np.nan
        if index != 0:
            results[intersection_dict['idx'][index]:] = np.nan
        # print("results: ", results)
        return results

        # Todo: Go through intersection_dict and assign correct swing or stance phase for every row
    def assign_swing_or_stance(self, sign):
        if sign > 0:  # swing
            if self.phase == 'stance' or self.phase == 'UNKNOWN':
                self.stride_phase_counter += 1
            self.phase = 'swing'  # originally called stride
            retval = f'swing{self.stride_phase_counter:04d}'

        else:  # stance
            if self.phase == 'swing' or self.phase == 'UNKNOWN':
                self.stance_phase_counter += 1
            self.phase = 'stance'
            retval = f'stance{self.stance_phase_counter:04d}'
        return retval

    def __str__(self):
        return f"swings: {self.stride_phase_counter}, stances: {self.stance_phase_counter}"


def plot_footfall_pattern(results, data_rows_count, filename, plotting_footfall_folder):
    """
    takes the result dataframe and creates a new dataframe for plotting. Every foot gets assigned an individual number.
    The dataframe is then filtered for strings containing "stride", the strides get replaced by the respective number,
    while all stances will be NaN.
    In the plot strides are therefore displayed as bars and stances are empty.
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import os
    import errno

    df_plot = pd.DataFrame(columns = results.keys(), index=range(data_rows_count))
    # filter here and only fill in stances as numbers => stances bars, strides white
    for i, key in enumerate(results):
        df_plot[key] = [i+1 if s.startswith(b'stance') else np.NaN for s in results[key]]

    key_list = [key for key in df_plot.columns]

    colors = False

    if colors:
        cmap = plt.cm.coolwarm
        legend_elements = [Line2D([0], [0], color=cmap(0.), lw=4, label=key_list[0]),
                    Line2D([0], [0], color=cmap(.33), lw=4, label=key_list[1]),
                    Line2D([0], [0], color=cmap(.66), lw=4, label=key_list[2]),
                    Line2D([0], [0], color=cmap(1.), lw=4, label=key_list[3]),
                    Line2D([0], [0], color='black', lw=4, label='stance phases'),
                    Line2D([0], [0], color='white', lw=4, label='stride phases')]
        fig, ax = plt.subplots()
        df_plot.plot(linewidth=10, color=cmap(np.linspace(0, 1, 5)), ax=ax)
        ax.legend(handles=legend_elements)
    else:
        legend_elements = [Line2D([0], [0], color='white', lw=1, label='1 = L1  |  2 = L2  |  3 = L3  |  4 = L4  |  '
                                                                       '5 = R1  |  6 = R2  |  7 = R3  |  8 = R4'),
                           Line2D([0], [0], color='black', lw=4, label='stance phases'),
                           Line2D([0], [0], color='white', lw=4, label='stride phases')]
        fig, ax = plt.subplots()
        df_plot.plot(linewidth=10, color='black', ax=ax)
        ax.legend(handles=legend_elements)


    # saves footfall pattern diagrams as pdf in defined result folder. If folder is not extant yet, it will be created
    try:
        os.makedirs(plotting_footfall_folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    plt.savefig(os.path.join(plotting_footfall_folder, "{}.pdf".format(filename)))
    plt.clf()
    plt.close()

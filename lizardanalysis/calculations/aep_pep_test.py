def aep_pep_test(**kwargs):
    """
    Calculates two different things:
    1.) The x and y coordinates of the AEP and PEP, relative to the coxa of a respective leg
    2.) The swing phases and the stance phases, identifying on a frame by frame basis

    Return: results data frame with 30 key value pairs:

    x6 allocation of swing and stance phases for each foot/leg
    x6 x coordinates of AEP for each foot/leg
    x6 y coordinates for AEP for each foot/leg
    x6 x coordinates for PEP for each foot/leg
    x6 y coordinates for PEP for each foot/leg

    """

    import os.path
    import pandas as pd
    from pandas import np
    from pathlib import Path
    from lizardanalysis.utils import animal_settings
    from scipy import signal
    import math

    # print("footfall_by_switches")

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    config = kwargs.get('config')
    filename = kwargs.get('filename')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')
    df_result_current = kwargs.get('df_result_current')

    # added in this so that you can get the estimated values from alpha
    # so long as that column currently resides in the data frame

    config_file = Path(config).resolve()
    # result folder for footfall plots
    step_detection_folder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results",
                                         "step_detection")
    # create file path for foot fall pattern diagrams
    plotting_footfall_folder = os.path.join(step_detection_folder, "footfall-pattern-diagrams")

    # TODO: instead of hard-coding the feet and the three points for body_motion,
    # TODO: let the user choose based on labels available in DLC result file: Choose feet & choose body motion
    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)

    relative = False
    plotting_footfall_patterns = True

    # define cut-off value -> crops X% of frames on each side of video
    p_cut_off = 0.05

    body_motion = {"frame": [], "mean_motion_x": []}
    abdomen_diff = 0
    head_diff = 0
    # assuming that the body from the head to the abdomen is rigid?

    # this for loop is used to calculate the x coordinate difference between a given frame and the previous
    # therefore gives you can indicator of the direction of motion
    # if the [row] - [row-1] > 0 , then the stick insect is moving to the right
    # if the [row] - [row-1] < 0, then the stick insect is moving to the left

    for row in range(1, data_rows_count):

        if data.loc[row][scorer, "head", 'likelihood'] >= likelihood and data.loc[row - 1][
            scorer, "head", 'likelihood'] >= likelihood:
            head_diff = data.loc[row][scorer, "head"] - data.loc[row - 1][scorer, "head"]

        if data.loc[row][scorer, "abdomen", 'likelihood'] >= likelihood and data.loc[row][
            scorer, "abdomen", 'likelihood'] >= likelihood:
            abdomen_dif = data.loc[row][scorer, "head",]

        body_motion['frame'].append(row - 1)
        body_motion['mean_motion_x'].append(abs((head_diff + abdomen_diff) / 2.0))

        # am taking the absolute value, because if the stick insect walks to the left, then you don't want to
        # switch the which sign changes indicates swing/pep and which sign change indicates stance/aep.

        # taking the average of the differences, to determine the average 'speed' i.e. the displacement over one frame of the whole body

        # one class instance and one result array for every foot, since every foot needs its own counter
        calculators = {}
        results = {}


        # for every foot, need to do within the original for loop, so all foot calculations are performed for a given frame
        foot_motions = {}
        rel_foot_motions = {}
        # left the for loop for the body motion, and will now be working with for loops for the foot motion

        for foot in feet:
            foot_motions[f"{foot}"] = []
            rel_foot_motions[[f"rel_{foot}"]] = []

            # if the [row] - [row-1] > 0 , then the stick insect FOOT is moving to the right
            # if the [row] - [row-1] < 0, then the stick insect FOOT is moving to the left

            # taking an absolute value for the body and foot motions avoid issues with directions (?)

            foot_motion = 0
            for f_row in range(1, data_rows_count):
                if data.loc[f_row][scorer, f"{foot}", 'likelihood'] >= likelihood and data.loc[f_row - 1][scorer,
                                                                                                          f"{foot}"] >= likelihood:
                    foot_motion = abs(data.loc[f_row][scorer, f"{foot}", 'x'] - data.loc[f_row - 1][
                        scorer, f"{foot}", 'x'])
                    foot_motions[f"{foot}"].append(foot_motion)

                    rel_foot_motions[f"rel{foot}"].append(foot_motion - body_motion['mean_motion_x'][f_row - 1])

            # now need to store the body motion data, the foot motion data, and the relative foot motion all in a dataframe
            # this dataframe within the loop is only for one foot
            dict_df = {'body_motion': body_motion['mean_motion_x'], 'foot_motion': foot_motions[f"{foot}"],
                       "rel_foot_motion": rel_foot_motions[f"rel_{foot}"]}

            df = pd.DataFrame.from_dict(dict_df)

            intersections = smooth_and_plot(df, data_rows_count, p_cut_off, relative, foot, filename,
                                            step_detection_folder)

            ######################################################################################################################

            # the smooth_and_plot function returns 'intersection_dict'
            # intersection dict is: {"idx":[], "sign":[]}
            # idx = the idx of the number list/array of differences in the sign, only storing when the differences are non-zero
            # sign = stores the sign of the number associated with the index of the non zero number
            # positive => start of swing =>PEP
            # negative => start of stance => AEP

            # gives the alpha_estimation values for the

            rom_list = [col for col in df_result_current.columns if ("rom_angle_{}".format(foot) in col)]

            aep_pep_angle = []

            # for loop will calculate the angle that defines the femur-coxa vector relative to the normal
            # to the body axis, running through the coxa of the foot of interest
            for angle in range(len(rom_list)):
                aep_pep_angle.append(90 - angle)

            foot_chars = list(foot)
            f_t_joint_lpx = []
            f_t_joint_lpy = []
            t_c_joint_lpx = []
            t_c_joint_lpy = []

            # low pass filter application of the coordinate data alone?
            # is this necessary

            b, a = signal.butter(3, 0.1, btype='lowpass', analog=False)

            f_t_joint_lpx = signal.filtfilt(b, a,
                                            (data.loc[:, (scorer, "{}m{}".format(foot_chars[0], foot_chars[1]), "x")]))
            f_t_joint_lpy = signal.filtfilt(b, a,
                                            (data.loc[:, (scorer, "{}m{}".format(foot_chars[0], foot_chars[1]), "y")]))

            t_c_joint_lpx = signal.filtfilt(b, a,
                                            (data.loc[:, (scorer, "{}b{}".format(foot_chars[0], foot_chars[1]), "x")]))
            t_c_joint_lpy = signal.filtfilt(b, a,
                                            (data.loc[:, (scorer, "{}b{}".format(foot_chars[0], foot_chars[1]), "y")]))

            # ensuring that the values for the keys are defined as arrays, so that you can append for the
            # following for loop
            results_aep = {"{}_x".format(foot): [], "{}_y".format(foot): []}
            results_pep = {"{}_x".format(foot): [], "{}_y".format(foot): []}


            for i in range(2, data_rows_count):

                if i - 2 in intersections["idx"]:

                    # atm just leaving the likelihood check
                    # is it worth doing, considering the alpha angles depended on those likelihoods anyway?
                    # so you would be just checking the same likelihood even though

                    # now calculating the Euclidean distance between the coxa label and the femur label

                    f_t_joint_co = (f_t_joint_lpx[i], f_t_joint_lpy[i])
                    t_c_joint_co = (t_c_joint_lpx[i], t_c_joint_lpy[i])

                    distance = np.sqrt(
                        (f_t_joint_co[0] - t_c_joint_co[0]) ** 2 + (f_t_joint_co[1] - t_c_joint_co[1]) ** 2)

                    # calibrate distance with conversion factor
                    # NEED TO WRITE THE CONVERSION FACTOR!
                    distance_calib = distance / conv_fac

                    # results_aep = {}
                    # results_pep = {}

                    if intersections["sign"][i - 2] > 0:
                        # this means you are transitioning to the swing phase, so should be PEP
                        results_pep[f"{foot}_x"].append((math.cos(aep_pep_angle[i]) * distance_calib))
                        results_pep[f"{foot}_y"].append((math.sin(aep_pep_angle[i]) * distance_calib))

                    if intersections["sign"][i - 2] < 0:
                        # this means you are transitioning to the stance phase so should be aep
                        results_aep[f"{foot}_x"].append((math.cos(aep_pep_angle[i]) * distance_calib))
                        results_aep[f"{foot}_y"].append((math.sin(aep_pep_angle[i]) * distance_calib))

        # therefore should now have two dictionaries that contain the x coordinates and the y coordinates
        # of the aep and the pep for each foot
        # one aep value and one pep value per stepping cycle

        #####################################################################################################################

        # initializes class instance for every foot and empty result dict to be filled with the swing and stance phases:
        calculators[foot] = StridesAndStances()
        # "S10" = string of 10 characters: stance/stride + counter 000n
        results[foot] = calculators[foot].determine_stride_phases(intersections, data_rows_count)

        # rename dictionary keys of results
    results = {'stepphase_' + key: value for (key, value) in results.items()}
    results_aep = {"AEP_" + key: value for(key, value) in results_aep.items()}
    results_pep = {"PEP_" + key: value for(key, value) in results_pep.items()}

    # print("results: ", results)

    if plotting_footfall_patterns:
        """ plots a foot fall pattern diagram for every DLC result csv file/every lizard run """
        plot_footfall_pattern(results, data_rows_count, filename, plotting_footfall_folder)

        ## need to add the result of the code here!

    # last step must be combining the three results dictionaries
    results.update(results_aep)
    results.update(results_pep)


    return results


# shouldn't matter whether the stick insect walks in a straight horizontal line or not, because you're only looking at
# the switch in the direction of movement
# therefore, as long as the insect doesn't walk completely vertically suddenly, then the algorithm should still work

def smooth_and_plot(df, data_rows_count, p_cut_off, relative, foot, filename, step_detection_folder, plotting=True):
    # smoothing of the raw input data from foot motion and body motion, using the Butterworth low-pass filter an a Savintzky-
    # Golay smoothing alogirthm. Then, the intersection points are computed between the smoothed body and foot curves

    # If relative is TRUE: body motion is already subtracted from the foot motion, hence foot is relative to the x-axis
    # If relative is FALSE: the intersection of the foot motion and body motion data curves needs to be determined

    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal
    import os
    import errno

    # savgol filter smoothing window (must be odd!)
    smooth_wind = 13

    x_cut_off_value = int(round(data_rows_count * p_cut_off, 0))
    x = np.linspace(0, data_rows_count - 1, data_rows_count - 1)
    b, a = signal.butter(3, 0.1, btype='lowpass', analog=False)

    x_cut_off = np.linspace(x_cut_off_value, data_rows_count - 1, int(data_rows_count - 1 - x_cut_off_value))

    if plotting == True:
        # initiate plot
        plt.figure()
        plt.axvline(x_cut_off_value, color='black', label='cutoff 0.05%')

    if relative == True:
        """Uses the relative foot motion i.e. the foot motion where body motion has been subtracted"""

        rel_foot_motion_low_passed = signal.filtfilt(b, a, df['rel_foot_motion'])

        # smooth curves with Savitzky-Golay filter:
        y_foot_rel = df.loc[x_cut_off_value:, 'rel_foot_motion']

        y_foot_rel_lp = rel_foot_motion_low_passed[x_cut_off_value:]  # two different types of filtering (?)
        # smooth without the low pass filter
        y_foot_rel_smoothed = signal.savgol_filter(y_foot_rel, smooth_wind, 3)
        # smooth with the low pass filter
        y_foot_rel_lp_smoothed = signal.savgol_filter(y_foot_rel_lp, smooth_wind, 3)

        x_axis_f = np.zeros(data_rows_count - 1 - x_cut_off_value)
        # get the indexes of the frames where you are transitioning from swing -> stance or stance -> swing
        idx = np.argwhere(np.diff(np.sign(x_axis_f - y_foot_rel_smoothed))).flatten()

        intersections_dict = {"idx": [], "sign": []}
        for i in idx:
            intersections_dict["idx"].append(i)
            intersections_dict["sign"].append(np.sign(x_axis_f[i] - y_foot_rel_smoothed[i]))
            intersections_dict["idx"] = [b + x_cut_off_value for b in intersections_dict['idx']]

        if plotting == True:
            df['rel_foot_motion'].plot(color='#f5c242')  # plot_rel_foot
            plt.plot(x, rel_foot_motion_low_passed, color='green', label='rel_foot_motion low pass (lp) filter')
            plt.plot(x_cut_off, y_foot_rel_smoothed, color='red', label='rel_foot_motion_smoothed')
            plt.plot(x_cut_off, y_foot_rel_lp_smoothed, color='lightgreen', label='rel_foot_motion_lp_smoothed')
            plt.plot(x_cut_off[idx], y_foot_rel_lp_smoothed[idx], 'ko')  # plot intersection points
            # edit here -> second argument was changed from x_axis_f to y_foot_rel_lp_smoothed

            for i in range(len(intersections_dict['idx'])):
                plt.annotate(intersections_dict['idx'][i],
                             (x_cut_off[intersections_dict['idx'][i] - x_cut_off_value] - 5,
                              y_foot_rel_lp_smoothed[intersections_dict['idx'][i] - x_cut_off_value] + 3))
        # another edit here?

        else:
            """
            Uses the foot motion and the body motion and computes the intersection points for the smoothed curves.
            Intersection points for the lizard standing (bodymotion -> 0) will get excluded by using a body-motion threshold
            of 10% of max(body_motion_lp_smoothed).
            """
            # lowpass filter for body motion
            body_motion_low_passed = signal.filtfilt(b, a, df['body_motion'])
            # lowpass filter for foot motion
            foot_motion_low_passed = signal.filtfilt(b, a, df['foot_motion'])

            # smooth curves:
            y_body = df.loc[x_cut_off_value:, 'body_motion']
            y_body_lp = body_motion_low_passed[x_cut_off_value:]
            y_foot = df.loc[x_cut_off_value:, 'foot_motion']
            y_foot_lp = foot_motion_low_passed[x_cut_off_value:]
            # smooth original body motion without low pass filter
            y_body_smoothed = signal.savgol_filter(y_body, 51, 3)
            # smooth low-pass-filtered body motion
            y_body_lp_smoothed = signal.savgol_filter(y_body_lp, 17, 3)
            # smooth original foot motion without low pass filter
            y_foot_smoothed = signal.savgol_filter(y_foot, 17, 3)
            # smooth low-pass-filtered rel foot motion
            y_foot_lp_smoothed = signal.savgol_filter(y_foot_lp, 17, 3)

            # compute and plot intersection points:
            idx = np.argwhere(np.diff(np.sign(y_body_lp_smoothed - y_foot_lp_smoothed))).flatten()
            intersections_dict = {"idx": [], "sign": []}
            max_body_motion = max([abs(max(y_body_lp_smoothed)), abs(min(y_body_lp_smoothed))])
            body_motion_stand = round(max_body_motion * 0.1, 2)
            # print(f"max body motion: {max_body_motion}, 10%: {body_motion_stand}")
            for i in idx:
                # exclude all intersections which are within 0+-1% of max body motion (~standing)
                if abs(y_body_lp_smoothed[i]) >= body_motion_stand:
                    intersections_dict["idx"].append(i)
                    intersections_dict["sign"].append(np.sign(y_body_lp_smoothed[i] - y_foot_lp_smoothed[i]))
            intersections_dict['idx'] = [b + x_cut_off_value for b in intersections_dict['idx']]
            # print("x intersections: ", intersections_dict)

            # remove intersection points when lizard has stopped walking (usually in the end):
            # intersections_dict = remove_standing_intersections(intersections_dict, y_body_lp_smoothed, y_foot_lp_smoothed)

            if plotting == True:
                df['body_motion'].plot(color='#3089db')  # plot body motion
                df['foot_motion'].plot(color='#d68f00')  # plot foot motion
                plt.plot(x, body_motion_low_passed, color='lightblue', label='body_motion low pass (lp) filter')
                plt.plot(x, foot_motion_low_passed, color='green', label='foot_motion low pass (lp) filter')
                plt.plot(x_cut_off, y_body_smoothed, color='#160578', label='body_motion_smoothed')
                plt.plot(x_cut_off, y_foot_smoothed, color='red', label='foot_motion_smoothed')
                plt.plot(x_cut_off, y_body_lp_smoothed, color='#9934b3', label='body_motion_lp_smoothed')
                plt.plot(x_cut_off, y_foot_lp_smoothed, color='lightgreen', label='foot_motion_lp_smoothed')
                plt.plot(x_cut_off[idx], y_body_lp_smoothed[idx], 'ko')  # plot intersection points
                for i in range(len(intersections_dict['idx'])):
                    plt.annotate(intersections_dict['idx'][i],
                                 (x_cut_off[intersections_dict['idx'][i] - x_cut_off_value] - 5,
                                  y_body_lp_smoothed[intersections_dict['idx'][i] - x_cut_off_value] + 3))

        if plotting == True:
            # set y-limits, add legend and display plots
            plt.axhline(0, color='black')
            plt.ylim(-30, 30)
            plt.legend()
            plt.xlabel('frames')
            plt.ylabel('dx/frame')
            filename_title = filename.split("_", 2)[:2]
            filename_title = filename_title[0] + filename_title[1]
            plt.title(f"{filename_title}-{foot}")
            # plt.show()

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

            # plt.show()
            plt.close()
        return intersections_dict


## removed the unused function, might need to put back in at some point

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
                index = intersection_dict['idx'].index(row)  # find the index in list of current idx
                sign = intersection_dict['sign'][index]  # find the respective sign
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

    df_plot = pd.DataFrame(columns=results.keys(), index=range(data_rows_count))
    # filter here and only fill in stances as numbers => stances bars, strides white
    for i, key in enumerate(results):
        df_plot[key] = [i + 1 if s.startswith(b'stance') else np.NaN for s in results[key]]

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
        legend_elements = [Line2D([0], [0], color='white', lw=1, label='1 = FL  |  2 = FR  |  3 = HR  |  4 = HL'),
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

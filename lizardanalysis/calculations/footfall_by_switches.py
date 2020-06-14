def footfall_by_switches(**kwargs):
    import os.path
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from pathlib import Path
    from scipy import signal
    from lizardanalysis.utils import auxiliaryfunctions

    print("footfall_by_switches")

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    config = kwargs.get('config')
    filename = kwargs.get('filename')

    config_file = Path(config).resolve()

    # TODO: instead of hard-coding the feet and the three points for body_motion,
    # TODO: let the user choose based on labels available in DLC result file: Choose feet & choose body motion
    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]

    relative = False

    # define cut-off value -> crops 10% of frames on each side of video:
    p_cut_off = 0.05

    # read in all the frames for hip, spine and shoulder (x) to get mean body motion
    body_motion = {"frame":[], "mean_motion_x":[]}
    for row in range(1, data_rows_count):
        # go through frames and extract the x-diff for body-axis labels; take the mean and store in dict
        hip_diff = data.loc[row][scorer, "Hip", 'x'] - data.loc[row-1][scorer, "Hip", 'x']
        shoulder_diff = data.loc[row][scorer, "Shoulder", 'x'] - data.loc[row-1][scorer, "Shoulder", 'x']
        body_motion['frame'].append(row-1)
        body_motion['mean_motion_x'].append((hip_diff + shoulder_diff)/2.0)

    # for every foot:
    foot_motions = {}
    rel_foot_motions = {}
    for foot in feet:
        foot_motions[f"{foot}"] = []
        rel_foot_motions[f"rel_{foot}"] = []
        # read in all frames (x) differences: if moving forward = pos, if moving backwards = neg
        for row in range(1, data_rows_count):
            foot_motion = data.loc[row][scorer, f"{foot}", 'x'] - data.loc[row-1][scorer, f"{foot}", 'x']
            # foot motion
            foot_motions[f"{foot}"].append(foot_motion)
            # foot motion - body motion
            rel_foot_motions[f"rel_{foot}"].append(foot_motion - body_motion['mean_motion_x'][row-1])
        print('foot_motions: ', foot_motions)
        # create dataframe with >> frame | body_motion | rel_foot_motion << for current foot
        dict_df = {'body_motion':body_motion['mean_motion_x'],
                   'foot_motion':foot_motions[f"{foot}"],
                   'rel_foot_motion':rel_foot_motions[f"rel_{foot}"]}
        df = pd.DataFrame.from_dict(dict_df)
        # print("df: ", df)

        # gets the x-values for switch in swing and stance phases (after smoothing data)
        idx = smooth_and_plot(df, data_rows_count, p_cut_off, relative, foot, filename)

        # check for change in sign: positive to body = swing, negative to body = stance


def smooth_and_plot(df, data_rows_count, p_cut_off, relative, foot, filename, plotting=True):
    """
    Smooths the raw input data from foot motion and body motion, and computed the intersection points
    between foot and body curves.
    If relative is True, body motion is already subtracted from the foot motion, hence it is relative to the x-axis.
    If relative is False, intersection between foot motion and body motion is determined.
    If plotting is True: plots the footfall and body motion curves, and the intersection points between the
    smoothed curve and the x-axis (switch betw. swing and stance phase)

    return: list with x-values (frames) of intersection points
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import signal

    # determine p_cutoff position:
    x_cutoff_value = int(round(data_rows_count * p_cut_off, 0))

    # add low pass filter to cut off spikes in data:
    # Butterworth filter
    x = np.linspace(0, data_rows_count - 1, data_rows_count - 1)
    b, a = signal.butter(3, 0.1, btype='lowpass', analog=False)

    x_cutoff = np.linspace(x_cutoff_value, data_rows_count - 1, int(data_rows_count - 1 - x_cutoff_value))

    if plotting == True:
        # initiate plot
        plt.figure()
        plt.axvline(x_cutoff_value, color='black', label='cutoff 0.05%')

    if relative == True:
        # lowpass filter for foot motion
        rel_foot_motion_low_passed = signal.filtfilt(b, a, df['rel_foot_motion'])

        # smooth curves:
        # Savitzky-Golay filter
        y_foot_rel = df.loc[x_cutoff_value:, 'rel_foot_motion']
        y_foot_rel_lp = rel_foot_motion_low_passed[x_cutoff_value:]
        # smooth original foot motion without low pass filter
        y_foot_rel_smoothed = signal.savgol_filter(y_foot_rel, 17, 3)
        # smooth low-pass-filtered rel foot motion
        y_foot_rel_lp_smoothed = signal.savgol_filter(y_foot_rel_lp, 17, 3)

        # compute and plot intersection points:
        x_axis_f = np.zeros(data_rows_count - 1 - x_cutoff_value)
        idx = np.argwhere(np.diff(np.sign(x_axis_f - y_foot_rel_lp_smoothed))).flatten()
        print("x intersections: ", idx)

        if plotting == True:
            df['rel_foot_motion'].plot(color='#f5c242')  # plot rel_foot
            plt.plot(x, rel_foot_motion_low_passed, color='green', label='rel_foot_motion low pass (lp) filter')
            plt.plot(x_cutoff, y_foot_rel_smoothed, color='red', label='rel_foot_motion_smoothed')
            plt.plot(x_cutoff, y_foot_rel_lp_smoothed, color='lightgreen', label='rel_foot_motion_lp_smoothed')
            plt.plot(x_cutoff[idx], x_axis_f[idx], 'ko')    # plot intersection points
            for i in range(len(idx)):
                plt.annotate(idx[i], (x_cutoff[idx[i]] - 5, x_axis_f[idx[i]] + 3))

    else:
        # lowpass filter for body motion
        body_motion_low_passed = signal.filtfilt(b, a, df['body_motion'])
        # lowpass filter for foot motion
        foot_motion_low_passed = signal.filtfilt(b, a, df['foot_motion'])

        # smooth curves:
        y_body = df.loc[x_cutoff_value:, 'body_motion']
        y_body_lp = body_motion_low_passed[x_cutoff_value:]
        y_foot = df.loc[x_cutoff_value:, 'foot_motion']
        y_foot_lp = foot_motion_low_passed[x_cutoff_value:]
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
        print("x intersections: ", idx)

        if plotting == True:
            df['body_motion'].plot(color='#3089db')  # plot body motion
            df['foot_motion'].plot(color='#d68f00')  # plot foot motion
            plt.plot(x, body_motion_low_passed, color='lightblue', label='body_motion low pass (lp) filter')
            plt.plot(x, foot_motion_low_passed, color='green', label='foot_motion low pass (lp) filter')
            plt.plot(x_cutoff, y_body_smoothed, color='#160578', label='body_motion_smoothed')
            plt.plot(x_cutoff, y_foot_smoothed, color='red', label='foot_motion_smoothed')
            plt.plot(x_cutoff, y_body_lp_smoothed, color='#9934b3', label='body_motion_lp_smoothed')
            plt.plot(x_cutoff, y_foot_lp_smoothed, color='lightgreen', label='foot_motion_lp_smoothed')
            plt.plot(x_cutoff[idx], y_body_lp_smoothed[idx], 'ko')  # plot intersection points
            for i in range(len(idx)):
                plt.annotate(idx[i], (x_cutoff[idx[i]] - 5, y_body_lp_smoothed[idx[i]] + 3))

    if plotting == True:
        # set y-limits, add legend and display plots
        plt.axhline(0, color='black')
        plt.ylim(-30, 30)
        plt.legend()
        filename_title = filename.split("_", 2)[:2]
        filename_title = filename_title[0]+filename_title[1]
        plt.title(f"{filename_title}-{foot}")
        plt.show()

    return idx
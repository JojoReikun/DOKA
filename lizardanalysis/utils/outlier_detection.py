import sklearn
from sklearn.ensemble import IsolationForest


def detect_outliers(motion_dict, foot):
    import random
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    """
    takes the motion dict which contains body_motion, foot_motion and rel_foot_motion and uses IsolationForest to detect anomalities
    """
    # select random subset
    print(f"\noutlier detection... {foot}")
    subset_percentage = 0.4

    sub_dict = {}
    subset_dict = {}
    columns=motion_dict.keys()
    df_pred_all=pd.DataFrame(columns=columns)
    for k,v in motion_dict.items():     # body_motion, foot_motion, rel_foot_motion
        num_to_pick = int(round(subset_percentage * len(motion_dict[k])))
        print('len[k]: ', len(motion_dict[k]), 'num_to_pick: ', num_to_pick)

        sub_dict[k] = num_to_pick   # contains the key from motion_dict and the num_to_pick
        print("sub_dict: ", sub_dict)

        train_list = random.sample(motion_dict[k], num_to_pick)

        # get the values higher than 0.9 of max value as peaks from data
        peaks_list = get_peaks(v, perc_of_max=0.9)
        # add the peaks list to the fit list
        train_list.extend(peaks_list)
        print("train_list + peaks: ", train_list)

        subset_dict[k] = train_list
        print("subset_dict: ", subset_dict)

        df_pred_all[k] = v
    # fit
    for k,v in subset_dict.items():
        # make v 2D array: v = [1,2,3,4...] --> v = [[1], [2], [3], [4],...]
        v_array = np.array(v)
        v_array_reshaped = v_array.reshape(-1,1)

        clf = IsolationForest(random_state=0).fit(v_array_reshaped)     # train model on subset of x_data
        # predict on all/new data
        array = np.array(motion_dict[k])
        array_reshaped = array.reshape(-1,1)

        pred = clf.predict(array_reshaped)      # predict outliers on x
        df_pred_all[f'{k}_pred'] = pred
        outliers = df_pred_all.loc[df_pred_all[f'{k}_pred'] == -1]
        outlier_index = list(outliers.index)
    print('\ndf_pred :\n', df_pred_all)

    return df_pred_all


def get_peaks(x_list, perc_of_max=0.9):
    max_value = max(max(x_list), abs(min(x_list)))
    max_range = max_value*perc_of_max
    peaks_list = [x for x in x_list if abs(x)>=max_range]
    print("peaks_list: ", peaks_list)
    return peaks_list

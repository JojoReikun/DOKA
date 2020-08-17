import sklearn
from sklearn.ensemble import IsolationForest
from lizardanalysis.utils import auxiliaryfunctions


def detect_outliers(motion_dict, foot, filename_title, step_detection_folder, exploration_plotting):
    import random
    import numpy as np
    import pandas as pd
    import itertools
    import matplotlib.pyplot as plt
    """
    takes the motion dict which contains body_motion, foot_motion and rel_foot_motion and uses IsolationForest 
    to detect anomalities. The contamination is set to 5% of the data.
    subset_percentage determines the size of the training dataset taken randomly from the data and peaks which are 
    >= 90% of the max value occuring in the data are added to the training set.
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
        #print('len[k]: ', len(motion_dict[k]), 'num_to_pick: ', num_to_pick)

        sub_dict[k] = num_to_pick   # contains the key from motion_dict and the num_to_pick for training data set
        #print("sub_dict: ", sub_dict)

        # adds a random subset of num_to_pick data points from motion dict to training list
        train_list = random.sample(motion_dict[k], num_to_pick)

        # get the values higher than perc_of_max of max value as peaks from data
        peaks_list = get_peaks(v, perc_of_max=0.90)

        # add the peaks list to the fit list
        train_list.extend(peaks_list)
        #print("train_list + peaks: ", train_list)

        subset_dict[k] = train_list
        #print("subset_dict: ", subset_dict)

    # Isolation Forest
    for k,v in subset_dict.items():
        # make v 2D array: v = [1,2,3,4...] --> v = [[1], [2], [3], [4],...]
        v_array = np.array(v)
        v_array_reshaped = v_array.reshape(-1,1)

        # set up Isolation Forest
        clf = IsolationForest(random_state=0, contamination=0.1).fit(v_array_reshaped)     # train model on subset of x_data

        # predict on all/new data
        array = np.array(motion_dict[k])
        array_reshaped = array.reshape(-1,1)
        pred = clf.predict(array_reshaped)      # predict outliers on x

        # add status outlier/no outlier to df
        df_pred_all[k] = motion_dict[k]     # original data
        df_pred_all[f'{k}_pred'] = pred     # predictions: 1 = good, -1 = outlier
        df_pred_all[f'{k}_outlier_rm'] = list(itertools.repeat("no", len(motion_dict[k])))

        outliers = df_pred_all.loc[df_pred_all[f'{k}_pred'] == -1]
        outlier_index = list(outliers.index)
        print(f"{k} ---> outlier indices: ", outlier_index)

    df_pred_outliers = df_pred_all.copy()
    for k,v in motion_dict.items():
        # remove outliers --> set to nan:
        mask_nan = df_pred_outliers[f'{k}_pred']==-1
        df_pred_outliers[k] = df_pred_outliers[k].where(~mask_nan, other=np.nan)

        mask_yes = df_pred_outliers[f'{k}_outlier_rm']=='no'
        df_pred_outliers[f'{k}_outlier_rm'] = df_pred_outliers[f'{k}_outlier_rm'].where(~mask_yes, other='yes')
        #print("df_pred_outliers removed: \n", df_pred_outliers)

    # build dataframe suitable for split violinplot:
    pd.set_option('display.max_columns', None)
    print("---> df_pred_all: \n", df_pred_all)
    df_exploration_plot = df_pred_all.append(df_pred_outliers, ignore_index=True)
    #print("df_exploration_plot: ", df_exploration_plot)

    # explore original x_data and after outlier removal:
    if exploration_plotting:
        exploration_plotting_of_original_data(df_pred_all, df_pred_outliers, foot, filename_title, step_detection_folder, save=True)
    #print('\ndf_pred :\n', df_pred_all)

    return df_pred_all, df_pred_outliers


def get_peaks(x_list, perc_of_max):
    max_value = max(max(x_list), abs(min(x_list)))
    max_range = max_value*perc_of_max
    peaks_list = [x for x in x_list if abs(x)>=max_range]
    #print("peaks_list: ", peaks_list)
    return peaks_list


def exploration_plotting_of_original_data(df_pred_all, df_pred_outliers, foot, filename_title, step_detection_folder, save=True):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os
    foldername = os.path.join(step_detection_folder, "OutlierDetection_IsolationForest")
    filename = f"{filename_title}-{foot}-Outlier Detection with Isolation Forest.png"
    plot_key = "foot_motion"
    fig, axs = plt.subplots(ncols=2, constrained_layout=True)
    print("DETETCTED OUTLIERS: ", df_pred_outliers.isna().sum())
    sns.violinplot(x=plot_key, data=df_pred_all, dropna=True, ax=axs[0])
    axs[0].title.set_text("original data")
    sns.violinplot(x=plot_key, data=df_pred_outliers, dropna=True, color='y', ax=axs[1])
    axs[1].title.set_text("outlier removed")
    fig.suptitle(f"{filename_title}-{foot}-Outlier Detection with Isolation Forest", y=1.0)

    if save:
        auxiliaryfunctions.attempttomakefolder(step_detection_folder)
        auxiliaryfunctions.attempttomakefolder(foldername)
        plt.savefig(os.path.join(foldername, filename))

    #plt.show()


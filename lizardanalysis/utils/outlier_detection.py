import sklearn
from sklearn.ensemble import IsolationForest


def detect_outliers(motion_dict, foot):
    import random
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    import matplotlib.pyplot as plt
    """
    takes the motion dict which contains body_motion, foot_motion and rel_foot_motion and uses IsolationForest to detect anomalities
    """
    # select random subset
    print(f"\noutlier detection... {foot}")
    subset_percentage = 0.6
    sub_dict = {}
    subset_dict = {}
    for k,v in motion_dict.items():     # body_motion, foot_motion, rel_foot_motion
        num_to_pick = round(0.6 * len(motion_dict[k]))
        print('len[k]: ', len(motion_dict[k]), 'num_to_pick: ', num_to_pick)
        sub_dict[k] = num_to_pick   # contains the key from motion_dict and the num_to_pick
        print("sub_dict: ", sub_dict)
        subset_dict[k] = random.sample(motion_dict[k], num_to_pick)
        print("subset_dict: ", subset_dict)
    # fit
    for k,v in subset_dict.items():
        # make v 2D array: v = [1,2,3,4...] --> v = [[1], [2], [3], [4],...]
        v_array = np.array(v)
        v_array_reshaped = v_array.reshape(-1,1)
        clf = IsolationForest(random_state=0).fit(v_array_reshaped)
        # predict on all/new data
        array = np.array(motion_dict[k])
        array_reshaped = array.reshape(-1,1)
        pred = clf.predict(array_reshaped)
        df_pred = pd.DataFrame({k:motion_dict[k], f'{k}_pred':pred})
        outliers = df_pred.loc[df_pred[f'{k}_pred'] == -1]
        outlier_index = list(outliers.index)
        print("key: ", k, "prediciton: ", pred, '\ndf_pred :\n', df_pred)
        print("total, detected outliers: \n", df_pred[f'{k}_pred'].value_counts())
        df_pred.plot(x =f'{k}_pred', y=k, kind = 'scatter')
        plt.show()


        # pca = PCA(2)
        # pca.fit(array_reshaped)
        # res = pd.DataFrame(pca.transform(array_reshaped))
        # Z = np.array(res)
        # plt.title("IsolationForest")
        # plt.contourf(Z, cmap=plt.cm.Blues_r)
        # b1 = plt.scatter(res[0], res[1], c='green',
        #                  s=20, label="normal points")
        # b1 = plt.scatter(res.iloc[outlier_index, 0], res.iloc[outlier_index, 1], c='green', s=20, edgecolor="red",
        #                  label="predicted outliers")
        # plt.legend(loc="upper right")
        # plt.show()



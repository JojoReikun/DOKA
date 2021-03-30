import pandas as pd
import numpy as np
from pathlib import Path
from scipy.spatial import distance
from math import factorial, atan2, degrees, acos, sqrt, pi

from lizardanalysis.utils import auxiliaryfunctions
#TODO: check why files only contain species names but no measurements!!
analyze_again = True

# utility functions
def calc_distance_between_points_two_vectors_2d(v1, v2):
    '''calc_distance_between_points_two_vectors_2d [pairwise distance between vectors points]
    Arguments:
        v1 {[np.array]} -- [description]
        v2 {[type]} -- [description]
    Raises:
        ValueError -- [description]
        ValueError -- [description]
        ValueError -- [description]
    Returns:
        [type] -- [description]
    testing:
    >>> v1 = np.zeros((2, 5))
    >>> v2 = np.zeros((2, 5))
    >>> v2[1, :]  = [0, 10, 25, 50, 100]
    >>> d = calc_distance_between_points_two_vectors_2d(v1.T, v2.T)
    '''

    # Check dataformats
    if not isinstance(v1, np.ndarray) or not isinstance(v2, np.ndarray):
        raise ValueError('Invalid argument data format')
    if not v1.shape[1] == 2 or not v2.shape[1] == 2:
        raise ValueError('Invalid shape for input arrays')
    if not v1.shape[0] == v2.shape[0]:
        raise ValueError('Error: input arrays should have the same length')

    # Calculate distance
    dist = [distance.euclidean(p1, p2) for p1, p2 in zip(v1, v2)]
    return dist


def angle_between_points_2d_anticlockwise(p1, p2):
    '''angle_between_points_2d_clockwise [Determines the angle of a straight line drawn between point one and two.
        The number returned, which is a double in degrees, tells us how much we have to rotate
        a horizontal line anti-clockwise for it to match the line between the two points.]
    Arguments:
        p1 {[np.ndarray, list]} -- np.array or list [ with the X and Y coordinates of the point]
        p2 {[np.ndarray, list]} -- np.array or list [ with the X and Y coordinates of the point]
    Returns:
        [int] -- [clockwise angle between p1, p2 using the inner product and the deterinant of the two vectors]
    Testing:  - to check:     print(zero, ninety, oneeighty, twoseventy)
        >>> zero = angle_between_points_2d_clockwise([0, 1], [0, 1])
        >>> ninety = angle_between_points_2d_clockwise([1, 0], [0, 1])
        >>> oneeighty = angle_between_points_2d_clockwise([0, -1], [0, 1])
        >>> twoseventy = angle_between_points_2d_clockwise([-1, 0], [0, 1])
        >>> ninety2 = angle_between_points_2d_clockwise([10, 0], [10, 1])
        >>> print(ninety2)
    '''

    """
        Determines the angle of a straight line drawn between point one and two.
        The number returned, which is a double in degrees, tells us how much we have to rotate
        a horizontal line anit-clockwise for it to match the line between the two points.
    """

    xDiff = p2[0] - p1[0]
    yDiff = p2[1] - p1[1]
    ang = degrees(atan2(yDiff, xDiff))
    if ang < 0: ang += 360
    # if not 0 <= ang <+ 360: raise ValueError('Ang was not computed correctly')
    return ang


def calc_angle_between_vectors_of_points_2d(v1, v2):
    '''calc_angle_between_vectors_of_points_2d [calculates the clockwise angle between each set of point for two 2d arrays of points]
    Arguments:
        v1 {[np.ndarray]} -- [2d array with X,Y position at each timepoint]
        v2 {[np.ndarray]} -- [2d array with X,Y position at each timepoint]
    Returns:
        [np.ndarray] -- [1d array with clockwise angle between pairwise points in v1,v2]
    Testing:
    >>> v1 = np.zeros((2, 4))
    >>> v1[1, :] = [1, 1, 1, 1, ]
    >>> v2 = np.zeros((2, 4))
    >>> v2[0, :] = [0, 1, 0, -1]
    >>> v2[1, :] = [1, 0, -1, 0]
    >>> a = calc_angle_between_vectors_of_points_2d(v2, v1)
    '''

    # Check data format
    if v1 is None or v2 is None or not isinstance(v1, np.ndarray) or not isinstance(v2, np.ndarray):
        raise ValueError('Invalid format for input arguments')
    if len(v1) != len(v2):
        raise ValueError('Input arrays should have the same length, instead: ', len(v1), len(v2))
    if not v1.shape[0] == 2 or not v2.shape[0] == 2:
        raise ValueError('Invalid shape for input arrays: ', v1.shape, v2.shape)

    # Calculate
    n_points = v1.shape[1]
    angs = np.zeros(n_points)
    for i in range(v1.shape[1]):
        p1, p2 = v1[:, i], v2[:, i]
        angs[i] = angle_between_points_2d_anticlockwise(p1, p2)

    return angs


# Process single bone
def analyzebone(bp1, bp2):
    """[Computes length and orientation of the bone at each frame]
    Arguments:
        bp1 {[type]} -- [description]
        bp2 {[type]} -- [description]
    """
    print("bone: ", bp1, bp2)
    bp1_pos = np.vstack([bp1.x.values, bp1.y.values]).T
    bp2_pos = np.vstack([bp2.x.values, bp2.y.values]).T

    # get bone length and orientation
    bone_length = calc_distance_between_points_two_vectors_2d(bp1_pos, bp2_pos)
    bone_orientation = calc_angle_between_vectors_of_points_2d(bp1_pos.T, bp2_pos.T)

    # keep the smallest of the two likelihoods
    likelihoods = np.vstack([bp2.likelihood.values, bp2.likelihood.values]).T
    likelihood = np.min(likelihoods, 1)

    # Create dataframe and return
    df = pd.DataFrame.from_dict(dict(
                                    length=bone_length,
                                    orientation=bone_orientation,
                                    likelihood=likelihood,
                                    ))
    # df.index.name=name
    print(df)
    return df


# MAIN FUNC
def calc_morphometrics(config, save_as_csv=True, **kwargs):
    """
    Extracts length and orientation of each "bone" of the skeleton as defined in the config file.
    Parameter
    ----------
    config : string
        Full path of the config.yaml file as a string.
    save_as_csv: bool, optional
        Saves the predictions in a .csv file. The default is ``False``; if provided it must be either ``True`` or ``False``
    destfolder: string, optional
        Specifies the destination folder for analysis data (default is the analysis results -> morphometrics folder).
    """

    import errno
    import os
    import tqdm
    import re
    from glob import glob

    current_path = os.getcwd()
    destfolder = None

    # Load config file, scorer and videos
    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    project_dir = f"{cfg['task']}-{cfg['scorer']}-{cfg['species']}-{cfg['date']}"

    # try to make folder for storing results
    if destfolder is None:
        destfolder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results",
                                  "lizard_morphometrics")
        try:
            os.makedirs(destfolder)
            # print("folder for curve_fitting plots created")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # create filelist of all files:
    files = cfg['file_sets'].keys()  # object type ('CommentedMapKeysView' object), does not support indexing
    filelist = []  # store filepaths as list
    for file in files:
        filelist.append(file)

    # get data and filename:
    individuals = []
    for i in range(1, len(filelist)+1):
        print("file in progress: {} of TOTAL: {} --- Progress: {}%".format(i, len(filelist), np.round(i/(len(filelist))*100)))
        filename = filelist[i-1].rsplit(os.sep, 1)[1]
        filename = filename.rsplit(".", 1)[0]
        temp = re.compile("([a-zA-Z]+)([0-9]+)")
        res = temp.match(filename).groups()
        individual = str(res[0]+res[1])
        #print(individual)
        if individual not in individuals:
            individuals.append(individual)

        file_path_2 = os.path.join(project_dir, "files", os.path.basename(filelist[i-1]))
        file_path = os.path.join(current_path, file_path_2)

        if analyze_again:
            data = pd.read_csv(file_path, delimiter=",",
                               header=[0, 1, 2])  # reads in first csv file in filelist to extract all available labels
            data_rows_count = data.shape[0]  # number of rows already excluded the 3 headers

            scorer = data.columns[1][0]

            # Process skeleton
            if cfg['skeleton'] is None:
                print('no skeleton defined in config. Copy skeleton from DLC config file to lizardanalysis config file.')
                break
            bones = {}
            for bp1, bp2 in cfg['skeleton']:
                name = "{}_{}".format(bp1, bp2)
                bones[name] = analyzebone(data[scorer][bp1], data[scorer][bp2])

            skeleton = pd.concat(bones, axis=1)

            # save
            if save_as_csv:
                skeleton.to_csv(os.path.join(destfolder, '{}_morph.csv'.format(filename)))

    # calculate the means for each individual:
    individual_filelists = {}
    print('\nnumber of individuals in group: ', len(individuals))
    filelist_morph = glob(os.path.join(destfolder, '*_morph.csv'))
    #print("{" + "\n".join("{!r}: {!r},".format(k, v) for k, v in filelist_morph.items()) + "}")
    for individual in individuals:
        individual_filelists[individual] = [file for file in filelist_morph if individual in file]
    mean_of_individuals = {}
    for individual, list_of_runs in individual_filelists.items():
        print("\nINDIVIDUAL: ", individual)
        means_of_run = {}
        i = 0
        for run in list_of_runs:
            print("progress: {}/{}".format(i, len(list_of_runs)))
            data_morph = pd.read_csv(run, delimiter=",", header=[0, 1])  # first two rows as header
            data_morph = data_morph.drop(data_morph.columns[[0]], axis=1)
            data_morph_rows_count = data_morph.shape[0]  # number of rows already excluded the 2 headers
            #print("number of rows: ", data_morph_rows_count)
            data_morph.rename(columns=lambda x: x.strip(), inplace=True)  # remove whitespaces from column names
            scorer = data_morph.columns[1][0]
            if i == 0:
                bones = get_bone_names(data_morph)
            i += 1
            for bone in bones:
                list_for_mean_bone = []
                for row in range(data_morph_rows_count-1):
                    list_for_mean_bone.append(data_morph.loc[row, (bone, 'length')])
                means_of_run[bone] = np.mean(list_for_mean_bone)
        mean_of_individuals[individual] = [(k, np.mean(v)) for k,v in means_of_run.items()]
    #print("mean_of_individuals: ", mean_of_individuals)

    # save means of individuals in summary file:
    morph_csv_columns = ['individual']
    individual = individuals[0]
    for bone_tuple in mean_of_individuals[individual]:
        morph_csv_columns.append(bone_tuple[0])
    print("morph_columns: ", morph_csv_columns)
    print("length of columns: ", len(morph_csv_columns))

    df_morph_means = pd.DataFrame(columns=morph_csv_columns)
    df_morph_means = df_morph_means.loc[:, ~df_morph_means.columns.duplicated()]  # remove duplicate columns
    #df_morph_means = df_morph_means.drop(df_morph_means.columns[[0]], axis=1)
    print(df_morph_means.shape)

    for j, individual in zip(range(len(individuals)+1), mean_of_individuals.keys()):
        new_row = {}
        print(j, individual)
        new_row["individual"] = individual
        for bone_tuple in mean_of_individuals[individual]:
            new_row[bone_tuple[0]] = bone_tuple[1]
        new_row = pd.Series(data=new_row, name=j)
        print("--- new row ---: \n",new_row, len(new_row))
        df_morph_means = df_morph_means.append(new_row, ignore_index=False)
    print(df_morph_means.head())


    # save morph summary to csv:
    df_morph_means.to_csv(os.path.join(destfolder, 'morph_data_summary.csv'))

    print("DONE calculating and saving the morph data")


def get_bone_names(data_morph):
    all_bones = [item for item in list(data_morph)]
    #print("all bones: ", all_bones)
    bones = []
    bones = [bone[0] for bone in all_bones if bone not in bones]
    # removes doubles from list and preserves order:
    seen = set()
    bones_no_doubles = [x for x in bones if not (x in seen or seen.add(x))]
    #print("bones: ", bones_no_doubles)
    #print("number of bones: ", len(bones_no_doubles))
    return bones_no_doubles






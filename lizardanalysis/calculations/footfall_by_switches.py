def switches(**kwargs):
    import os.path
    import numpy as np
    import pandas as pd
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    config = kwargs.get('config')
    filename = kwargs.get('filename')

    config_file = Path(config).resolve()

    scorer = data.columns[1][0]
    feet = ["FL", "FR", "HR", "HL"]

    # read in all the frames for hip, spine and shoulder (x) to get mean body motion
    body_motion = {"frame":[], "mean_motion_x":[]}
    for row in range(1, data_rows_count):
        # go through frames and extract the x-diff for Hip, Spine and Shoulder, take the mean and store in dict
        hip_diff = data.loc[row][scorer, "Hip", 'x'] - data.loc[row-1][scorer, "Hip", 'x']
        spine_diff = data.loc[row][scorer, "Spine", 'x'] - data.loc[row-1][scorer, "Spine", 'x']
        shoulder_diff = data.loc[row][scorer, "Shoulder", 'x'] - data.loc[row-1][scorer, "Shoulder", 'x']
        body_motion['frame'].append(row-1)
        body_motion['mean_motion_x'].append(np.mean(hip_diff, spine_diff, shoulder_diff))

    # for every foot:
        # read in all frames (x)
        # plot relative velocity of foot to body
        # smooth curves
        # check for change in sign: positive to body = swing, negative to body = stance
def stride_and_stance_phases(data, clicked, data_rows_count, config):
    import math
    import numpy as np

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    for foot in feet:
        print("\n", "---------- {} ----------".format(foot))
        foot_coords = data[scorer, "{}".format(foot)]

        # df: only use tracking points with likelihood >= 0.90
        coords_90_likelihood = foot_coords[foot_coords.likelihood >= 0.90]

        # df: find frames with foot attached to the wall (no change in x & y coords between subsequent frames):
        stances = coords_90_likelihood[abs(coords_90_likelihood["x"].diff()) <= 3.0]

        # df: find frames with foot moving / strides (all frames not in stances):
        strides = coords_90_likelihood[~coords_90_likelihood["x"].isin(stances["x"])]
        stride_indices = list(strides.index)

        # find beginning of strides
        stride_beginnings = []
        stride_beginnings.append(stride_indices[0])
        for x in range(len(strides) - 1):
            if (stride_indices[x + 1] - stride_indices[x]) > 1:
                stride_beginnings.append(stride_indices[x + 1])
        print("stride beginnings: ", stride_beginnings)

        # make list with tuples containing the row index of stride_begin and stride_end:
        stride_phases = []
        stride_coords = []
        for s in range(len(stride_beginnings) - 1):
            stride_phases.append(
                (stride_beginnings[s], stride_indices[stride_indices.index(stride_beginnings[s + 1]) - 1]))
            # only keep stride lengths greater than 5 frames:
            stride_phases = [item for item in stride_phases if abs(item[0] - item[1]) >= 3]
        # remove first stride phase as most of the time results in weird curve:
        if len(stride_phases) > 0:
            stride_phases.pop(0)

        # get indices of the beginnings of stance phases (first frame used)
        stance_phase_beginnings = [item[1] + 1 for item in stride_phases]
        print("stance_phase_beginnings: ", stance_phase_beginnings)

        for item in stride_phases:
        # get x and y coords for strides begin and end [[(x,y), (x1,y1)][...]]
            stride_coords.append([(coords_90_likelihood.loc[item[0], "x"],
                                   (coords_90_likelihood.loc[item[0], "y"])),
                                  (coords_90_likelihood.loc[item[1], "x"],
                                   (coords_90_likelihood.loc[item[1], "y"]))])
        print("stride phases: ", stride_phases, "\n",
              "stride coordinates: ", stride_coords)

        # calculate the stride lengths and mean stride length
        stride_lengths = []
        for item in stride_coords:
            stride_length = math.sqrt((item[1][0] - item[0][0]) ** 2 + (item[1][1] - item[0][1]))
            stride_lengths.append(stride_length)
            mean_stride_length = np.mean(stride_lengths)
        print("stride_lengths_{}: ".format(foot), stride_lengths)

    # write to dataframe:
    # 8 columns: strides_and_stances_FR, stride_lengths_FR, strides_and_stances_FL, stride_lengths_FL, ... etc.
    # for row_indices in stride phase 1 = list of "stride1"*len(stride_phase1), list of stride_length1*len(stride_phase1) ... etc.
    stride_and_stance_phases_list = 0
    return {__name__.rsplit('.', 1)[1]: stride_and_stance_phases_list}
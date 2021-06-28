def limb_rom(**kwargs):
    """
    Calculates the angle between the limb vector (knee - shoulder) for every limb/foot and the body axis.
    To determine the Range of Motion, the angle at the beginning of a stride phase is subtracted from the angle at the
    end of the stride phase.
    :return:
    """
    import numpy as np
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings
    from pathlib import Path
    import os.path

    print("limb rom")

    calc_rel_to_body_axis = False
    plotting_vectors = False

    spine_label = 'Spine_B'
    # spine_label = 'Spine'

    #print('LIMB ROM CALCULATION')
    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    likelihood = kwargs.get('likelihood')
    config = kwargs.get('config')
    filename = kwargs.get('filename')
    animal = kwargs.get('animal')

    config_file = Path(config).resolve()
    # print("config path resolved: ", config_file)
    cfg = auxiliaryfunctions.read_config(config_file)

    # TODO: Function in utils giving back results path folder from config resolve
    # create file path for foot fall pattern diagrams
    plotting_limb_ROM_vectors = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results",
                                            "limb_rom_vectors")

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    max_stride_phase_count = 1000
    active_columns = []
    for foot in feet:
        active_columns.append("stepphase_{}".format(foot))

    results = {}

    for foot, column in zip(feet, active_columns):
        #print("\n----------- FOOT: ", foot)
        column = column.strip('')
        #print("column :", column)
        results[foot] = np.full((data_rows_count,), np.NAN)
        limb_rom_foot = []

        for i in range(1, max_stride_phase_count):
            #print('stride phase i: ', i)
            cell_value = loop_encode(i)
            #print("cell value: ", cell_value)
            df_stride_section = df_result_current[df_result_current[column] == cell_value]
            if len(df_stride_section) == 0:
                break
            #print(df_stride_section)
            df_stride_section_indices = list(df_stride_section.index.values)
            #print("indices: ", df_stride_section_indices)

            # only include steps with at least 5 frames
            if len(df_stride_section_indices) >= 5:
                beg_end_tuple = (df_stride_section_indices[0], df_stride_section_indices[-1])
                #print(beg_end_tuple)
                shoulder_foot_likelihood_begin = data.loc[beg_end_tuple[0]][scorer, "Shoulder_{}".format(foot), "likelihood"]
                knee_foot_likelihood_begin = data.loc[beg_end_tuple[0]][scorer, "{}_knee".format(foot), "likelihood"]
                shoulder_foot_likelihood_end = data.loc[beg_end_tuple[1]][scorer, "Shoulder_{}".format(foot), "likelihood"]
                knee_foot_likelihood_end = data.loc[beg_end_tuple[1]][scorer, "{}_knee".format(foot), "likelihood"]
                #print("likelihoods: ", shoulder_foot_likelihood_begin, knee_foot_likelihood_begin)

                # filters data points of labels for likelihood
                if shoulder_foot_likelihood_begin >= likelihood and knee_foot_likelihood_begin >= likelihood and \
                        shoulder_foot_likelihood_end >= likelihood and knee_foot_likelihood_end >= likelihood:

                    limb_vector_begin = ((data.loc[beg_end_tuple[0], (scorer, "Shoulder_{}".format(foot), "x")]
                                          - data.loc[beg_end_tuple[0], (scorer, "{}_knee".format(foot), "x")]),
                                         (data.loc[beg_end_tuple[0], (scorer, "Shoulder_{}".format(foot), "y")]
                                          - data.loc[beg_end_tuple[0], (scorer, "{}_knee".format(foot), "y")]))

                    limb_vector_end = ((data.loc[beg_end_tuple[1], (scorer, "Shoulder_{}".format(foot), "x")]
                                        - data.loc[beg_end_tuple[1], (scorer, "{}_knee".format(foot), "x")]),
                                       (data.loc[beg_end_tuple[1], (scorer, "Shoulder_{}".format(foot), "y")]
                                        - data.loc[beg_end_tuple[1], (scorer, "{}_knee".format(foot), "y")]))

                    if calc_rel_to_body_axis:
                        limb_rom_angle_begin = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_begin,
                                                                                         auxiliaryfunctions.calc_body_axis(data,
                                                                                                                           beg_end_tuple[
                                                                                                                               0],
                                                                                                                           scorer))
                        limb_rom_angle_end = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_end,
                                                                                       auxiliaryfunctions.calc_body_axis(data,
                                                                                                                         beg_end_tuple[
                                                                                                                             1],
                                                                                                                    scorer))
                    else:
                        # TODO: adjust label names --> Spine vs Spine_B --> make flexible
                        # print("foot: ", foot, "\n")
                        # calculate relative to Shoulder-Spine (fore feet) or Hip-Spine (hind feet)
                        spine_shoulder_vector_begin = ((data.loc[beg_end_tuple[0], (scorer, spine_label, "x")] - data.loc[
                            beg_end_tuple[0], (scorer, "Shoulder", "x")]),
                                                       (data.loc[beg_end_tuple[0], (scorer, spine_label, "y")] - data.loc[
                                                           beg_end_tuple[0], (scorer, "Shoulder", "y")]))
                        spine_shoulder_vector_end = ((data.loc[beg_end_tuple[1], (scorer, spine_label, "x")] - data.loc[
                            beg_end_tuple[1], (scorer, "Shoulder", "x")]),
                                                     (data.loc[beg_end_tuple[1], (scorer, spine_label, "y")] - data.loc[
                                                         beg_end_tuple[1], (scorer, "Shoulder", "y")]))
                        spine_hip_vector_begin = ((data.loc[beg_end_tuple[0], (scorer, spine_label, "x")] - data.loc[
                            beg_end_tuple[0], (scorer, "Hip", "x")]),
                                                  (data.loc[beg_end_tuple[0], (scorer, spine_label, "y")] - data.loc[
                                                      beg_end_tuple[0], (scorer, "Hip", "y")]))
                        spine_hip_vector_end = ((data.loc[beg_end_tuple[1], (scorer, spine_label, "x")] - data.loc[
                            beg_end_tuple[1], (scorer, "Hip", "x")]),
                                                (data.loc[beg_end_tuple[1], (scorer, spine_label, "y")] - data.loc[
                                                    beg_end_tuple[1], (scorer, "Hip", "y")]))
                        if foot == "FL" or foot == "FR":

                            #print(spine_shoulder_vector_begin, spine_shoulder_vector_end)
                            limb_rom_angle_begin = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_begin,
                                                                                             spine_shoulder_vector_begin)
                            limb_rom_angle_end = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_end,
                                                                                             spine_shoulder_vector_end)
                            #print("a begin: ", limb_rom_angle_begin, "a end: ", limb_rom_angle_end)

                        elif foot == "HR" or foot == "HL":

                            #print(spine_hip_vector_begin, spine_hip_vector_end)
                            limb_rom_angle_begin = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_begin,
                                                                                             spine_hip_vector_begin)
                            limb_rom_angle_end = auxiliaryfunctions.py_angle_betw_2vectors(limb_vector_end,
                                                                                           spine_hip_vector_end)
                            #print("a begin: ", limb_rom_angle_begin, "a end: ", limb_rom_angle_end)
                        else:
                            print("foot does not equal FL, FR, HL, or HR!")

                        if plotting_vectors:
                            # plot vectors
                            plot_limb_vectors(spine_shoulder_vector_begin, spine_shoulder_vector_end,
                                                  spine_hip_vector_begin,
                                                  spine_hip_vector_end, limb_vector_begin, limb_vector_end,
                                                  plotting_limb_ROM_vectors, filename, foot)

                else:
                    limb_rom_angle_begin = 0.0
                    limb_rom_angle_end = 0.0

                if limb_rom_angle_begin > 0.0 and limb_rom_angle_end > 0.0:
                    limb_rom = abs(limb_rom_angle_end - limb_rom_angle_begin)
                    #limb_rom2 = abs(limb_rom_angle_begin - limb_rom_angle_end)     #it's the same
                    #print("LIMB ROM: ", limb_rom)
                else:
                    limb_rom = 0.0


                #print('limbROM: ', limb_rom)

                if limb_rom > 0.0:
                    for row in range(beg_end_tuple[0], beg_end_tuple[1] + 1):
                        results[foot][row] = limb_rom

    # rename dictionary keys of results
    results = {'limbROM_' + key: value for (key, value) in results.items()}

    return results


def loop_encode(i):
    # get utf-8 encoded version of the string
    cell_value = 'stride000{}'.format(i).encode()
    # print("cell value :", cell_value)
    return cell_value


def plot_limb_vectors(shoulder_vector_begin, shoulder_vector_end, hip_vector_begin, hip_vector_end, limb_angle_begin, limb_angle_end, plotting_limb_ROM_vectors, filename, foot):
    import matplotlib.pyplot as plt
    import os.path
    import errno
    import numpy as np
    V = np.array([[shoulder_vector_begin[0], shoulder_vector_begin[1]],
                  [shoulder_vector_end[0], shoulder_vector_end[1]],
                  [hip_vector_begin[0], hip_vector_begin[1]],
                  [hip_vector_end[0], hip_vector_end[1]],
                  [limb_angle_begin[0], limb_angle_begin[1]],
                  [limb_angle_end[0], limb_angle_end[1]]])
    labels=["shoulder_beg", "shoulder_end", "hip_beg", "hip_end", "limb_beg", "limb_end"]
    #print("vectors: \n", V)
    origin = [0], [0]  # origin point

    #print("PLOT")
    plt.quiver(*origin, V[:,0], V[:,1], color=['b', 'g', 'r', 'c', 'm', 'y'], scale=0.1,
               label=labels)
    plt.legend(["shoulder_beg", "shoulder_end", "hip_beg", "hip_end", "limb_beg", "limb_end"])

    try:
        os.makedirs(plotting_limb_ROM_vectors)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    plt.savefig(os.path.join(plotting_limb_ROM_vectors, "{}_{}_firstStride.png".format(filename, foot)))
    plt.clf()
    plt.close()
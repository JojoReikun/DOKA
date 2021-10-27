def xyLengths_of_feet_to_COM(**kwargs):
    """
    calculates the distances in x and y direction to the COM of the lizard.
    The distance of the COM to the hip scales with the SVL of the lizard with R^2=0.70 (tailpaper, Schultz & Cieri et al., 2021)
    To find the xy location of the COM, use the segment lengths between spine points and find BCOM point on the correct segment:
    e.g.:
        if BCOMhip < hip_seg1 (hip-spine_C):
            find BCOM point on that segment
        elif BCOMhip < (hip_seg1 + hip_seg2):
            find BCOM point on that segment
        else:
            BCOM in front half of lizard --> likely wrong

    The distances of the feet to that BCOM location will be calculated frame-wise.
    :param kwargs:
    :return:
    """

    #### IMPORTS:
    import numpy as np
    import re
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    data = kwargs.get('data')
    filename = kwargs.get('filename')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    likelihood = kwargs.get('likelihood')
    animal = kwargs.get('animal')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    max_stride_phase_count = 1000
    active_columns = []

    for row in range(1, data_rows_count):
        ### 1st) get the BCOM location for the current lizard for the current row:
        # get the species (e.g. hfren) and speciesCode (e.g. hfren11) from filename, assuming that all files start with speciesCode_...:
        speciesCode = filename.rsplit("_", 1)[0]
        species = " ".join(re.findall("[a-zA-Z]+", speciesCode))

        # get SVLs of lizards by species/species code
        SVL_dict_species = animal_settings.get_SVL_of_individuals("lizard", species)
        # extract the SVL in mm for the current individual:
        SVL = SVL_dict_species[speciesCode]

        # calculate the BCOM position
        # y = 0.4718x - 6.2276 equation from SVL and BCOM_hips of geckos in tailpaper
        bcom_hip = 0.4718*SVL - 6.2276
        print("bcom_hip estimate: ", bcom_hip)

        # get the BCOM location by finding the correct segment (seg1 = hip - Spine_C)
        hip_x = data.loc[row, (scorer, "Hip", "x")]
        hip_y = data.loc[row, (scorer, "Hip", "y")]
        Spine_C_x = data.loc[row, (scorer, "Spine_C", "x")]
        Spine_C_y = data.loc[row, (scorer, "Spine_C", "y")]
        Spine_B_x = data.loc[row, (scorer, "Spine_B", "x")]
        Spine_B_y = data.loc[row, (scorer, "Spine_B", "y")]

        hip_seg1_length = np.sqrt((hip_x - Spine_C_x)**2 + (hip_y - Spine_C_y)**2)
        hip_seg1 = ((hip_x-Spine_C_x), (hip_y-Spine_C_y))
        hip_seg2_length = np.sqrt((Spine_C_x - Spine_B_x)**2 + (Spine_C_y - Spine_B_y)**2)
        hip_seg2 = ((Spine_C_x-Spine_B_x), (Spine_C_y-Spine_B_y))

        print("segment lengths: \n", hip_seg1_length, hip_seg2_length)

        ### for intersection point: build a circle around hip with r=length bcom_hip and find intersection of segment.
        #if bcom_hip < hip_seg1_length:
            # find interception of vector of length bcom_hip pointing from hip to a point on that segment
        #elif bcom_hip > hip_seg1_length and bcom_hip < (hip_seg1_length + hip_seg2_length):
            # same as above but for next segment
        #else:
            # print("BCOM in front half of lizard --> likely wrong!")
            # exit()

        # then go through feet and active step column (see spineROM) and get the distances of feet to BCOM

    return

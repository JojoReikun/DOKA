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

        # get the BCOM location by finding the correct segment

        # then go through feet and active step column (see spineROM) and get the distances of feet to BCOM

    return

def step_length(**kwargs):
    #TODO: stride length = dist of body during one stride
    import numpy as np
    import pandas as pd
    from lizardanalysis.utils import animal_settings
    pd.set_option('display.max_columns', None)

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')
    animal = kwargs.get('animal')

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)
    max_stride_phase_count = 1000
    active_columns = []

    return 0
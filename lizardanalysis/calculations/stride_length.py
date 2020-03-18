def step_length(**kwargs):
    #TODO: stride length = dist of body during one stride
    import numpy as np
    import pandas as pd
    pd.set_option('display.max_columns', None)

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    df_result_current = kwargs.get('df_result_current')

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]
    max_stride_phase_count = 1000
    active_columns = []

    return 0
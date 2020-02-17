def stride_and_stance_phases(data, clicked, data_rows_count, config):
    import math
    import numpy as np
    import pandas as pd
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    # set a distance_limit a foot has to move in px to be viewed as stride (can be changed in config, default is 5.0)
    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    distance_limit = cfg['distance_limit']
    if distance_limit is None:
        distance_limit = 5.0

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]

    plotting = True

########################################################################################################################

    # one class instance and one result array for every foot, because every foot needs own counter
    calculators = {}
    results = {}
    for foot in feet:
        calculators[foot] = StridesAndStances()
        results[foot] = np.full((data_rows_count,), '', dtype='S10')
    for row in range(1, data_rows_count):
        # print('---------- ROW: ', row)
        for foot in feet:
            # calculate the euclidean distance between last coord and current coord of foot
            xdiff = data.loc[row][scorer, f"{foot}", 'x'] - data.loc[row-1][scorer, f"{foot}", 'x']
            ydiff = data.loc[row][scorer, f"{foot}", 'y'] - data.loc[row-1][scorer, f"{foot}", 'y']
            distance = np.sqrt(xdiff**2 + ydiff**2)
            # get the current phase of the step for every foot, calling the respective class instance function
            results[foot][row] = calculators[foot].determine_current_phase(distance, distance_limit)

    # copy second row into first row of each array
    for foot in feet:
        results[foot][0] = results[foot][1]
    # print final counters
    for foot in feet:
        print(foot, ": ", calculators[foot])

    for foot in results:
        print('calculating stride lengths')
        print(type(results[foot][0]))
        df = pd.DataFrame(results[foot], columns=[foot])
        print(df, df.dtypes)
        df['phase-length'] = df[foot]
        print(foot, df.groupby([foot]).count())

    # rename dictionary keys of results
    results = {'stepphase_'+key: value for (key, value) in results.items()}
    if plotting:
        plot_footfall_pattern(results, data_rows_count)

    return results


class StridesAndStances:
    def __init__(self):
        self.stride_phase_counter = 0
        self.stance_phase_counter = 0
        self.phase = 'UNKNOWN'

    def determine_current_phase(self, distance, distance_limit):
        #print('current row difference: ',distance,self.phase,self.stride_phase_counter,self.stance_phase_counter)
        if distance >= distance_limit:    # stride
            if self.phase == 'stance' or self.phase == 'UNKNOWN':
                self.stride_phase_counter += 1
            self.phase = 'stride'
            retval = f'stride{self.stride_phase_counter:04d}'

        else:                                   # stance
            if self.phase == 'stride' or self.phase == 'UNKNOWN':
                self.stance_phase_counter += 1
            self.phase = 'stance'
            retval = f'stance{self.stride_phase_counter:04d}'
        return retval

    def __str__(self):
        return f"strides: {self.stride_phase_counter}, stances: {self.stance_phase_counter}"


def plot_footfall_pattern(results, data_rows_count):
    import pandas as pd
    import numpy as np

    df_plot = pd.DataFrame(columns = results.keys(), index=range(data_rows_count))
    print("number of columns: ", len(df_plot.columns))
    print("generate df: ", df_plot)
    # filter here and only fill in strides as numbers
    for i, key in enumerate(results):
        df_plot[key] = [i+1 if s.startswith(b'stride') else np.NaN for s in results[key]]

    df_plot.plot(linewidth=10)






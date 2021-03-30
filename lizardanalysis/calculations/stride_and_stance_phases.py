def stride_and_stance_phases(**kwargs):
    """
    This calc function determines stance and stride phases by calling the responsible class.
    A list of feet has to be defined to be looped through, this can be any number, but the labels have to appear in the
    list of labels in the config file. A distance limit can be either passed in the config file, or the default value
    of 5.0px will be used. An additional option allows to plot footfall patterns, which can be a good way for
    visualization ot even just control if phases make sense.
    return: results = dictionary of result dataframe columnname "stepphase_foot" (keys) and the respective array with
    the phases and counters for every frame (values)
    """
    import math
    import os.path
    import numpy as np
    import pandas as pd
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions
    from lizardanalysis.utils import animal_settings

    # define necessary **kwargs:
    data = kwargs.get('data')
    data_rows_count = kwargs.get('data_rows_count')
    config = kwargs.get('config')
    filename = kwargs.get('filename')
    animal = kwargs.get('animal')

    # set a distance_limit a foot has to move in px to be viewed as stride (can be changed in config, default is 5.0)
    config_file = Path(config).resolve()
    # print("config path resolved: ", config_file)
    cfg = auxiliaryfunctions.read_config(config_file)
    distance_limit = cfg['distance_limit']
    if distance_limit is None:
        distance_limit = 5.0

    # TODO: include likelihood in this

    scorer = data.columns[1][0]
    feet = animal_settings.get_list_of_feet(animal)

    # TODO: Function in utils giving back results path folder from config resolve
    plotting_footfall_patterns = False
    # create file path for foot fall pattern diagrams
    plotting_footfall_folder = os.path.join(str(config_file).rsplit(os.path.sep, 1)[0], "analysis-results", "footfall-pattern-diagrams")
    # print("plotting_footfall_folder: ", plotting_footfall_folder)

########################################################################################################################

    # one class instance and one result array for every foot, because every foot needs own counter
    calculators = {}
    results = {}
    for foot in feet:
        calculators[foot] = StridesAndStances()
        # "S10" = string of 10 characters: stance/stride + counter 000n
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

    # copy second row into first row of each array, because otherwise first row has no value
    for foot in feet:
        results[foot][0] = results[foot][1]
    # print final counters
    # for foot in feet:
        # print(foot, ": ", calculators[foot])

    for foot in results:
        df = pd.DataFrame(results[foot], columns=[foot])
        df['phase-length'] = df[foot]
        #print(foot, df.groupby([foot]).count())

    # rename dictionary keys of results
    results = {'stepphase_'+key: value for (key, value) in results.items()}
    #print("results: ", results)

    if plotting_footfall_patterns:
        """ plots a foot fall pattern diagram for every DLC result csv file/every lizard run """
        plot_footfall_pattern(results, data_rows_count, filename, plotting_footfall_folder)

    return results


class StridesAndStances:
    """
    class to detect stride and stance phases for any number of feet. A distance limit in px is passed as an argument to
    determine the critical cut-off limit for a frame to be seen as stance.
    Distance is the euclidean distance between two frames for the current foot this class is called for.
    """
    def __init__(self):
        self.stride_phase_counter = 0
        self.stance_phase_counter = 0
        self.phase = 'UNKNOWN'

    def determine_current_phase(self, distance, distance_limit):
        # print('current row difference: ',distance,self.phase,self.stride_phase_counter,self.stance_phase_counter)
        if distance >= distance_limit:          # stride
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


def plot_footfall_pattern(results, data_rows_count, filename, plotting_footfall_folder):
    """
    takes the result dataframe and creates a new dataframe for plotting. Every foot gets assigned an individual number.
    The dataframe is then filtered for strings containing "stride", the strides get replaced by the respective number,
    while all stances will be NaN.
    In the plot strides are therefore displayed as bars and stances are empty.
    """
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    import os
    import errno

    df_plot = pd.DataFrame(columns = results.keys(), index=range(data_rows_count))
    # filter here and only fill in stances as numbers => stances bars, strides white
    for i, key in enumerate(results):
        df_plot[key] = [i+1 if s.startswith(b'stance') else np.NaN for s in results[key]]

    key_list = [key for key in df_plot.columns]

    colors = False

    if colors:
        cmap = plt.cm.coolwarm
        legend_elements = [Line2D([0], [0], color=cmap(0.), lw=4, label=key_list[0]),
                    Line2D([0], [0], color=cmap(.33), lw=4, label=key_list[1]),
                    Line2D([0], [0], color=cmap(.66), lw=4, label=key_list[2]),
                    Line2D([0], [0], color=cmap(1.), lw=4, label=key_list[3]),
                    Line2D([0], [0], color='black', lw=4, label='stance phases'),
                    Line2D([0], [0], color='white', lw=4, label='stride phases')]
        fig, ax = plt.subplots()
        df_plot.plot(linewidth=10, color=cmap(np.linspace(0, 1, 5)), ax=ax)
        ax.legend(handles=legend_elements)
    else:
        legend_elements = [Line2D([0], [0], color='white', lw=1, label='1 = FL  |  2 = FR  |  3 = HR  |  4 = HL'),
                           Line2D([0], [0], color='black', lw=4, label='stance phases'),
                           Line2D([0], [0], color='white', lw=4, label='stride phases')]
        fig, ax = plt.subplots()
        df_plot.plot(linewidth=10, color='black', ax=ax)
        ax.legend(handles=legend_elements)


    # saves footfall pattern diagrams as pdf in defined result folder. If folder is not extant yet, it will be created
    try:
        os.makedirs(plotting_footfall_folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    plt.savefig(os.path.join(plotting_footfall_folder, "{}.pdf".format(filename)))
    plt.clf()
    plt.close()


def convert_b_string(b_string):
    """converts bite string to normal string"""
    if "stride" in b_string:
        string = "stride" + b_string.rsplit("g", 1)[0]
    elif "stance" in b_string:
        string = "stance" + b_string.rsplit("e", 1)[0]
    return string






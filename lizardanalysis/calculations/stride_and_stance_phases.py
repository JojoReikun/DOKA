def stride_and_stance_phases(data, clicked, data_rows_count, config):
    import math
    import numpy as np
    import pandas as pd

    print("FUNCTION Stride and Stance Phases")
    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]

    # one class instance and one result array for every foot, because every foot needs own counter
    calculators = {}
    results = {}
    for foot in feet:
        calculators[foot] = StridesAndStances()
        results[foot] = np.full((data_rows_count,), '', dtype='S10')
    for row in range(1, data_rows_count):
        # print('---------- ROW: ', row)
        for foot in feet:
            # print('FOOT: ', foot)
            xdiff = data.loc[row][scorer, f"{foot}", 'x'] - data.loc[row-1][scorer, f"{foot}", 'x']
            ydiff = data.loc[row][scorer, f"{foot}", 'y'] - data.loc[row-1][scorer, f"{foot}", 'y']
            distance = np.sqrt(xdiff**2 + ydiff**2)
            #print('last row and curent row x values: ', last_row, current_row)
            results[foot][row] = calculators[foot].determine_current_phase(distance)

    # copy second row into first row of each array
    for foot in feet:
        results[foot][0] = results[foot][1]
    # print final counters
    for foot in feet:
        print(foot, ": ", calculators[foot])
    # ToDo: calculate stride and stance lengths
    for foot in results:
        df = pd.DataFrame(results[foot], columns=[foot])
        df['dummy'] = df[foot]
        print(foot, df.groupby([foot]).count())

    # rename dictionary keys of results
    results = {'stepphase_'+key: value for (key, value) in results.items()}

    return results


class StridesAndStances:
    def __init__(self):
        self.stride_phase_counter = 0
        self.stance_phase_counter = 0
        self.phase = 'UNKNOWN'
        #self.stride_phase_start = True
        #self.stance_phase_start = True

    def determine_current_phase(self, distance):
        # print('current row difference: ',abs(current_row - last_row),self.phase,self.stride_phase_counter,self.stance_phase_counter)
        if distance >= 3:    # stride
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

    #TODO:
    # class switchClassInstance():
    #     """
    #     function to switch cases and call respective instance of class for current foot
    #     :return: function call ...
    #     """
    #     def switchInstance(self, foot):
    #         switcher = {
    #             'FR': calc_FR.determine_current_phase(last_row, current_row),
    #             'FL': calc_FL.determine_current_phase(last_row, current_row),
    #             'HR': calc_HR.determine_current_phase(last_row, current_row),
    #             'HL': calc_HL.determine_current_phase(last_row, current_row)
    #     }
    #     return 0

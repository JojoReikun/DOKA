def stride_and_stance_phases(data, clicked, data_rows_count, config):
    import math
    import numpy as np

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
        print('---------- ROW: ', row)
        for foot in feet:
            print('FOOT: ', foot)
            if row == 1:
                last_row = data.loc[0][scorer, "{}".format(foot), 'x']
            current_row = data.loc[row][scorer, "{}".format(foot), 'x']
            #print('last row and curent row x values: ', last_row, current_row)
            results[foot][row] = calculators[foot].determine_current_phase(last_row, current_row)

        last_row = current_row

    # print final counters
    for foot in feet:
        print(foot, ": ", calculators[foot])
    # rename dictionary keys of results
    results = {key:value for (key, value) in results.items()}
    # ToDo: calculate stride and stance lengths

    return results


class StridesAndStances:
    def __init__(self):
        self.stride_phase_counter = 0
        self.stance_phase_counter = 0
        self.phase = 'UNKNOWN'
        #self.stride_phase_start = True
        #self.stance_phase_start = True

    def determine_current_phase(self, last_row, current_row):
        print('current row difference: ',abs(current_row - last_row),self.phase,self.stride_phase_counter,self.stance_phase_counter)
        if abs(current_row - last_row) >= 3:    # stride
            if self.phase == 'stance':
                self.stride_phase_counter += 1
            self.phase = 'stride'
            retval = f'stride{self.stride_phase_counter:04d}'
        else:                                   # stance
            if self.phase == 'stride':
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

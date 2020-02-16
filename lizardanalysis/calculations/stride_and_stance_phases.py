def stride_and_stance_phases(data, clicked, data_rows_count, config):
    import math
    import numpy as np

    scorer = data.columns[1][0]
    feet = ["FR", "FL", "HR", "HL"]

    # 1 class instance for every foot, because every foot needs own counter
    calc_FR = StridesAndStances()  # reinitialize class for every new foot to reset counters
    calc_FL = StridesAndStances()  # reinitialize class for every new foot to reset counters
    calc_HR = StridesAndStances()  # reinitialize class for every new foot to reset counters
    calc_HL = StridesAndStances()  # reinitialize class for every new foot to reset counters

    for row in range(1, data_rows_count):
        for foot in feet:
            if row == 1:
                last_row = data[0][scorer, "{}".format(foot), 'x']
            current_row = data[row][scorer, "{}".format(foot), 'x']
            print('last row and curent row x values: ', last_row, current_row)

            #TODO: add switch case function call depending on foot
            class_instance = "calc_" + "{}".format(foot)
            eval_ = eval(class_instance)
            print('eval_: ', eval_)
            eval_.determine_current_phase(last_row, current_row)

        last_row = current_row

    stride_and_stance_phases_list = 0
    return {__name__.rsplit('.', 1)[1]: stride_and_stance_phases_list}


class StridesAndStances:
    def __init__(self):
        self.stride_phase_counter = 0
        self.stance_phase_counter = 0
        self.stride_phase_start = True
        self.stance_phase_start = True

    def determine_current_phase(self, last_row, current_row):
        if abs(current_row - last_row) >= 3:    # stride
            self.stance_phase_start = True
            if self.stride_phase_counter == 0 & self.stance_phase_counter == 0:     # start condition
                retval = 'stride' + str(self.stride_phase_counter)
            else:
                if self.stride_phase_start:
                    self.stance_phase_counter += 1      # only do 1nce in phase
                    retval = 'stride' + str(self.stride_phase_counter)
                    self.stride_phase_start = False
                else:
                    retval = 'stride' + str(self.stride_phase_counter)

        else:                                   # stance
            self.stride_phase_start = True
            if self.stride_phase_counter == 0 & self.stance_phase_counter == 0:     # start condition
                retval = 'stance' + str(self.stance_phase_counter)
            else:
                if self.stance_phase_start:
                    self.stride_phase_counter += 1      # only do 1nce in phase
                    retval = 'stance' + str(self.stance_phase_counter)
                    self.stance_phase_start = False
                else:
                    retval = 'stance' + str(self.stance_phase_counter)
        return retval

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

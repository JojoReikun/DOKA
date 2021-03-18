from lizardanalysis.utils.auxiliaryfunctions import UserFunc

def set_animal(animal):
    """
    define the calculations and the labels required labels for these in a dictionary for each available animal.
    When new calculations are added, these need to be included in these dictionaries to be found by the program.
    :param animal: string of the animal species selected for analysis. Get from GUI when clicking animal button.
    :return:
    """
    # list of all calculations and their requirements of labels as implemented in the program
    if animal == "lizard":
        dict = {'direction_of_climbing': ['nose'],
                'body_axis_deflection_angle': ['shoulder', 'hip'],
                'footfall_by_switches': ['fl', 'fr', 'hl', 'hr', 'shoulder', 'hip'],
                'lizards_feet_width_and_height': ['fl', 'fr', 'hl', 'hr']
                #'climbing_speed_framewise': ['nose'],
                # 'stride_and_stance_phases': ['fl', 'fr', 'hl', 'hr'],
                #'step_length': ['fl', 'fr', 'hl', 'hr'],
                # 'froude_numbers': ['fl', 'fr', 'hl', 'hr', 'nose', 'hip', 'shoulder_fl', 'fl_knee'],
                # 'stride_length': ['fl', 'fr', 'hl', 'hr', 'shoulder', 'hip'],
                #'limb_kinematics': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                #                    'hr_knee',
                #                    'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                #'wrist_angles': ['shoulder', 'hip', 'fr_knee', 'fr_ti', 'fr_to', 'fl_knee', 'fl_ti', 'fl_to',
                #                 'shoulder_fl', 'hr_knee', 'hr_ti', 'hr_to', 'hl_knee', 'hl_ti', 'hl_to'],
                #'limb_rom': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                #             'hr_knee', 'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                #'spine_rom': ['shoulder', 'hip', 'spine'],
                #'center_limb_rom_angle': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                #                          'hr_knee', 'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                #'hip_and_shoulder_angles': ['shoulder', 'hip', 'fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl',
                #                            'hr_knee',
                #                            'shoulder_hr', 'hl_knee', 'shoulder_hl'],
                #'knee_and_elbow_angles': ['fr_knee', 'shoulder_fr', 'fl_knee', 'shoulder_fl', 'hr_knee',
                #                           'shoulder_hr', 'hl_knee', 'shoulder_hl', 'fl', 'fr', 'hl', 'hr'],
                #'toe_angles': ['fl', 'fr', 'hr', 'hl', 'fl_ti', 'fl_ti1', 'fl_to1', 'fl_to',
                #               'fr_ti', 'fr_ti1', 'fr_to1', 'fr_to',
                #               'hr_ti', 'hr_ti1', 'hr_to1', 'hr_to',
                #               'hl_ti', 'hl_ti1', 'hl_to1', 'hl_to'],
                #'tail_biomech_angles': ['shoulder', 'spine', 'hip', 'tail_middle', 'tail_tip', 'spine_a', 'spine_c', 'tail_a', 'tail_c'],
                #'point_amplitudes_to_bA': ['shoulder', 'spine', 'hip', 'tail_middle', 'tail_tip', 'spine_a', 'spine_c', 'tail_a', 'tail_c'],
                # 'tail_kinematics': ['tail_a', 'tail_middle', 'hip', 'shoulder']
            }

    elif animal == "spider":
        dict = {'direction_of_running': ['head'],
                'footfall_by_switches_spider': ['l1', 'l2', 'l3', 'l4', 'r1', 'r2', 'r3', 'r4'],
                'extension_or_flexion_dist': ['l1', 'l2', 'l3', 'l4', 'r1', 'r2', 'r3', 'r4',
                                              'lb1', 'lb2', 'lb3', 'lb4', 'rb1', 'rb2', 'rb3', 'rb4'],
                'extension_or_flexion_phase': ['l1', 'l2', 'l3', 'l4', 'r1', 'r2', 'r3', 'r4',
                                              'lb1', 'lb2', 'lb3', 'lb4', 'rb1', 'rb2', 'rb3', 'rb4'],
                #'leg_speeds': ['l1', 'l2', 'l3', 'l4', 'r1', 'r2', 'r3', 'r4'],
                'body_speed': ['body'],
                'leg_segments_dist': ['l1', 'l2', 'l3', 'l4', 'r1', 'r2', 'r3', 'r4',
                                      'lb1', 'lb2', 'lb3', 'lb4', 'rb1', 'rb2', 'rb3', 'rb4',
                                      'lm1', 'lm2', 'lm3', 'lm4', 'rm1', 'rm2', 'rm3', 'rm4']}

    elif animal == "stick":
        dict = {
            'alpha_est_angles': ['l1', 'l2', 'l3', 'r1', 'r2', 'r3', 'lb1', 'lb2', 'lb3', 'rb1', 'rb2', 'rb3', 'head',
                                 'abdomen']}

    else:
        dict = {}
        print("no animal has been selected.")

    calculations = dict

    return calculations


def get_list_of_feet(animal):
    if animal == "lizard":
        feet = ["FL", "FR", "HR", "HL"]
    elif animal == "spider":
        feet = ['L1', 'L2', 'L3', 'L4', 'R1', 'R2', 'R3', 'R4']
    elif animal == "stick":
        feet = ['l1', 'l2', 'l3', 'r1', 'r2', 'r3']
    else:
        feet = []
        print("no animal has been selected.")
    return feet

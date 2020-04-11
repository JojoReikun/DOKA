def toe_angles(**kwargs):
    import os
    from pathlib import Path
    from lizardanalysis.utils import auxiliaryfunctions

    print("TOE ANGLE CALCULATION")

    data = kwargs.get("data")
    config = kwargs.get("config")

    config_file = Path(config).resolve()
    cfg = auxiliaryfunctions.read_config(config_file)
    print(cfg['labels'])

    feet = ["FL", "FR", "HR", "HL"]

    return 0


class ToeAngleCalculation:
    """
    class to calculate toe angles. Looks for all available toe angles, because it can be either 4 or 5 for lizards.
    """
    def __init__(self):
        self.toe_labels_available = {}

    def detect_toe_angle_labels(self, cfg, feet):
        """
        determines for very foot how many and which toe labels are available that follow the pattern: foot_toe
        :return: dictionary with the feet as keys and the respective toe labels as values
        """
        for foot in feet:
            toe_labels = [label for label in cfg['labels'] if "{foot}_t".format(foot) in label]
            print(toe_labels)
            self.toe_angles_available['{}'.format(foot)] = toe_labels
        print(self.toe_angles_available)
        return

    def calculate_toe_angles(self, toe_angles_available):
        """
        calculated the toe angles foot wise and toe pair wise
        :param toe_angles_available:
        :return:
        """
        return

    def __str__(self):
        return f"available are {len(self.toe_angles)} toe labels: {self.toe_angles}"
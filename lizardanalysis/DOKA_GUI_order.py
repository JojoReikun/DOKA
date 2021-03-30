"""
Locations of required executables and how to use them:
"""

# qt designer located at:
# FABI
# C:\Users\PlumStation\Anaconda3\envs\tf-gpu\Lib\site-packages\pyqt5_tools\Qt\bin\designer.exe
# pyuic5 to convert UI to executable python code is located at:
# C:\Users\PlumStation\Anaconda3\envs\tf-gpu\Scripts\pyuic5.exe
# -x = input     -o = output
# pyuic5.exe -x "I:\ClimbingLizardDLCAnalysis\lizardanalysis\GUI\DLC_Output_Kinematic_Analysis.ui" -o "I:\ClimbingLizardDLCAnalysis\lizardanalysis\GUI\DLC_Output_Kinematic_Analysis.py"

# JOJO
# C:\Users\JojoS\Miniconda3\Lib\site-packages\pyqt5_tools\Qt\bin\designer.exe
# pyuic5 to convert UI to executable python code is located at:
# C:\Users\JojoS\Miniconda3\Scripts\pyuic5.exe
# to convert the UI into the required .py file run:
# -x = input     -o = output
# pyuic5.exe -x "C:\Users\JojoS\Documents\phd\ClimbingRobot_XGen4\ClimbingLizardDLCAnalysis\lizardanalysis\GUI\DLC_Output_Kinematic_Analysis.ui" -o "C:\Users\JojoS\Documents\phd\ClimbingRobot_XGen4\ClimbingLizardDLCAnalysis\lizardanalysis\GUI\DLC_Output_Kinematic_Analysis.py"

"""
imports
"""

import sys
import traceback
import datetime
from time import sleep
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QPixmap, QFont
from PyQt5.QtWidgets import *
from lizardanalysis.GUI.DLC_Output_Kinematic_Analysis import Ui_MainWindow  # importing our generated file
from lizardanalysis.calculations import read_in_files
from tkinter import filedialog, Tk
import os
from pathlib import Path
from lizardanalysis.start_new_analysis import new
from lizardanalysis.utils import auxiliaryfunctions
from lizardanalysis import analyze_files, initialize
from functools import partial


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class DOKA_mainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(DOKA_mainWindow, self).__init__()

        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)

        self.threadpool = QtCore.QThreadPool()

        ###
        # variables
        ###
        self.project_name = ""
        self.project_experimenter = ""
        self.project_species = ""
        self.DLC_path = ""
        self.project_config_file = ""

        self.progress = 0
        self.updateProgress(self.progress)
        self.project_loaded = False
        self.label_buttons = []
        self.label_coords = {}
        self.labels = []
        self.button_diameter = 20

        self.animal = None
        # create list of translated labels to use arbitrary naming convention
        # format: ["name_in_DOKA","name_in_config"],[]...
        self.label_reassignment = []

        ###
        # assign button / lineEdit functions
        ###

        self.ui.Project_name_lineEdit.textChanged.connect(self.set_project_name)
        self.ui.Project_experimenter_lineEdit.textChanged.connect(self.set_project_experimenter)
        self.ui.Project_species_lineEdit.textChanged.connect(self.set_project_species)

        self.ui.Project_openDLCFiles_pushButton.pressed.connect(self.choose_DLC_folder)
        self.ui.Project_confirmNew_pushButton.pressed.connect(self.confirmNew)

        self.ui.Project_openConfig_pushButton.pressed.connect(self.choose_Existing_Project)
        self.ui.Project_confirm_pushButton.pressed.connect(self.confirmExistingProject)

        self.ui.Animal_lizard_pushButton.pressed.connect(self.select_Lizard)
        self.ui.Animal_spider_pushButton.pressed.connect(self.select_Spider)
        self.ui.Animal_ant_pushButton.pressed.connect(self.select_Ant)
        self.ui.Animal_stick_pushButton.pressed.connect(self.select_Stick)

        self.ui.letsGo_pushButton.pressed.connect(self.start_analysis)

    ###
    # (load / create) project functions

    def set_project_name(self):
        self.project_name = self.ui.Project_name_lineEdit.text()
        self.setWindowTitle("DLC Output Kinematic Analysis" + " - " + self.project_name)

    def set_project_experimenter(self):
        self.project_experimenter = self.ui.Project_experimenter_lineEdit.text()

    def set_project_species(self):
        self.project_species = self.ui.Project_species_lineEdit.text()

    def choose_DLC_folder_threaded(self, progress_callback):
        root = Tk()
        root.withdraw()  # use to hide tkinter window

        current_path = os.getcwd()

        if self.ui.Project_openDLCFiles_lineEdit.text is not None:
            current_path = self.DLC_path

        selected_path = filedialog.askdirectory(parent=root, initialdir=current_path,
                                                title='Please select a directory containing all DLC output files (.csv) for this project')
        if len(selected_path) > 0:
            self.DLC_path = selected_path
            self.log_info(self.DLC_path)

        self.ui.Project_openDLCFiles_lineEdit.setText(self.DLC_path)

        root.destroy()

    def choose_DLC_folder(self):
        worker = Worker(self.choose_DLC_folder_threaded)
        self.threadpool.start(worker)

    def choose_Existing_Project(self):
        worker = Worker(self.choose_Existing_Project_threaded)
        self.threadpool.start(worker)

    def choose_Existing_Project_threaded(self, progress_callback):
        root = Tk()
        root.withdraw()  # use to hide tkinter window

        current_path = os.getcwd()

        if self.ui.Project_openConfig_lineEdit.text is not None:
            current_path = self.ui.Project_openConfig_lineEdit.text

        config_file_path = filedialog.askopenfilename(parent=root, initialdir=current_path,
                                                      title='Please select a the config file of project to open')
        if len(config_file_path) > 0:
            self.log_info("Selected project at: " + config_file_path)
            self.ui.Project_openConfig_lineEdit.setText(config_file_path)
            self.project_config_file = config_file_path

        root.destroy()

    def confirmNew(self):
        self.project_set_up = False
        if len(self.DLC_path) > 0 and len(self.project_name) > 0 and len(self.project_experimenter) > 0 and len(
                self.project_species) > 0:
            if os.path.exists(self.DLC_path):
                worker = Worker(self.createProject_threaded)
                self.threadpool.start(worker)
            else:
                self.log_warning("Invalid path to DLC Files!")
        else:
            self.log_warning("Missing information to set up new project!")

    def createProject_threaded(self, progress_callback):
        date = datetime.datetime.today().strftime('%Y-%m-%d')

        self.project_config_file, click = new.create_new_project(project=self.project_name,
                                                                 experimenter=self.project_experimenter,
                                                                 species=self.project_species,
                                                                 file_directory=self.DLC_path)

        self.ui.Project_openConfig_lineEdit.setText(self.project_config_file)

        self.log_info("New project created: " + os.path.join(os.getcwd(), self.project_config_file))
        sleep(0.02)  # wait briefly to log info in correct order. I know, beautifully written code.
        self.log_warning("Define framerate & shutter in created config.yaml")
        sleep(0.02)  # wait briefly to log info in correct order. I know, beautifully written code.
        self.log_info("Click CONFIRM existing project to load generated config file!")

    def confirmExistingProject(self):
        if self.animal is not None:
            # read in the config file: get labels and number of files
            if len(self.project_config_file) > 0:
                current_path = os.getcwd()
                worker = Worker(self.confirmExistingProject_threaded)
                self.threadpool.start(worker)
            else:
                self.log_warning("select a config file to open an existing project first!")
        else:
            self.log_warning("Select an animal before loading your project!")

    def update_labels(self):
        # clear list before loading elements from config file
        self.ui.Labels_listWidget.clear()

        style_sheet = "border-radius :" + str(self.button_diameter / 2) + ";border: 2px solid green"
        QToolTip.setFont(QFont('SansSerif', 10))

        label_count = 0

        for label in self.labels:
            if label != "bodyparts":
                self.add_labels([number for number in list(self.label_coords.keys()) if self.label_coord(number)[0] == label] + label)
                for elem in range(len(self.label_coords)):
                    # TODO: change to dict
                    # if the label is listed as a default label, or as a reassigned label, colour the respective button green
                    if label == self.label_coords[elem][0] or [self.label_coords[elem][0],
                                                               label] in self.label_reassignment:
                        if self.label_buttons[elem].styleSheet() != style_sheet:
                            self.label_buttons[elem].setStyleSheet(style_sheet)
                            self.label_buttons[elem].setToolTip('label: <b>' + label + '</b>')
                        break
                label_count += 1

        self.ui.Labels_listWidget.sortItems(QtCore.Qt.AscendingOrder)
        self.ui.Info_numLabels_lcdNumber.display(label_count)

    def confirmExistingProject_threaded(self, progress_callback):
        config_file = Path(self.project_config_file).resolve()
        cfg = auxiliaryfunctions.read_config(config_file)

        # get labels
        self.labels = cfg['labels']

        self.update_labels()

        # labels = ";   ".join(labels)  # bring list in gui printable format
        # self.ui.Info_text_label.setText(labels)

        # get number of files
        files = cfg['file_sets'].keys()  # object type ('CommentedMapKeysView' object), does not support indexing
        filelist = []  # store filepaths as list
        for file in files:
            filelist.append(file)
        number_of_files = len(filelist)
        self.ui.Info_numFiles_lcdNumber.display(number_of_files)

        calculations, calculations_str, MODULE_PREFIX = initialize(self.animal)

        # check for label reassignment when re(loading) project configuration
        if len(self.label_reassignment) > 0:
            print(self.label_reassignment)
            for reassignment in self.label_reassignment:
                for i, label in enumerate(cfg['labels']):
                    if label == reassignment[1]:
                        cfg['labels'][i] = reassignment[0]

        print(cfg['labels'])

        try:
            calculations_checked, calculations_checked_namelist, calculations_all_list = read_in_files.check_calculation_requirements(
                cfg, calculations, calculations_str, MODULE_PREFIX)

            # clear and reload all elements of the calculations table each time a project is loaded to avoid repeated
            # display of the same entries
            if self.project_loaded:
                self.ui.calculations_tableWidget.setRowCount(0)
            self.ui.calculations_tableWidget.setColumnCount(2)

            for calc in calculations_all_list:
                row_position = self.ui.calculations_tableWidget.rowCount()
                self.ui.calculations_tableWidget.insertRow(row_position)
                self.ui.calculations_tableWidget.setItem(row_position, 0, QTableWidgetItem(str(calc)))

                if calc in calculations_checked_namelist:
                    self.ui.calculations_tableWidget.item(row_position, 0).setBackground(QColor(100, 255, 100))

            self.ui.calculations_tableWidget.setColumnWidth(0, 200)
            self.ui.calculations_tableWidget.setColumnWidth(1, 50)
            self.ui.calculations_tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Calculation"))
            self.ui.calculations_tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Run"))

        except TypeError:
            self.log_warning("No executable calculations found!")

        # TODO Insert checkbox for desired calculations

        self.project_loaded = True
        self.update_labels()

    ### INFO SECTION ###

    def log_info(self, info):
        now = datetime.datetime.now()
        # TODO add item colour (red for warnings)
        self.ui.Log_listWidget.addItem(now.strftime("%H:%M:%S") + " [INFO]  " + info)
        self.ui.Log_listWidget.sortItems(QtCore.Qt.DescendingOrder)

    def log_warning(self, info):
        now = datetime.datetime.now()
        self.ui.Log_listWidget.addItem(now.strftime("%H:%M:%S") + " [WARNING]  " + info)
        self.ui.Log_listWidget.sortItems(QtCore.Qt.DescendingOrder)

    def add_labels(self, label_text):
        self.ui.Labels_listWidget.addItem(label_text)
        self.ui.Labels_listWidget.sortItems(QtCore.Qt.DescendingOrder)

    def updateProgress(self, progress):
        self.progress = progress
        self.ui.Info_progressBar.setValue(int(self.progress))

    def start_analysis(self):
        if self.project_loaded:
            worker = Worker(self.start_analysis_threaded)
            worker.signals.progress.connect(self.updateProgress)
            # parse the animal selected through the gui to the callback:
            worker.kwargs['animal'] = self.animal
            self.threadpool.start(worker)
        else:
            self.log_warning("A config file needs to be selected first!")

    def start_analysis_threaded(self, progress_callback, animal):
        self.log_info("Analyzing project at " + self.project_config_file)
        analyze_files(self.project_config_file, self.label_reassignment, callback=progress_callback, animal=self.animal)
        progress_callback.emit(100)

    ### ANALYSIS SECTION ###

    def delete_label_buttons(self):
        for button in self.label_buttons:
            button.deleteLater()
            self.label_buttons = []

    def draw_label_buttons(self):
        # label_coords = dict of shape: {num: [label, coord_x, coord_y], ...}
        print(self.label_coords.items())
        for num, label in zip(self.label_coords.items()):
            print(num, label)
            # create button for each label
            self.label_buttons.append(QPushButton(num, self))
            self.label_buttons[-1].setGeometry(label[1] - self.button_diameter / 2, label[2] - self.button_diameter / 2,
                                               self.button_diameter, self.button_diameter)

            # setting radius and border
            style_sheet = "border-radius :" + str(self.button_diameter / 2) + ";border: 2px solid grey;color: white"
            self.label_buttons[-1].setStyleSheet(style_sheet)
            self.label_buttons[-1].setFont(QFont('Times', 8))
            # set up mouse over text
            self.label_buttons[-1].setToolTip('click to assign label from <b>config</b> file')
            # connect to label select function. Using functools.partial to pass the number of the label as an additional
            # argument to reuse the same dialog function for all label buttons
            self.label_buttons[-1].clicked.connect(partial(self.open_label_dialog, num))
            self.label_buttons[-1].show()

    def open_label_dialog(self, num):
        if self.project_loaded:
            dlg = LabelSelectDialog(self)
            dlg.setWindowTitle("select label: " + self.label_buttons[num].text())
            for label in self.labels:
                if label != "bodyparts":
                    dlg.comboBoxLabels.addItem(label)
            if dlg.exec_():
                self.log_info("assigned " + self.label_buttons[num].text() + " to " + dlg.comboBoxLabels.currentText())
                new_assignment = [self.label_buttons[num].text(), dlg.comboBoxLabels.currentText()]
                # remove previous reassignment, if present
                if len(self.label_reassignment) > 0:
                    for i, pair in enumerate(self.label_reassignment):
                        if pair[0] == new_assignment[0]:
                            del self.label_reassignment[i]
                self.label_reassignment.append(new_assignment)

                self.update_labels()

                # update existing project to display newly available calculations
                self.confirmExistingProject()
            else:
                print("Canceled assignment!")
        else:
            self.log_warning("Load project before assigning labels!")

    def select_Lizard(self):
        lizard_img = QPixmap('GUI\\lizard_shape.svg')
        self.ui.animal_QLabel.setPixmap(lizard_img)
        self.animal = "lizard"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = {
            '33': ["fl", 802, 353],
            '32': ["fl_knee", 826, 331],
            '38': ["fl_ti", 815, 386],
            '37': ["fl_ti1", 777, 397],
            '36': ["fl_tm", 758, 372],
            '34': ["fl_to", 790, 335],
            '35': ["fl_to1", 767, 345],
            '9': ["fr", 790, 205],
            '8': ["fr_knee", 828, 207],
            '14': ["fr_ti", 789, 170],
            '13': ["fr_ti1", 751, 173],
            '12': ["fr_tm", 742, 202],
            '10': ["fr_to", 781, 227],
            '11': ["fr_to1", 757, 220],
            '4': ["hip", 1027, 279],
            '25': ["hl", 1022, 365],
            '24': ["hl_knee", 992, 331],
            '26': ["hl_ti", 997, 374],
            '27': ["hl_ti1", 991, 396],
            '28': ["hl_tm", 1001, 416],
            '29': ["hl_to", 1050, 385],
            '30': ["hl_to1", 1039, 434],
            '17': ["hr", 1092, 245],
            '16': ["hr_knee", 1054, 218],
            '18': ["hr_ti", 1095, 215],
            '19': ["hr_ti1", 1113, 207],
            '20': ["hr_tm", 1134, 203],
            '21': ["hr_to", 1122, 266],
            '22': ["hr_to1", 1163, 232],
            '1': ["nose", 652, 262],
            '2': ["shoulder", 814, 271],
            '31': ["shoulder_fl", 820, 303],
            '7': ["shoulder_fr", 813, 243],
            '23': ["shoulder_hl", 1017, 301],
            '15': ["shoulder_hr", 1037, 258],
            '3': ["spine", 915, 268],
            '5': ["tail_middle", 1205, 366],
            '6': ["tail_tip", 1205, 559]}

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()

    def select_Spider(self):
        spider_img = QPixmap('GUI\\spider_shape.svg')
        self.ui.animal_QLabel.setPixmap(spider_img)
        self.animal = "spider"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = {
            27: ["l1", 744, 172],
            26: ["lm1", 848, 308],
            25: ["lb1", 936, 334],
            24: ["l2", 627, 334],
            23: ["lm2", 828, 377],
            22: ["lb2", 932, 351],
            21: ["l3", 761, 443],
            20: ["lm3", 880, 424],
            19: ["lb3", 931, 367],
            18: ["l4", 823, 558],
            17: ["lm4", 906, 448],
            16: ["lb4", 934, 381],
            6: ["r1", 1177, 173],
            5: ["rm1", 1072, 308],
            4: ["rb1", 984, 334],
            9: ["r2", 1299, 334],
            8: ["rm2", 1093, 376],
            7: ["rb2", 990, 351],
            12: ["r3", 1164, 444],
            11: ["rm3", 1042, 423],
            10: ["rb3", 991, 367],
            15: ["r4", 1100, 559],
            14: ["rm4", 1017, 450],
            13: ["rb4", 989, 382],
            1: ["head", 962, 318],
            2: ["body", 962, 390],
            3: ["tail", 961, 473]
        }

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()

    def select_Ant(self):
        spider_img = QPixmap('GUI\\ant_shape.svg')
        self.ui.animal_QLabel.setPixmap(spider_img)
        self.animal = "ant"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = {
            25: ["l1", 810, 200],
            24: ["lm1", 850, 275],
            23: ["lb1", 928, 298],
            22: ["l2", 774, 450],
            21: ["lm2", 854, 346],
            20: ["lb2", 933, 326],
            19: ["l3", 781, 554],
            18: ["lm3", 844, 423],
            17: ["lb3", 940, 346],
            10: ["r1", 1111, 200],
            9: ["rm1", 1069, 275],
            8: ["rb1", 992, 298],
            13: ["r2", 1145, 450],
            12: ["rm2", 1066, 346],
            11: ["rb2", 988, 326],
            16: ["r3", 1136, 554],
            15: ["rm3", 1074, 423],
            14: ["rb3", 980, 346],
            1: ["lmandible", 941, 168],
            2: ["rmandible", 979, 168],
            3: ["head", 959, 209],
            4: ["t1", 959, 296],
            5: ["t2", 959, 324],
            6: ["t3", 959, 340],
            7: ["abdomen", 959, 430]
        }

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()

    def select_Stick(self):
        spider_img = QPixmap('GUI\\stick_shape.svg')
        self.ui.animal_QLabel.setPixmap(spider_img)
        self.animal = "stick"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = {
            31: ["l1", 715, 464],
            10: ["rt1", 756, 272],
            29: ["lm1", 796, 451],
            28: ["lb1", 862, 383],
            27: ["l2", 886, 505],
            14: ["rt2", 909, 243],
            25: ["lm2", 929, 470],
            24: ["lb2", 956, 395],
            23: ["l3", 1206, 522],
            22: ["rt3", 1144, 237],
            21: ["lm3", 1073, 466],
            20: ["lb3", 1026, 396],
            11: ["r1", 715, 269],
            30: ["lt1", 756, 458],
            9: ["rm1", 795, 280],
            8: ["rb1", 862, 348],
            15: ["r2", 886, 227],
            26:  ["lt2", 909, 487],
            13: ["rm2", 929, 263],
            12: ["rb2", 956, 339],
            19: ["r3", 1206, 211],
            18: ["lt3", 1144, 495],
            17: ["rm3", 1072, 267],
            16: ["rb3", 1026, 337],
            1: ["lantenna", 621, 455],
            2: ["rantenna", 621, 275],
            3: ["head", 816, 366],
            4: ["t1", 873, 366],
            5: ["t2", 962, 366],
            6: ["t3", 1024, 366],
            7: ["abdomen", 1304, 366]
        }

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()


class LabelSelectDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(LabelSelectDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("select label from config file")

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.comboBoxLabels = QComboBox()

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.comboBoxLabels)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


app = QtWidgets.QApplication([])

application = DOKA_mainWindow()

application.show()

sys.exit(app.exec())

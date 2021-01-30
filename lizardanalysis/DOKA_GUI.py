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
        self.new_label_buttons = []
        self.x_coord = None
        self.y_coord = None
        self.label_coords = []
        self.labels = []
        self.labels_orig = self.labels.copy()
        self.button_diameter = 20

        self.animal = None
        self.animal_image_size = None
        self.QLabel_topcorner = (530, 180)      # the top corner of the Qlabel which contains the pixmap image
        self.new_label_counter = 0
        self.new_labels = []
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

        self.ui.animal_addNewLabels_pushButton.setCheckable(True)
        self.ui.animal_addNewLabels_pushButton.clicked.connect(self.add_new_labels)
        self.ui.animal_confirmAddedLabels_pushButton.pressed.connect(self.save_changes)

        self.ui.letsGo_pushButton.pressed.connect(self.start_analysis)

    ###
    # add enw labels functions:
    def mouseLabelPos(self, QMouseEvent):  # also tried mousePressEvent...
        # TODO: Doesn't work, crashes when button is checked with if condition uncommmented, freezes (infinity loop??) like this.
        print("mouse event")
        # if QMouseEvent.button() == QtCore.Qt.LeftButton:
        self.x_coord = QMouseEvent.pos()[0]
        self.y_coord = QMouseEvent.pos()[1]
        print("mouse click: ", QMouseEvent.pos())

        name = "name"
        self.new_labels.append([name, self.x_coord, self.y_coord])
        self.draw_new_label_button()

    def draw_new_label_button(self):
        """ draws the last added label"""
        self.new_label_buttons.append(QPushButton(str(len(self.label_buttons) + len(self.new_labels) + 1), self))
        self.new_label_buttons[-1].setGeometry(int(self.new_labels[-1][1] - self.button_diameter / 2),
                                               int(self.new_labels[-1][2] - self.button_diameter / 2),
                                               self.button_diameter, self.button_diameter)
        # setting radius and border
        style_sheet_grey = "QPushButton{border-radius :" + str(
            int(self.button_diameter / 2)) + ";border: 2px solid blue;color: white}"
        self.new_label_buttons[-1].setStyleSheet(style_sheet_grey)
        self.new_label_buttons[-1].setFont(QFont('Times', 9))
        # set up mouse over text
        self.new_label_buttons[-1].setToolTip('click to assign label from <b>config</b> file')
        # to set custom stylesheets for QToolTip
        # self.label_buttons[-1].setStyleSheet("QToolTip{background-color: black;color:white;border:black solid 1px}")
        # connect to label select function. Using functools.partial to pass the number of the label as an additional
        # argument to reuse the same dialog function for all label buttons
        self.new_label_buttons[-1].clicked.connect(partial(self.open_label_dialog, (len(self.label_buttons) + len(self.new_labels) + 1)))
        self.new_label_buttons[-1].show()

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

        style_sheet_green = "QPushButton{border-radius :" + str(
            self.button_diameter / 2) + ";border: 2px solid green;color: white }"

        style_sheet_grey = "QPushButton{border-radius :" + str(
            int(self.button_diameter / 2)) + ";border: 2px solid grey;color: white}"
        QToolTip.setFont(QFont('SansSerif', 9))

        label_count = 0

        for i, label in enumerate(self.label_coords):
            found = ""
            for elem in range(len(self.labels)):
                # if the label is listed as a default label or as a reassigned label, colour the respective button
                # we start by checking for reassigned labels
                if [label[0], self.labels_orig[elem]] in self.label_reassignment:
                    self.label_buttons[i].setStyleSheet(style_sheet_green)
                    self.label_buttons[i].setToolTip('label: <b>' + self.labels_orig[elem] + '</b>')

                    # try find matching entry (only relevant, when a label has been previously incorrectly assigned
                    try:
                        orig_button = \
                            self.label_reassignment[self.label_reassignment.index([label[0], self.labels_orig[elem]])][
                                1]
                        # find entry in label_coords
                        ind = [i[0] for i in self.label_coords].index(orig_button)
                        # set old button, corresponding to the original label, to grey/unassigned
                        self.label_buttons[ind].setStyleSheet(style_sheet_grey)
                        self.label_buttons[ind].setToolTip('click to assign label from <b>config</b> file')
                    except:
                        pass
                    found = self.labels_orig[elem]
                    break

                # if the button has not been reassigned we check the labels for an entry
                if label[0] == self.labels[elem]:
                    self.label_buttons[i].setStyleSheet(style_sheet_green)
                    self.label_buttons[i].setToolTip('label: <b>' + self.labels_orig[elem] + '</b>')

                    found = self.labels_orig[elem]
                    break

            if i < 10:
                self.add_labels("(0" + str(i) + ")" + "  " + found)
            else:
                self.add_labels("(" + str(i) + ")" + "  " + found)

            if found != "":
                label_count += 1

        self.ui.Labels_listWidget.sortItems(QtCore.Qt.AscendingOrder)
        self.ui.Info_numLabels_lcdNumber.display(label_count)

    def confirmExistingProject_threaded(self, progress_callback):
        config_file = Path(self.project_config_file).resolve()
        cfg = auxiliaryfunctions.read_config(config_file)

        # get labels
        self.labels = cfg['labels']
        self.labels_orig = self.labels.copy()

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
            print("label reassignment: ", self.label_reassignment)
            for reassignment in self.label_reassignment:
                for i, label in enumerate(cfg['labels']):
                    if label == reassignment[1]:
                        cfg['labels'][i] = reassignment[0]

        print("config labels: ", cfg['labels'])

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

    def add_new_labels_threaded(self, progress_callback):
        self.ui.animal_QLabel.mousePressEvent = self.mouseLabelPos

    ### add new labels to animal: ###
    def add_new_labels(self):
        """
        this function enables the user to click onto the lizard image and generate new labels with left click,
        move them with dragging and delete them with middle mouse button.
        New labels will be stored as lists of the format ["name", x, y], where x and y are the coordinates in the image.
        :return:
        """
        # test if project has been loaded yet
        # TODO: uncomment after testing
        # if self.animal is not None:
        #     # read in the config file: get labels and number of files
        #     if len(self.project_config_file) > 0:
        #         ## put code below here!
        #     else:
        #         self.log_warning("select a config file to open an existing project first!")
        # else:
        #     self.log_warning("Select an animal before loading your project!")


        self.ui.animal_addNewLabels_pushButton.setChecked(True)
        print("button is checked: ", self.ui.animal_addNewLabels_pushButton.isChecked())

        worker = Worker(self.add_new_labels_threaded)
        self.threadpool.start(worker)

        # TODO: get the correct size of image from self.animal_image_size in px to define coordinates correctly
        # create list with new labels with the format: ["name", x, y]

    def save_changes(self):
        self.ui.animal_addNewLabels_pushButton.setChecked(False)
        print("button is checked: ", self.ui.animal_addNewLabels_pushButton.isChecked())
        # append labels to self.label_coords
        for new_label in self.new_labels:
            self.label_coords.append(new_label)


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
        for num, label in enumerate(self.label_coords):
            # create button for each label
            self.label_buttons.append(QPushButton(str(num), self))
            self.label_buttons[-1].setGeometry(int(label[1] - self.button_diameter / 2),
                                               int(label[2] - self.button_diameter / 2),
                                               self.button_diameter, self.button_diameter)

            # setting radius and border
            style_sheet_grey = "QPushButton{border-radius :" + str(
                int(self.button_diameter / 2)) + ";border: 2px solid grey;color: white}"
            self.label_buttons[-1].setStyleSheet(style_sheet_grey)
            self.label_buttons[-1].setFont(QFont('Times', 9))
            # set up mouse over text
            self.label_buttons[-1].setToolTip('click to assign label from <b>config</b> file')
            # to set custom stylesheets for QToolTip
            # self.label_buttons[-1].setStyleSheet("QToolTip{background-color: black;color:white;border:black solid 1px}")
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
                new_assignment = [self.label_coords[num][0], dlg.comboBoxLabels.currentText()]
                # remove previous reassignment, if present
                if len(self.label_reassignment) > 0:
                    for i, pair in enumerate(self.label_reassignment):
                        if pair[0] == new_assignment[0]:
                            del self.label_reassignment[i]
                self.label_reassignment.append(new_assignment)

                # update existing project to display newly available calculations
                self.confirmExistingProject()
            else:
                print("Canceled assignment!")
        else:
            self.log_warning("Load project before assigning labels!")

    def select_Lizard(self):
        lizard_img = QPixmap('GUI\\lizard_shape.svg')
        self.ui.animal_QLabel.setPixmap(lizard_img)
        self.animal_image_size = self.ui.animal_QLabel.pixmap().size()     # get's the actual size in pixels

        print("animal_image_size: ", self.animal_image_size)
        self.animal = "lizard"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = [
            ["nose", 652, 262],
            ["shoulder", 814, 271],
            ["spine", 915, 268],
            ["hip", 1027, 279],
            ["tail_middle", 1205, 366],
            ["tail_tip", 1205, 559],
            ["shoulder_fr", 813, 243],
            ["fr_knee", 828, 207],
            ["fr", 790, 205],
            ["fr_to", 781, 227],
            ["fr_to1", 757, 220],
            ["fr_tm", 742, 202],
            ["fr_ti1", 751, 173],
            ["fr_ti", 789, 170],
            ["shoulder_hr", 1037, 258],
            ["hr_knee", 1054, 218],
            ["hr", 1092, 245],
            ["hr_ti", 1095, 215],
            ["hr_ti1", 1113, 207],
            ["hr_tm", 1134, 203],
            ["hr_to", 1122, 266],
            ["hr_to1", 1163, 232],
            ["shoulder_hl", 1017, 301],
            ["hl_knee", 992, 331],
            ["hl", 1022, 365],
            ["hl_ti", 997, 374],
            ["hl_ti1", 991, 396],
            ["hl_tm", 1001, 416],
            ["hl_to", 1050, 385],
            ["hl_to1", 1039, 434],
            ["shoulder_fl", 820, 303],
            ["fl_knee", 826, 331],
            ["fl", 802, 353],
            ["fl_to", 790, 335],
            ["fl_to1", 767, 345],
            ["fl_tm", 758, 372],
            ["fl_ti1", 777, 397],
            ["fl_ti", 815, 386]
        ]

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()

    def select_Spider(self):
        spider_img = QPixmap('GUI\\spider_shape.svg')
        self.ui.animal_QLabel.setPixmap(spider_img)
        self.animal_image_size = self.ui.animal_QLabel.pixmap().size()     # get's the actual size in pixels
        print("animal_image_size: ", self.animal_image_size)
        self.animal = "spider"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = [
            ["l1", 744, 172],
            ["lm1", 848, 308],
            ["lb1", 936, 334],
            ["l2", 627, 334],
            ["lm2", 828, 377],
            ["lb2", 932, 351],
            ["l3", 761, 443],
            ["lm3", 880, 424],
            ["lb3", 931, 367],
            ["l4", 823, 558],
            ["lm4", 906, 448],
            ["lb4", 934, 381],
            ["r1", 1177, 173],
            ["rm1", 1072, 308],
            ["rb1", 984, 334],
            ["r2", 1299, 334],
            ["rm2", 1093, 376],
            ["rb2", 990, 351],
            ["r3", 1164, 444],
            ["rm3", 1042, 423],
            ["rb3", 991, 367],
            ["r4", 1100, 559],
            ["rm4", 1017, 450],
            ["rb4", 989, 382],
            ["head", 962, 318],
            ["body", 962, 390],
            ["tail", 961, 473]
        ]

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()

    def select_Ant(self):
        spider_img = QPixmap('GUI\\ant_shape.svg')
        self.ui.animal_QLabel.setPixmap(spider_img)
        self.animal_image_size = self.ui.animal_QLabel.pixmap().size()     # get's the actual size in pixels
        print("animal_image_size: ", self.animal_image_size)
        self.animal = "ant"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = [
            ["l1", 810, 200],
            ["lm1", 850, 275],
            ["lb1", 928, 298],
            ["l2", 774, 450],
            ["lm2", 854, 346],
            ["lb2", 933, 326],
            ["l3", 781, 554],
            ["lm3", 844, 423],
            ["lb3", 940, 346],
            ["r1", 1111, 200],
            ["rm1", 1069, 275],
            ["rb1", 992, 298],
            ["r2", 1145, 450],
            ["rm2", 1066, 346],
            ["rb2", 988, 326],
            ["r3", 1136, 554],
            ["rm3", 1074, 423],
            ["rb3", 980, 346],
            ["lmandible", 941, 168],
            ["rmandible", 979, 168],
            ["head", 959, 209],
            ["t1", 959, 296],
            ["t2", 959, 324],
            ["t3", 959, 340],
            ["abdomen", 959, 430]
        ]

        self.delete_label_buttons()

        self.draw_label_buttons()

        if self.project_loaded:
            self.update_labels()

    def select_Stick(self):
        spider_img = QPixmap('GUI\\stick_shape.svg')
        self.ui.animal_QLabel.setPixmap(spider_img)
        self.animal_image_size = self.ui.animal_QLabel.pixmap().size()     # get's the actual size in pixels
        print("animal_image_size: ", self.animal_image_size)
        self.animal = "stick"
        self.log_info("Selected animal : " + self.animal)

        self.label_coords = [
            ["l1", 715, 464],
            ["rt1", 756, 272],
            ["lm1", 796, 451],
            ["lb1", 862, 383],
            ["l2", 886, 505],
            ["rt2", 909, 243],
            ["lm2", 929, 470],
            ["lb2", 956, 395],
            ["l3", 1206, 522],
            ["rt3", 1144, 237],
            ["lm3", 1073, 466],
            ["lb3", 1026, 396],
            ["r1", 715, 269],
            ["lt1", 756, 458],
            ["rm1", 795, 280],
            ["rb1", 862, 348],
            ["r2", 886, 227],
            ["lt2", 909, 487],
            ["rm2", 929, 263],
            ["rb2", 956, 339],
            ["r3", 1206, 211],
            ["lt3", 1144, 495],
            ["rm3", 1072, 267],
            ["rb3", 1026, 337],
            ["lantenna", 621, 455],
            ["rantenna", 621, 275],
            ["head", 816, 366],
            ["t1", 873, 366],
            ["t2", 962, 366],
            ["t3", 1024, 366],
            ["abdomen", 1304, 366]
        ]

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

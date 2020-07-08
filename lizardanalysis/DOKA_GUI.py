"""
Locations of required executables and how to use them:
"""

# qt designer located at:
# C:\Users\PlumStation\Anaconda3\envs\tf-gpu\Lib\site-packages\pyqt5_tools\Qt\bin\designer.exe
# pyuic5 to convert UI to executable python code is located at:
# C:\Users\PlumStation\Anaconda3\envs\tf-gpu\Scripts\pyuic5.exe
# to convert the UI into the required .py file run:
# -x = input     -o = output
# pyuic5.exe -x "I:\ClimbingLizardDLCAnalysis\GUI\DLC_Output_Kinematic_Analysis.ui" -o "I:\ClimbingLizardDLCAnalysis\GUI\DLC_Output_Kinematic_Analysis.py"

"""
imports
"""

import sys
import traceback
import datetime
from PyQt5 import QtWidgets, QtCore
from GUI.DLC_Output_Kinematic_Analysis import Ui_MainWindow  # importing our generated file
from tkinter import filedialog, Tk
import os
from start_new_analysis import new


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

        self.updateProgress(0)

        ###
        # assign button / lineEdit functions
        ###

        self.ui.Project_name_lineEdit.textChanged.connect(self.set_project_name)
        self.ui.Project_experimenter_lineEdit.textChanged.connect(self.set_project_experimenter)
        self.ui.Project_species_lineEdit.textChanged.connect(self.set_project_species)

        self.ui.Project_openDLCFiles_pushButton.pressed.connect(self.choose_DLC_folder)
        self.ui.Project_confirmNew_pushButton.pressed.connect(self.confirmNew)

        self.ui.Project_openConfig_pushButton.pressed.connect(self.choose_Existing_Project)

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

        # dialog = QFileDialog(self)
        # dialog.setFileMode(QFileDialog.Directory)
        # dialog.setViewMode(QFileDialog.Detail)
        #
        # if dialog.exec_():
        #     print("dis is okay")
        #     self.DLC_path = dialog.directory() #returns: <PyQt5.QtCore.QDir object at 0x000002814CCBB438>
        #     #self.log_info(self.DLC_path)   #needs str not QDir
        #     print(self.DLC_path)

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

        new.create_new_project(project=self.project_name, experimenter=self.project_experimenter,
                               species=self.project_species, file_directory=self.DLC_path)

        generated_project_path = self.project_name + "-" + self.project_experimenter + "-" \
                                 + self.project_species + "-" + date
        self.log_info("New project created: " + os.path.join(os.getcwd(), generated_project_path))
        self.log_info("Define framerate & shutter in created config.yaml")

    ###

    def log_info(self, info):
        now = datetime.datetime.now()
        # TODO add item colour (red for warnings)
        self.ui.Log_listWidget.addItem(now.strftime("%H:%M:%S") + " [INFO]  " + info)
        self.ui.Log_listWidget.sortItems(QtCore.Qt.DescendingOrder)

    def log_warning(self, info):
        now = datetime.datetime.now()
        self.ui.Log_listWidget.addItem(now.strftime("%H:%M:%S") + " [WARNING]  " + info)
        self.ui.Log_listWidget.sortItems(QtCore.Qt.DescendingOrder)

    def updateProgress(self, progress):
        self.progress = progress
        self.ui.Info_progressBar.setValue(int(self.progress))


app = QtWidgets.QApplication([])

application = DOKA_mainWindow()

application.show()

sys.exit(app.exec())

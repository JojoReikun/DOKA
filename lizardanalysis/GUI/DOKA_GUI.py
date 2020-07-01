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
from PyQt5 import QtWidgets, QtGui, QtCore
from DLC_Output_Kinematic_Analysis import Ui_MainWindow  # importing our generated file


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
        self.project_name = "default"
        self.project_experimenter = "Jojo"
        self.project_species = "Atta_fabiweideri"

        self.updateProgress(0)

        ###
        # assign button / lineEdit functions
        ###

        self.ui.Project_name_lineEdit.textChanged.connect(self.set_project_name)
        self.ui.Project_experimenter_lineEdit.textChanged.connect(self.set_project_experimenter)
        self.ui.Project_species_lineEdit.textChanged.connect(self.set_project_species)

        self.ui.Project_openDLCFiles_pushButton.pressed.connect(self.choose_DLC_folder)

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
        # TODO Add folder select function
        self.log_info("THIS DOES NOT WORK YET!!")

        """
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.setViewMode(QtWidgets.QFileDialog.Detail)

        if dialog.exec_():
            print("dis is okay")
        """

    def choose_DLC_folder(self):
        worker = Worker(self.choose_DLC_folder_threaded)
        self.threadpool.start(worker)

    ###

    def log_info(self, info):
        now = datetime.datetime.now()
        self.ui.Log_listWidget.addItem("[INFO] " + now.strftime("%H:%M:%S") + "  " + info)
        self.ui.Log_listWidget.sortItems(QtCore.Qt.DescendingOrder)

    def updateProgress(self, progress):
        self.progress = progress
        self.ui.Info_progressBar.setValue(int(self.progress))


app = QtWidgets.QApplication([])

application = DOKA_mainWindow()

application.show()

sys.exit(app.exec())

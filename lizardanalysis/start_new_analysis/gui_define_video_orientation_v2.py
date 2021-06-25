import sys
import datetime
import traceback
import cgitb
import time
import os
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

from lizardanalysis.start_new_analysis.lizards_direction_of_climbing_gui import Ui_MainWindow  # importing main window of the GUI

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


class directionGUI_mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(directionGUI_mainWindow, self).__init__()
        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)

        # start thread pool
        self.threadpool = QtCore.QThreadPool()

        ###
        # add images to GUI
        ###
        self.set_pixmaps()

        ###
        # variables
        ###
        self.clicked = None
        self.selection_confirmed = False
        self.ui.QpushButton_confirm.pressed.connect(self.confirm_selection)
        self.ui.QcheckBox_option1.pressed.connect(self.update_selected)
        self.ui.QcheckBox_option2.pressed.connect(self.update_selected)
        self.ui.QcheckBox_option3.pressed.connect(self.update_selected)

    def set_pixmaps(self):
        worker = Worker(self.set_pixmaps_threaded)
        self.threadpool.start(worker)

    def set_pixmaps_threaded(self, progress_callback):
        self.ui.QLabel_option1_image.setPixmap(QtGui.QPixmap("GUI_video_config_x_up_dir_up.png"))
        self.ui.QLabel_option2_image.setPixmap(QtGui.QPixmap("GUI_video_config_x_down_dir_up.png"))

    def update_selected(self):
        worker = Worker(self.update_selected_threaded)
        self.threadpool.start(worker)

    def update_selected_threaded(self, progress_callback):
        if self.ui.QcheckBox_option1.isChecked():
            self.ui.QcheckBox_option2.setChecked(False)
            self.ui.QcheckBox_option3.setChecked(False)
            self.clicked = 1
            self.ui.lcdNumber.display(self.clicked)
        elif self.ui.QcheckBox_option2.isChecked():
            self.ui.QcheckBox_option1.setChecked(False)
            self.ui.QcheckBox_option3.setChecked(False)
            self.clicked = 2
            self.ui.lcdNumber.display(self.clicked)
        elif self.ui.QcheckBox_option3.isChecked():
            self.ui.QcheckBox_option2.setChecked(False)
            self.ui.QcheckBox_option1.setChecked(False)
            self.clicked = 3
            self.ui.lcdNumber.display(self.clicked)

    def confirm_selection(self):
        self.clicked = self.ui.lcdNumber.value()
        global clicked
        global selection_confirmed
        clicked = self.clicked
        self.selection_confirmed = True
        selection_confirmed = self.selection_confirmed



class ConfirmationChecker(QtCore.QObject):
    valueUpdated = QtCore.pyqtSignal(int)

    def checkForConfirmation(self):
        # i want to connect variable i to progress bar value
        if selection_confirmed == True & clicked != None:
            self.valueUpdated.emit(clicked)



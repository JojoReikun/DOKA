# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'I:\ClimbingLizardDLCAnalysis\lizardanalysis\GUI\DLC_Output_Kinematic_Analysis.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 800)
        MainWindow.setMinimumSize(QtCore.QSize(1400, 800))
        MainWindow.setMaximumSize(QtCore.QSize(1400, 800))
        MainWindow.setWindowTitle("DLC Output Kinematic Analysis")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Animal_Selection_Frame = QtWidgets.QFrame(self.centralwidget)
        self.Animal_Selection_Frame.setGeometry(QtCore.QRect(10, 10, 161, 761))
        self.Animal_Selection_Frame.setFrameShape(QtWidgets.QFrame.Box)
        self.Animal_Selection_Frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Animal_Selection_Frame.setLineWidth(1)
        self.Animal_Selection_Frame.setMidLineWidth(0)
        self.Animal_Selection_Frame.setObjectName("Animal_Selection_Frame")
        self.Animal_Label = QtWidgets.QLabel(self.Animal_Selection_Frame)
        self.Animal_Label.setGeometry(QtCore.QRect(10, 10, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Animal_Label.setFont(font)
        self.Animal_Label.setObjectName("Animal_Label")
        self.Animal_spider_pushButton = QtWidgets.QPushButton(self.Animal_Selection_Frame)
        self.Animal_spider_pushButton.setGeometry(QtCore.QRect(10, 100, 141, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 127))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.Animal_spider_pushButton.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Mandalore")
        font.setPointSize(20)
        self.Animal_spider_pushButton.setFont(font)
        self.Animal_spider_pushButton.setObjectName("Animal_spider_pushButton")
        self.Animal_ant_pushButton = QtWidgets.QPushButton(self.Animal_Selection_Frame)
        self.Animal_ant_pushButton.setGeometry(QtCore.QRect(10, 150, 141, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(170, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.Animal_ant_pushButton.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Mandalore")
        font.setPointSize(20)
        self.Animal_ant_pushButton.setFont(font)
        self.Animal_ant_pushButton.setObjectName("Animal_ant_pushButton")
        self.Animal_lizard_pushButton = QtWidgets.QPushButton(self.Animal_Selection_Frame)
        self.Animal_lizard_pushButton.setGeometry(QtCore.QRect(10, 50, 141, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 85, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.Animal_lizard_pushButton.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Mandalore")
        font.setPointSize(20)
        self.Animal_lizard_pushButton.setFont(font)
        self.Animal_lizard_pushButton.setObjectName("Animal_lizard_pushButton")
        self.Project_Frame = QtWidgets.QFrame(self.centralwidget)
        self.Project_Frame.setEnabled(True)
        self.Project_Frame.setGeometry(QtCore.QRect(180, 10, 1211, 131))
        self.Project_Frame.setFrameShape(QtWidgets.QFrame.Box)
        self.Project_Frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Project_Frame.setObjectName("Project_Frame")
        self.Project_existing_label = QtWidgets.QLabel(self.Project_Frame)
        self.Project_existing_label.setGeometry(QtCore.QRect(10, 10, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.Project_existing_label.setFont(font)
        self.Project_existing_label.setObjectName("Project_existing_label")
        self.Project_new_label = QtWidgets.QLabel(self.Project_Frame)
        self.Project_new_label.setGeometry(QtCore.QRect(370, 10, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.Project_new_label.setFont(font)
        self.Project_new_label.setObjectName("Project_new_label")
        self.line = QtWidgets.QFrame(self.Project_Frame)
        self.line.setGeometry(QtCore.QRect(330, 0, 41, 131))
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.Project_openConfig_label = QtWidgets.QLabel(self.Project_Frame)
        self.Project_openConfig_label.setGeometry(QtCore.QRect(10, 50, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Project_openConfig_label.setFont(font)
        self.Project_openConfig_label.setObjectName("Project_openConfig_label")
        self.Project_openConfig_lineEdit = QtWidgets.QLineEdit(self.Project_Frame)
        self.Project_openConfig_lineEdit.setGeometry(QtCore.QRect(100, 50, 131, 20))
        self.Project_openConfig_lineEdit.setObjectName("Project_openConfig_lineEdit")
        self.Project_openConfig_pushButton = QtWidgets.QPushButton(self.Project_Frame)
        self.Project_openConfig_pushButton.setGeometry(QtCore.QRect(240, 50, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.Project_openConfig_pushButton.setFont(font)
        self.Project_openConfig_pushButton.setObjectName("Project_openConfig_pushButton")
        self.Project_confirm_pushButton = QtWidgets.QPushButton(self.Project_Frame)
        self.Project_confirm_pushButton.setGeometry(QtCore.QRect(100, 80, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Project_confirm_pushButton.setFont(font)
        self.Project_confirm_pushButton.setStyleSheet("background-color: rgb(187, 255, 176)")
        self.Project_confirm_pushButton.setObjectName("Project_confirm_pushButton")
        self.Project_name_lineEdit = QtWidgets.QLineEdit(self.Project_Frame)
        self.Project_name_lineEdit.setGeometry(QtCore.QRect(970, 40, 221, 20))
        self.Project_name_lineEdit.setObjectName("Project_name_lineEdit")
        self.Project_experimenter_lineEdit = QtWidgets.QLineEdit(self.Project_Frame)
        self.Project_experimenter_lineEdit.setGeometry(QtCore.QRect(970, 70, 221, 20))
        self.Project_experimenter_lineEdit.setObjectName("Project_experimenter_lineEdit")
        self.Project_species_lineEdit = QtWidgets.QLineEdit(self.Project_Frame)
        self.Project_species_lineEdit.setGeometry(QtCore.QRect(970, 100, 221, 20))
        self.Project_species_lineEdit.setObjectName("Project_species_lineEdit")
        self.Project_name_text_label = QtWidgets.QLabel(self.Project_Frame)
        self.Project_name_text_label.setGeometry(QtCore.QRect(860, 40, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Project_name_text_label.setFont(font)
        self.Project_name_text_label.setObjectName("Project_name_text_label")
        self.Project_experimenter_text_label = QtWidgets.QLabel(self.Project_Frame)
        self.Project_experimenter_text_label.setGeometry(QtCore.QRect(860, 70, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Project_experimenter_text_label.setFont(font)
        self.Project_experimenter_text_label.setObjectName("Project_experimenter_text_label")
        self.Project_experimenter_text_label_2 = QtWidgets.QLabel(self.Project_Frame)
        self.Project_experimenter_text_label_2.setGeometry(QtCore.QRect(860, 100, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Project_experimenter_text_label_2.setFont(font)
        self.Project_experimenter_text_label_2.setObjectName("Project_experimenter_text_label_2")
        self.Project_confirmNew_pushButton = QtWidgets.QPushButton(self.Project_Frame)
        self.Project_confirmNew_pushButton.setGeometry(QtCore.QRect(550, 80, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Project_confirmNew_pushButton.setFont(font)
        self.Project_confirmNew_pushButton.setStyleSheet("background-color: rgb(187, 255, 176)")
        self.Project_confirmNew_pushButton.setObjectName("Project_confirmNew_pushButton")
        self.Project_chooseDLCFiles_text_label = QtWidgets.QLabel(self.Project_Frame)
        self.Project_chooseDLCFiles_text_label.setGeometry(QtCore.QRect(370, 50, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Project_chooseDLCFiles_text_label.setFont(font)
        self.Project_chooseDLCFiles_text_label.setObjectName("Project_chooseDLCFiles_text_label")
        self.Project_openDLCFiles_lineEdit = QtWidgets.QLineEdit(self.Project_Frame)
        self.Project_openDLCFiles_lineEdit.setGeometry(QtCore.QRect(550, 50, 131, 20))
        self.Project_openDLCFiles_lineEdit.setObjectName("Project_openDLCFiles_lineEdit")
        self.Project_openDLCFiles_pushButton = QtWidgets.QPushButton(self.Project_Frame)
        self.Project_openDLCFiles_pushButton.setGeometry(QtCore.QRect(690, 50, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.Project_openDLCFiles_pushButton.setFont(font)
        self.Project_openDLCFiles_pushButton.setObjectName("Project_openDLCFiles_pushButton")
        self.Info_Frame = QtWidgets.QFrame(self.centralwidget)
        self.Info_Frame.setGeometry(QtCore.QRect(180, 150, 351, 621))
        self.Info_Frame.setFrameShape(QtWidgets.QFrame.Box)
        self.Info_Frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Info_Frame.setObjectName("Info_Frame")
        self.Info_label = QtWidgets.QLabel(self.Info_Frame)
        self.Info_label.setGeometry(QtCore.QRect(10, 10, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.Info_label.setFont(font)
        self.Info_label.setObjectName("Info_label")
        self.Info_progressBar = QtWidgets.QProgressBar(self.Info_Frame)
        self.Info_progressBar.setGeometry(QtCore.QRect(90, 570, 241, 31))
        self.Info_progressBar.setProperty("value", 24)
        self.Info_progressBar.setObjectName("Info_progressBar")
        self.Info_progress_label = QtWidgets.QLabel(self.Info_Frame)
        self.Info_progress_label.setGeometry(QtCore.QRect(10, 570, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Info_progress_label.setFont(font)
        self.Info_progress_label.setObjectName("Info_progress_label")
        self.Log_listWidget = QtWidgets.QListWidget(self.Info_Frame)
        self.Log_listWidget.setGeometry(QtCore.QRect(10, 420, 331, 131))
        self.Log_listWidget.setObjectName("Log_listWidget")
        self.Info_log_label = QtWidgets.QLabel(self.Info_Frame)
        self.Info_log_label.setGeometry(QtCore.QRect(10, 380, 91, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.Info_log_label.setFont(font)
        self.Info_log_label.setObjectName("Info_log_label")
        self.Info_numFiles_text_label = QtWidgets.QLabel(self.Info_Frame)
        self.Info_numFiles_text_label.setGeometry(QtCore.QRect(10, 40, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Info_numFiles_text_label.setFont(font)
        self.Info_numFiles_text_label.setObjectName("Info_numFiles_text_label")
        self.Info_numFiles_lcdNumber = QtWidgets.QLCDNumber(self.Info_Frame)
        self.Info_numFiles_lcdNumber.setGeometry(QtCore.QRect(150, 42, 64, 25))
        self.Info_numFiles_lcdNumber.setObjectName("Info_numFiles_lcdNumber")
        self.line_2 = QtWidgets.QFrame(self.Info_Frame)
        self.line_2.setGeometry(QtCore.QRect(0, 100, 351, 16))
        self.line_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.Info_Frame)
        self.line_3.setGeometry(QtCore.QRect(0, 370, 351, 16))
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setObjectName("line_3")
        self.Info_numLabels_text_label = QtWidgets.QLabel(self.Info_Frame)
        self.Info_numLabels_text_label.setGeometry(QtCore.QRect(10, 70, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.Info_numLabels_text_label.setFont(font)
        self.Info_numLabels_text_label.setObjectName("Info_numLabels_text_label")
        self.Info_numLabels_lcdNumber = QtWidgets.QLCDNumber(self.Info_Frame)
        self.Info_numLabels_lcdNumber.setGeometry(QtCore.QRect(150, 72, 64, 25))
        self.Info_numLabels_lcdNumber.setObjectName("Info_numLabels_lcdNumber")
        self.Labels_listWidget = QtWidgets.QListWidget(self.Info_Frame)
        self.Labels_listWidget.setGeometry(QtCore.QRect(10, 150, 331, 221))
        self.Labels_listWidget.setObjectName("Labels_listWidget")
        self.Info_labels_label = QtWidgets.QLabel(self.Info_Frame)
        self.Info_labels_label.setGeometry(QtCore.QRect(10, 110, 91, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.Info_labels_label.setFont(font)
        self.Info_labels_label.setObjectName("Info_labels_label")
        self.Label_Assignment_Frame = QtWidgets.QFrame(self.centralwidget)
        self.Label_Assignment_Frame.setGeometry(QtCore.QRect(530, 150, 861, 431))
        self.Label_Assignment_Frame.setFrameShape(QtWidgets.QFrame.Box)
        self.Label_Assignment_Frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Label_Assignment_Frame.setObjectName("Label_Assignment_Frame")
        self.animal_QLabel = QtWidgets.QLabel(self.Label_Assignment_Frame)
        self.animal_QLabel.setGeometry(QtCore.QRect(10, 10, 841, 411))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.animal_QLabel.setFont(font)
        self.animal_QLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.animal_QLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.animal_QLabel.setObjectName("animal_QLabel")
        self.Calculations_Frame = QtWidgets.QFrame(self.centralwidget)
        self.Calculations_Frame.setGeometry(QtCore.QRect(530, 580, 861, 191))
        self.Calculations_Frame.setFrameShape(QtWidgets.QFrame.Box)
        self.Calculations_Frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Calculations_Frame.setObjectName("Calculations_Frame")
        self.letsGo_pushButton = QtWidgets.QPushButton(self.Calculations_Frame)
        self.letsGo_pushButton.setGeometry(QtCore.QRect(720, 140, 131, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(85, 255, 20))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.letsGo_pushButton.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Mandalore")
        font.setPointSize(22)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.letsGo_pushButton.setFont(font)
        self.letsGo_pushButton.setStyleSheet("background-color: rgb(85, 255, 20)")
        self.letsGo_pushButton.setObjectName("letsGo_pushButton")
        self.Calculations_label = QtWidgets.QLabel(self.Calculations_Frame)
        self.Calculations_label.setGeometry(QtCore.QRect(10, 10, 281, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.Calculations_label.setFont(font)
        self.Calculations_label.setObjectName("Calculations_label")
        self.calculations_tableWidget = QtWidgets.QTableWidget(self.Calculations_Frame)
        self.calculations_tableWidget.setGeometry(QtCore.QRect(10, 40, 701, 141))
        self.calculations_tableWidget.setObjectName("calculations_tableWidget")
        self.calculations_tableWidget.setColumnCount(0)
        self.calculations_tableWidget.setRowCount(0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.Animal_Label.setText(_translate("MainWindow", "Animal"))
        self.Animal_spider_pushButton.setText(_translate("MainWindow", "SPIDER"))
        self.Animal_ant_pushButton.setText(_translate("MainWindow", "ANT"))
        self.Animal_lizard_pushButton.setText(_translate("MainWindow", "LIZARD"))
        self.Project_existing_label.setText(_translate("MainWindow", "Open Existing Project"))
        self.Project_new_label.setText(_translate("MainWindow", "Create New Project"))
        self.Project_openConfig_label.setText(_translate("MainWindow", "Open config:"))
        self.Project_openConfig_pushButton.setText(_translate("MainWindow", "open"))
        self.Project_confirm_pushButton.setText(_translate("MainWindow", "Confirm"))
        self.Project_name_text_label.setText(_translate("MainWindow", "Project name:"))
        self.Project_experimenter_text_label.setText(_translate("MainWindow", "Experimenter:"))
        self.Project_experimenter_text_label_2.setText(_translate("MainWindow", "Species:"))
        self.Project_confirmNew_pushButton.setText(_translate("MainWindow", "Confirm"))
        self.Project_chooseDLCFiles_text_label.setText(_translate("MainWindow", "Choose DLC output files:"))
        self.Project_openDLCFiles_pushButton.setText(_translate("MainWindow", "open"))
        self.Info_label.setText(_translate("MainWindow", "Project Info"))
        self.Info_progress_label.setText(_translate("MainWindow", "Progress :"))
        self.Info_log_label.setText(_translate("MainWindow", "Log :"))
        self.Info_numFiles_text_label.setText(_translate("MainWindow", "Number of Files"))
        self.Info_numLabels_text_label.setText(_translate("MainWindow", "Number of Labels"))
        self.Info_labels_label.setText(_translate("MainWindow", "Labels :"))
        self.animal_QLabel.setText(_translate("MainWindow", "Select an animal from the right column to begin your analysis!"))
        self.letsGo_pushButton.setText(_translate("MainWindow", "Let\'s go!"))
        self.Calculations_label.setText(_translate("MainWindow", "Available Calculations:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

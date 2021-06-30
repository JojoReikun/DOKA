# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Jojo\PhD\ClimbingRobot\ClimbingLizardDLCAnalysis\start_new_analysis\lizards_direction_of_climbing_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(709, 560)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("D:\\Jojo\\PhD\\ClimbingRobot\\ClimbingLizardDLCAnalysis\\start_new_analysis\\resources/lizard_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("/*-----QWidget-----*/\n"
"QWidget\n"
"{\n"
"    background-color: #232430;\n"
"    color: #000000;\n"
"    border-color: #000000;\n"
"\n"
"}\n"
"\n"
"\n"
"/*-----QLabel-----*/\n"
"QLabel\n"
"{\n"
"    background-color: #232430;\n"
"    color: #c1c1c1;\n"
"    border-color: #000000;\n"
"\n"
"}\n"
"\n"
"\n"
"/*-----QPushButton-----*/\n"
"QPushButton\n"
"{\n"
"    background-color: #ff9c2b;\n"
"    color: #000000;\n"
"    font-weight: bold;\n"
"    border-style: solid;\n"
"    border-color: #000000;\n"
"    padding: 6px;\n"
"\n"
"}\n"
"\n"
"\n"
"QPushButton::hover\n"
"{\n"
"    background-color: #ffaf5d;\n"
"\n"
"}\n"
"\n"
"\n"
"QPushButton::pressed\n"
"{\n"
"    background-color: #dd872f;\n"
"\n"
"}\n"
"\n"
"/*-----QCheckBox-----*/\n"
"QCheckBox\n"
"{\n"
"    color: #c1c1c1;\n"
"    padding: 6px;\n"
"}\n"
"\n"
"/*-----QToolButton-----*/\n"
"QToolButton\n"
"{\n"
"    background-color: #ff9c2b;\n"
"    color: #000000;\n"
"    font-weight: bold;\n"
"    border-style: solid;\n"
"    border-color: #000000;\n"
"    padding: 6px;\n"
"\n"
"}\n"
"\n"
"\n"
"QToolButton::hover\n"
"{\n"
"    background-color: #ffaf5d;\n"
"\n"
"}\n"
"\n"
"\n"
"QToolButton::pressed\n"
"{\n"
"    background-color: #dd872f;\n"
"\n"
"}\n"
"\n"
"\n"
"/*-----QLineEdit-----*/\n"
"QLineEdit\n"
"{\n"
"    background-color: #38394e;\n"
"    color: #c1c1c1;\n"
"    border-style: solid;\n"
"    border-width: 1px;\n"
"    border-color: #4a4c68;\n"
"\n"
"}\n"
"\n"
"\n"
"/*-----QTableView-----*/\n"
"QTableView, \n"
"QHeaderView, \n"
"QTableView::item \n"
"{\n"
"    background-color: #232430;\n"
"    color: #c1c1c1;\n"
"    border: none;\n"
"\n"
"}\n"
"\n"
"\n"
"QTableView::item:selected \n"
"{ \n"
"    background-color: #41424e;\n"
"    color: #c1c1c1;\n"
"\n"
"}\n"
"\n"
"\n"
"QHeaderView::section:horizontal \n"
"{\n"
"    background-color: #232430;\n"
"    border: 1px solid #37384d;\n"
"    padding: 5px;\n"
"\n"
"}\n"
"\n"
"\n"
"QTableView::indicator{\n"
"    background-color: #1d1d28;\n"
"    border: 1px solid #37384d;\n"
"\n"
"}\n"
"\n"
"\n"
"QTableView::indicator:checked{\n"
"    image:url(\"./ressources/check.png\"); /*To replace*/\n"
"    background-color: #1d1d28;\n"
"\n"
"}\n"
"\n"
"/*-----QTabWidget-----*/\n"
"QTabWidget::pane \n"
"{ \n"
"    border: none;\n"
"\n"
"}\n"
"\n"
"\n"
"QTabWidget::tab-bar \n"
"{\n"
"    left: 5px; \n"
"\n"
"}\n"
"\n"
"\n"
"QTabBar::tab \n"
"{\n"
"    color: #c1c1c1;\n"
"    min-width: 1px;\n"
"    padding-left: 25px;\n"
"    margin-left:-22px;\n"
"    height: 28px;\n"
"    border: none;\n"
"\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:selected \n"
"{\n"
"    color: #c1c1c1;\n"
"    font-weight: bold;\n"
"    height: 28px;\n"
"\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:!first \n"
"{\n"
"    margin-left: -20px;\n"
"\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:hover \n"
"{\n"
"    color: #DDD;\n"
"\n"
"}\n"
"\n"
"\n"
"/*-----QScrollBar-----*/\n"
"QScrollBar:horizontal \n"
"{\n"
"    background-color: transparent;\n"
"    height: 8px;\n"
"    margin: 0px;\n"
"    padding: 0px;\n"
"\n"
"}\n"
"\n"
"\n"
"QScrollBar::handle:horizontal \n"
"{\n"
"    border: none;\n"
"    min-width: 100px;\n"
"    background-color: #56576c;\n"
"\n"
"}\n"
"\n"
"\n"
"QScrollBar::add-line:horizontal, \n"
"QScrollBar::sub-line:horizontal,\n"
"QScrollBar::add-page:horizontal, \n"
"QScrollBar::sub-page:horizontal \n"
"{\n"
"    width: 0px;\n"
"    background-color: transparent;\n"
"\n"
"}\n"
"\n"
"\n"
"QScrollBar:vertical \n"
"{\n"
"    background-color: transparent;\n"
"    width: 8px;\n"
"    margin: 0;\n"
"\n"
"}\n"
"\n"
"\n"
"QScrollBar::handle:vertical \n"
"{\n"
"    border: none;\n"
"    min-height: 100px;\n"
"    background-color: #56576c;\n"
"\n"
"}\n"
"\n"
"\n"
"QScrollBar::add-line:vertical, \n"
"QScrollBar::sub-line:vertical,\n"
"QScrollBar::add-page:vertical, \n"
"QScrollBar::sub-page:vertical \n"
"{\n"
"    height: 0px;\n"
"    background-color: transparent;\n"
"\n"
"}\n"
"\n"
"/*-----QLCDNumber-----*/\n"
"QLCDNumber\n"
"{\n"
"    color: #456789;    \n"
"}\n"
"")
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 691, 501))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.QLabel_guiDescription = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QLabel_guiDescription.setFont(font)
        self.QLabel_guiDescription.setAlignment(QtCore.Qt.AlignCenter)
        self.QLabel_guiDescription.setObjectName("QLabel_guiDescription")
        self.verticalLayout_4.addWidget(self.QLabel_guiDescription)
        self.line = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_4.addWidget(self.line)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(10, -1, 10, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.QLabel_option1 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QLabel_option1.sizePolicy().hasHeightForWidth())
        self.QLabel_option1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QLabel_option1.setFont(font)
        self.QLabel_option1.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QLabel_option1.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.QLabel_option1.setObjectName("QLabel_option1")
        self.verticalLayout_5.addWidget(self.QLabel_option1)
        self.QLabel_option1_description = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.QLabel_option1_description.setWordWrap(True)
        self.QLabel_option1_description.setObjectName("QLabel_option1_description")
        self.verticalLayout_5.addWidget(self.QLabel_option1_description)
        self.frame_4 = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.frame_4.setMinimumSize(QtCore.QSize(0, 150))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.QLabel_option1_image = QtWidgets.QLabel(self.frame_4)
        self.QLabel_option1_image.setGeometry(QtCore.QRect(6, 2, 191, 151))
        self.QLabel_option1_image.setAlignment(QtCore.Qt.AlignCenter)
        self.QLabel_option1_image.setObjectName("QLabel_option1_image")
        self.frame_5 = QtWidgets.QFrame(self.frame_4)
        self.frame_5.setGeometry(QtCore.QRect(190, 40, 191, 150))
        self.frame_5.setMinimumSize(QtCore.QSize(0, 150))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.label_13 = QtWidgets.QLabel(self.frame_5)
        self.label_13.setGeometry(QtCore.QRect(6, 2, 181, 151))
        self.label_13.setAlignment(QtCore.Qt.AlignCenter)
        self.label_13.setObjectName("label_13")
        self.verticalLayout_5.addWidget(self.frame_4)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.QcheckBox_option1 = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QcheckBox_option1.sizePolicy().hasHeightForWidth())
        self.QcheckBox_option1.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QcheckBox_option1.setFont(font)
        self.QcheckBox_option1.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QcheckBox_option1.setObjectName("QcheckBox_option1")
        self.verticalLayout_5.addWidget(self.QcheckBox_option1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setContentsMargins(10, -1, 10, -1)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.QLabel_option2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QLabel_option2.sizePolicy().hasHeightForWidth())
        self.QLabel_option2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QLabel_option2.setFont(font)
        self.QLabel_option2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QLabel_option2.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.QLabel_option2.setObjectName("QLabel_option2")
        self.verticalLayout_6.addWidget(self.QLabel_option2)
        self.QLabel_option2_description = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.QLabel_option2_description.setWordWrap(True)
        self.QLabel_option2_description.setObjectName("QLabel_option2_description")
        self.verticalLayout_6.addWidget(self.QLabel_option2_description)
        self.frame_6 = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.frame_6.setMinimumSize(QtCore.QSize(0, 150))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.QLabel_option2_image = QtWidgets.QLabel(self.frame_6)
        self.QLabel_option2_image.setGeometry(QtCore.QRect(6, 2, 191, 151))
        self.QLabel_option2_image.setAlignment(QtCore.Qt.AlignCenter)
        self.QLabel_option2_image.setObjectName("QLabel_option2_image")
        self.verticalLayout_6.addWidget(self.frame_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem1)
        self.QcheckBox_option2 = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QcheckBox_option2.sizePolicy().hasHeightForWidth())
        self.QcheckBox_option2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QcheckBox_option2.setFont(font)
        self.QcheckBox_option2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QcheckBox_option2.setStyleSheet("")
        self.QcheckBox_option2.setObjectName("QcheckBox_option2")
        self.verticalLayout_6.addWidget(self.QcheckBox_option2)
        self.horizontalLayout_2.addLayout(self.verticalLayout_6)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setContentsMargins(10, -1, 10, -1)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.QLabel_option3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QLabel_option3.sizePolicy().hasHeightForWidth())
        self.QLabel_option3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QLabel_option3.setFont(font)
        self.QLabel_option3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QLabel_option3.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.QLabel_option3.setObjectName("QLabel_option3")
        self.verticalLayout_7.addWidget(self.QLabel_option3)
        self.QLabel_option3_description = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.QLabel_option3_description.setWordWrap(True)
        self.QLabel_option3_description.setObjectName("QLabel_option3_description")
        self.verticalLayout_7.addWidget(self.QLabel_option3_description)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem2)
        self.QcheckBox_option3 = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.QcheckBox_option3.sizePolicy().hasHeightForWidth())
        self.QcheckBox_option3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.QcheckBox_option3.setFont(font)
        self.QcheckBox_option3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.QcheckBox_option3.setObjectName("QcheckBox_option3")
        self.verticalLayout_7.addWidget(self.QcheckBox_option3)
        self.horizontalLayout_2.addLayout(self.verticalLayout_7)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.lcdNumber = QtWidgets.QLCDNumber(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.lcdNumber.setFont(font)
        self.lcdNumber.setFrameShadow(QtWidgets.QFrame.Raised)
        self.lcdNumber.setObjectName("lcdNumber")
        self.verticalLayout_4.addWidget(self.lcdNumber)
        self.QpushButton_confirm = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.QpushButton_confirm.setObjectName("QpushButton_confirm")
        self.verticalLayout_4.addWidget(self.QpushButton_confirm)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 709, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Definition of Direction of Climbing"))
        self.QLabel_guiDescription.setText(_translate("MainWindow", "Select one of the 3 options - defines how direction of climbing will be determined"))
        self.QLabel_option1.setText(_translate("MainWindow", "Option 1:"))
        self.QLabel_option1_description.setText(_translate("MainWindow", "Uses the \"Nose\" marker of the animal to determine the direction of climbing. Moving right (increasing x coordinates) will be defined as UP"))
        self.QLabel_option1_image.setText(_translate("MainWindow", "Option1 setting image"))
        self.label_13.setText(_translate("MainWindow", "option1 setting image"))
        self.QcheckBox_option1.setText(_translate("MainWindow", "select his option"))
        self.QLabel_option2.setText(_translate("MainWindow", "Option 2:"))
        self.QLabel_option2_description.setText(_translate("MainWindow", "<html><head/><body><p>Uses the &quot;Nose&quot; marker of the animal to determine the direction of climbing. Moving left (decreasing x coordinates) will be defined as UP</p></body></html>"))
        self.QLabel_option2_image.setText(_translate("MainWindow", "Option 2 setting image"))
        self.QcheckBox_option2.setText(_translate("MainWindow", "select his option"))
        self.QLabel_option3.setText(_translate("MainWindow", "Option 3:"))
        self.QLabel_option3_description.setText(_translate("MainWindow", "<html><head/><body><p>The direction of climbing is contained in the filenames as &quot;up&quot; and &quot;down&quot; and will therefore be extracted from there. The search for these clues works case-insensitive, but needs to match the exact word.</p></body></html>"))
        self.QcheckBox_option3.setText(_translate("MainWindow", "select his option"))
        self.QpushButton_confirm.setText(_translate("MainWindow", "Confirm"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

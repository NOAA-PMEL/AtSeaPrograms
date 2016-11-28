# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ecofoci_processing_design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(489, 626)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.layoutWidget = QtGui.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(150, 460, 193, 134))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridLayout_lower = QtGui.QGridLayout(self.layoutWidget)
        self.gridLayout_lower.setObjectName(_fromUtf8("gridLayout_lower"))
        self.btlSummaryButton = QtGui.QPushButton(self.layoutWidget)
        self.btlSummaryButton.setObjectName(_fromUtf8("btlSummaryButton"))
        self.gridLayout_lower.addWidget(self.btlSummaryButton, 3, 0, 1, 1)
        self.addMetaButton = QtGui.QPushButton(self.layoutWidget)
        self.addMetaButton.setObjectName(_fromUtf8("addMetaButton"))
        self.gridLayout_lower.addWidget(self.addMetaButton, 1, 0, 1, 1)
        self.processButton = QtGui.QPushButton(self.layoutWidget)
        self.processButton.setObjectName(_fromUtf8("processButton"))
        self.gridLayout_lower.addWidget(self.processButton, 0, 0, 1, 1)
        self.exitButton = QtGui.QPushButton(self.layoutWidget)
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.gridLayout_lower.addWidget(self.exitButton, 4, 0, 1, 1)
        self.widget = QtGui.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(120, 10, 268, 433))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputButton = QtGui.QPushButton(self.widget)
        self.inputButton.setObjectName(_fromUtf8("inputButton"))
        self.verticalLayout.addWidget(self.inputButton)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.inputList = QtGui.QListWidget(self.widget)
        self.inputList.setObjectName(_fromUtf8("inputList"))
        self.verticalLayout.addWidget(self.inputList)
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.outputList = QtGui.QListWidget(self.widget)
        self.outputList.setObjectName(_fromUtf8("outputList"))
        self.verticalLayout.addWidget(self.outputList)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.btlSummaryButton.setText(_translate("MainWindow", "Generate Bottle Summary", None))
        self.addMetaButton.setText(_translate("MainWindow", "Add Cruise Meta Data", None))
        self.processButton.setText(_translate("MainWindow", "Process Files", None))
        self.exitButton.setText(_translate("MainWindow", "Exit", None))
        self.inputButton.setText(_translate("MainWindow", "Select Cruise Directory", None))
        self.label_2.setText(_translate("MainWindow", "Choose Input Directory", None))
        self.label.setText(_translate("MainWindow", "Choose Output Directory", None))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Matt/Development/projects/sword_drill/src/gui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(575, 253)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ui_mic_number = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.ui_mic_number.setObjectName("ui_mic_number")
        self.verticalLayout.addWidget(self.ui_mic_number)
        self.ui_start = QtWidgets.QPushButton(self.centralwidget)
        self.ui_start.setObjectName("ui_start")
        self.verticalLayout.addWidget(self.ui_start)
        self.ui_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(28)
        self.ui_label.setFont(font)
        self.ui_label.setTextFormat(QtCore.Qt.PlainText)
        self.ui_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui_label.setWordWrap(True)
        self.ui_label.setObjectName("ui_label")
        self.verticalLayout.addWidget(self.ui_label)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ui_start.setText(_translate("MainWindow", "Start Recording"))
        self.ui_label.setText(_translate("MainWindow", "In the box above, enter microphone number from below and click \"Start Recording\""))

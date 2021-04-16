# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(575, 253)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.ui_mic_number = QPlainTextEdit(self.centralwidget)
        self.ui_mic_number.setObjectName(u"ui_mic_number")

        self.verticalLayout.addWidget(self.ui_mic_number)

        self.ui_start = QPushButton(self.centralwidget)
        self.ui_start.setObjectName(u"ui_start")

        self.verticalLayout.addWidget(self.ui_start)

        self.ui_label = QLabel(self.centralwidget)
        self.ui_label.setObjectName(u"ui_label")
        font = QFont()
        font.setPointSize(28)
        self.ui_label.setFont(font)
        self.ui_label.setTextFormat(Qt.PlainText)
        self.ui_label.setAlignment(Qt.AlignCenter)
        self.ui_label.setWordWrap(True)

        self.verticalLayout.addWidget(self.ui_label)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.ui_start.setText(QCoreApplication.translate("MainWindow", u"Start Recording", None))
        self.ui_label.setText(QCoreApplication.translate("MainWindow", u"In the box above, enter microphone number from below and click \"Start Recording\".", None))
    # retranslateUi


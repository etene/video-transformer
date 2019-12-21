# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video-transformer.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

# type: ignore

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(407, 275)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 10, 401, 241))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(7, 0, 7, 0)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName("verticalLayout")
        self.file_select_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.file_select_button.sizePolicy().hasHeightForWidth())
        self.file_select_button.setSizePolicy(sizePolicy)
        self.file_select_button.setText("")
        self.file_select_button.setObjectName("file_select_button")
        self.verticalLayout.addWidget(self.file_select_button)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.speed_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.speed_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.speed_label.setAlignment(QtCore.Qt.AlignCenter)
        self.speed_label.setObjectName("speed_label")
        self.horizontalLayout.addWidget(self.speed_label)
        self.speed_spinbox = QtWidgets.QDoubleSpinBox(self.verticalLayoutWidget)
        self.speed_spinbox.setDecimals(2)
        self.speed_spinbox.setMinimum(0.1)
        self.speed_spinbox.setSingleStep(0.1)
        self.speed_spinbox.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.speed_spinbox.setProperty("value", 2.0)
        self.speed_spinbox.setObjectName("speed_spinbox")
        self.horizontalLayout.addWidget(self.speed_spinbox)
        self.resulting_duration = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.resulting_duration.setText("")
        self.resulting_duration.setObjectName("resulting_duration")
        self.horizontalLayout.addWidget(self.resulting_duration)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.process_button = QtWidgets.QCommandLinkButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.process_button.sizePolicy().hasHeightForWidth())
        self.process_button.setSizePolicy(sizePolicy)
        self.process_button.setText("")
        self.process_button.setCheckable(False)
        self.process_button.setDescription("")
        self.process_button.setObjectName("process_button")
        self.verticalLayout.addWidget(self.process_button)
        self.progress_bar = QtWidgets.QProgressBar(self.verticalLayoutWidget)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout.addWidget(self.progress_bar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "video transformer"))
        self.speed_label.setText(_translate("MainWindow", "Speedup:"))
        self.speed_spinbox.setPrefix(_translate("MainWindow", "x"))

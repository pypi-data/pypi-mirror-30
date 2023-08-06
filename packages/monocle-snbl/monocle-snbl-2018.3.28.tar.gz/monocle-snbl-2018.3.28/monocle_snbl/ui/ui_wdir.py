# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/satarsa/python/monocle/ui/ui_wdir.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WDir(object):
    def setupUi(self, WDir):
        WDir.setObjectName("WDir")
        WDir.resize(833, 130)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(WDir.sizePolicy().hasHeightForWidth())
        WDir.setSizePolicy(sizePolicy)
        WDir.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtWidgets.QVBoxLayout(WDir)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.editDir = QtWidgets.QLineEdit(WDir)
        self.editDir.setMinimumSize(QtCore.QSize(500, 0))
        self.editDir.setObjectName("editDir")
        self.horizontalLayout.addWidget(self.editDir)
        self.buttonDir = QtWidgets.QToolButton(WDir)
        self.buttonDir.setObjectName("buttonDir")
        self.horizontalLayout.addWidget(self.buttonDir)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(WDir)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(WDir)
        self.buttonBox.accepted.connect(WDir.accept)
        self.buttonBox.rejected.connect(WDir.reject)
        QtCore.QMetaObject.connectSlotsByName(WDir)

    def retranslateUi(self, WDir):
        _translate = QtCore.QCoreApplication.translate
        WDir.setWindowTitle(_translate("WDir", "Set dir"))
        self.buttonDir.setText(_translate("WDir", "..."))


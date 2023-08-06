#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from qtsnbl.widgets import FixedWidget
from .ui.ui_wdir import Ui_WDir


class WDir(QtWidgets.QDialog, Ui_WDir, FixedWidget):
    sigSetDir = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setUI()
        self.fixWindow()

    def setUI(self):
        self.setupUi(self)
        style = QtWidgets.QApplication.style()
        self.buttonDir.setIcon(style.standardIcon(style.SP_DirOpenIcon))

    def accept(self):
        self.sigSetDir.emit(self.editDir.text())
        super().accept()

    @QtCore.pyqtSlot()
    def on_buttonDir_clicked(self):
        self.editDir.setText(QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose directory', self.editDir.text()))

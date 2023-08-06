#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import partial
from PyQt5 import QtCore, QtWidgets
import aspic
from .mwmonocle import MWMonocle
from .flogger import Flogger
from .wdir import WDir


class Controller(QtCore.QObject):
    sigSetValue = QtCore.pyqtSignal(int, float)

    def __init__(self):
        super().__init__()
        self.createWindows()
        self.createDevices()
        self.connectSignals()

    def createWindows(self):
        self.mwmonocle = MWMonocle()
        self.wdir = WDir(self.mwmonocle)

    def start(self):
        self.loadSettings()
        self.mwmonocle.show()
        self.timer.start(100)

    def loadSettings(self):
        self.flogger.loadSettings()
        self.mwmonocle.loadSettings()

    def saveSettings(self):
        self.flogger.saveSettings()
        self.mwmonocle.saveSettings()

    def close(self):
        self.saveSettings()
        self.mwmonocle.close()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.mwmonocle.sigClose.connect(self.close)
        self.timer.timeout.connect(self.runCommand)
        self.sigSetValue.connect(self.mwmonocle.setValue)
        for key in self.sensors:
            self.sensors[key]['cmd'].sigFinished.connect(partial(self.commandFinished, key))
        self.flogger.sigFileError.connect(self.showError)
        self.mwmonocle.actionSetLogDirectory.triggered.connect(self.wdir.exec)
        self.flogger.sigDir.connect(self.wdir.editDir.setText)
        self.wdir.sigSetDir.connect(self.flogger.setDir)
        self.sigSetValue.connect(self.flogger.setSensor)

    def showError(self, msg: str):
        QtWidgets.QMessageBox.critical(self.mwmonocle, 'Error', msg)

    def createDevices(self):
        self.timer = QtCore.QTimer()
        self.con = aspic.manager.connect(('snbla2.esrf.fr', 'wagotest'))
        self.sensors = {
            0: {'txt': "wago_readch('oa_temp[0]')", 'cmd': aspic.Qommand(self.con), 'sent': False},
            1: {'txt': "wago_readch('oa_temp[1]')", 'cmd': aspic.Qommand(self.con), 'sent': False},
            2: {'txt': "wago_readch('ob_temp[1]')", 'cmd': aspic.Qommand(self.con), 'sent': False},
            3: {'txt': "wago_readch('ob_temp[0]')", 'cmd': aspic.Qommand(self.con), 'sent': False},
        }
        self.flogger = Flogger()

    def commandFinished(self, sensor, value):
        self.sensors[sensor]['sent'] = False
        try:
            value = float(value)
        except ValueError:
            return
        self.sigSetValue.emit(sensor, value)

    def runCommand(self):
        if not self.con.connected:
            return
        for sensor in self.sensors:
            if self.sensors[sensor]['sent']:
                continue
            self.sensors[sensor]['cmd'].run(self.sensors[sensor]['txt'])
            self.sensors[sensor]['sent'] = True

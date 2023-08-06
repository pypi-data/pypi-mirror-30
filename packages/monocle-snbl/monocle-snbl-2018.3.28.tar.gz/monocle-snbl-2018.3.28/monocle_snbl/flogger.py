#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from PyQt5 import QtCore


class Flogger(QtCore.QObject):
    LogFile = 'monocle.log'
    sigFileError = QtCore.pyqtSignal(str)
    sigDir = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.sensors = {}
        self.dir = ''
        self.file = None
        self.connectSignals()

    def saveSettings(self):
        _ = QtCore.QSettings().setValue
        _('Flogger/dir', self.dir)

    def loadSettings(self):
        _ = QtCore.QSettings().value
        self.dir = _('Flogger/dir', '', str)
        self.setDir(self.dir)
        self.timer.start()

    def connectSignals(self):
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.dumpSensors)

    def setSensor(self, sensor, value):
        self.sensors[sensor] = value

    def dumpSensors(self):
        if not self.file:
            return
        self.file.write(str(time.time()))
        for key in sorted(self.sensors):
            self.file.write(f'\t{self.sensors[key]:.2f}')
        self.file.write('\n')
        self.file.flush()

    def setDir(self, name):
        if not name:
            self.dir = ''
            self.file = None
            return
        self.dir = name
        try:
            f = open(os.path.join(self.dir, self.LogFile), 'a+')
        except OSError as err:
            self.sigFileError.emit(f'Could not create file in {name}: {err}')
            self.dir = ''
            self.file = None
        else:
            self.file = f
        self.sigDir.emit(self.dir)

    def __del__(self):
        if self.file:
            self.file.close()

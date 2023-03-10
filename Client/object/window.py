# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author : JLM

from object.toolbar import Toolbar
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import Qt


class MyWindow(Toolbar):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height() - 40) / 2))

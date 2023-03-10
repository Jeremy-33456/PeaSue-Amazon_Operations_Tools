# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author : JLM

from PyQt5.QtWidgets import QApplication
from object import window

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    my_window = window.MyWindow()
    my_window.show()
    sys.exit(app.exec_())

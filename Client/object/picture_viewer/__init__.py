#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from object.picture_viewer import widget_1
import requests
from object.basic import Basic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap, QImage


class PictureViewer(QMainWindow, widget_1.Ui_Picture_viewer):
    def __init__(self, list_asin, basic: Basic):
        super(PictureViewer, self).__init__()
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height() - 40) / 2))
        self.setupUi(self)
        self.index = 0
        self.basic = basic
        self.list_asin = list_asin
        self.show_data(self.list_asin[self.index])
        self.back.clicked.connect(self.back_up)
        self.forw.clicked.connect(self.forward)
        self.refresh.clicked.connect(self.refresh_info)
        self.open.clicked.connect(self.open_browser)

    def show_data(self, asin):
        try:
            temp = self.basic.get_picture_info(asin)
            try:
                img = requests.get(temp[5], timeout=10)
                if img.status_code == 200:
                    pic = QImage.fromData(img.content)
                    self.viewer.setPixmap(QPixmap.fromImage(pic))
                    self.viewer.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                else:
                    QMessageBox.information(self, '失败', '图片获取失败：图片链接不存在', QMessageBox.Yes)
                    self.viewer.clear()
            except Exception as ex:
                QMessageBox.information(self, '失败', '图片获取失败：%s' % ex, QMessageBox.Yes)
            self.label_asin.setText(temp[0])
            self.label_brand.setText(temp[1])
            self.label_rank.setText(temp[2])
            self.label_number.setText(str(temp[3]))
            self.label_rate.setText(str(temp[4]))
        except TypeError:
            QMessageBox.information(self, '失败', '请先爬取asin信息：' + asin, QMessageBox.Yes)

    def back_up(self):
        if self.index > 0:
            self.index -= 1
            self.show_data(self.list_asin[self.index])
        else:
            QMessageBox.information(self, '失败', '已是第一张', QMessageBox.Yes)

    def forward(self):
        if self.index < len(self.list_asin) - 1:
            self.index += 1
            self.show_data(self.list_asin[self.index])
        else:
            QMessageBox.information(self, '失败', '已是最后一张', QMessageBox.Yes)

    def refresh_info(self):
        self.show_data(self.list_asin[self.index])

    def open_browser(self):
        import webbrowser
        webbrowser.open("https://www.amazon.com/dp/" + self.list_asin[self.index])

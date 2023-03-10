#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from object.menu import Menu
from PyQt5.QtWidgets import QMessageBox


class Toolbar(Menu):
    def __init__(self):
        super(Toolbar, self).__init__()
        self.action_refresh.triggered.connect(self.refresh)
        self.action_switch.triggered.connect(self.switch)
        self.action_exit.triggered.connect(self.exit_count)

    def refresh(self):
        try:
            self.basic.send_message('update_connection')
            self.basic.get_basic()
            self.date_information.update(self.basic)
            self.product_information.blockSignals(True)
            self.product_information.clear()
            self.product_information.blockSignals(False)
            self.product_information.addItems(['All'] + self.basic.product_list)
            self.date_performance.update(self.basic)
            self.product_performance.blockSignals(True)
            self.product_performance.clear()
            self.product_performance.blockSignals(False)
            self.product_performance.addItems(['All'] + self.basic.product_list)
            self.ad_setting.update(self.basic)
            self.product_setting.blockSignals(True)
            self.product_setting.clear()
            self.product_setting.blockSignals(False)
            self.product_setting.addItems(self.basic.product_list)
            self.date_data.update(self.basic)
            self.ad_data.update(self.basic)
            self.product_data.blockSignals(True)
            self.product_data.clear()
            self.product_data.blockSignals(False)
            self.product_data.addItems(self.basic.product_list)
            self.category_work.blockSignals(True)
            self.category_work.clear()
            self.category_work.blockSignals(False)
            self.category_work.addItems(self.basic.type)
            QMessageBox.information(self, '成功', '刷新成功', QMessageBox.Yes)
        except Exception as ex:
            QMessageBox.information(self, '失败', '失败：%s' % ex, QMessageBox.Yes)

    def switch(self):
        self.basic.history = not self.basic.history
        self.refresh()

    @staticmethod
    def exit_count():
        exit()

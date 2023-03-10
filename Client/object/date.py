#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from object.basic import Basic
from PyQt5.QtWidgets import QComboBox
from function import function
from object import combobox


def range_choice(scope: str, list_date: list):
    today = list_date[-1]
    if scope == '所有':
        now1, now2 = 0, len(list_date) - 1
    elif scope == '本年':
        year = today[0: 4]
        now1, now2 = len(list_date) - 1, len(list_date) - 1
        for date in list_date:
            if year == date[0: 4]:
                now1 = list_date.index(date)
                break
    elif scope == '本月':
        year = today[0: 4]
        month = today[5: 7]
        now1, now2 = len(list_date) - 1, len(list_date) - 1
        for date in list_date:
            if year == date[0: 4] and month == date[5: 7]:
                now1 = list_date.index(date)
                break
    elif scope == '30天':
        if len(list_date) >= 30:
            now1 = len(list_date) - 30
        else:
            now1 = 0
        now2 = len(list_date) - 1
    elif scope == '7天':
        if len(list_date) >= 7:
            now1 = len(list_date) - 7
        else:
            now1 = 0
        now2 = len(list_date) - 1
    elif scope == '14天':
        if len(list_date) >= 14:
            now1 = len(list_date) - 14
        else:
            now1 = 0
        now2 = len(list_date) - 1
    else:
        now1, now2 = len(list_date) - 1, len(list_date) - 1
    return now1, now2


class Date:
    def __init__(self, date1: QComboBox, date2: QComboBox, scope: QComboBox, choice: QComboBox, category: str,
                 basic: Basic):
        self.category = category
        self.date1 = date1
        self.date2 = date2
        self.date1.currentIndexChanged.connect(self.range_change)
        self.date2.currentIndexChanged.connect(self.range_change)
        self.range = scope
        self.choice = choice
        self.range.addItems(['所有', '本年', '本月', '30天', '14天', '7天', '当天', '自定义'])
        self.range.currentIndexChanged.connect(lambda: self.date_change('', ''))
        self.all_date = []
        self.list_date = []
        self.basic = basic

    def refresh(self, name: str):
        try:
            if self.category == 'information':
                list_date = self.basic.date['information'][name]
            elif self.category == 'performance':
                if self.choice.currentText() == '数据':
                    list_date = self.basic.date['performance'][name]
                    list_date.sort()
                elif self.choice.currentText() == '坑位':
                    list_date = self.basic.date['crawl'][name]
                else:
                    list_date = self.basic.date['profit'][name]
                    list_date.sort()
            else:
                list_date = self.basic.date['data'][name]
                list_date.sort()
        except KeyError:
            list_date = []
        self.all_date = list_date
        date1 = self.date1.currentText()
        date2 = self.date2.currentText()
        self.date1.blockSignals(True)
        self.date2.blockSignals(True)
        combobox.reset_value_simple(self.date1, list_date)
        combobox.reset_value_simple(self.date2, list_date)
        self.date_change(date1, date2)

    def range_change(self):
        self.list_date = function.get_day(self.date1.currentText(), self.date2.currentText())
        self.range.blockSignals(True)
        self.range.setCurrentIndex(7)
        self.range.blockSignals(False)

    def date_change(self, date1: str = '', date2: str = ''):
        if self.all_date:
            self.date1.blockSignals(True)
            self.date2.blockSignals(True)
            scope = self.range.currentText()
            if scope != '自定义':
                result = range_choice(scope, self.all_date)
                self.date1.setCurrentIndex(result[0])
                self.date2.setCurrentIndex(result[1])
            else:
                if date1 == '' and date2 == '':
                    date1 = self.date1.currentText()
                    date2 = self.date2.currentText()
                combobox.set_text(self.date1, date1)
                combobox.set_text(self.date2, date2, len(self.all_date) - 1)
            self.list_date = function.get_day(self.date1.currentText(), self.date2.currentText())
        else:
            self.list_date = []
        self.date1.blockSignals(False)
        self.date2.blockSignals(False)

    def update(self, basic: Basic):
        self.basic = basic

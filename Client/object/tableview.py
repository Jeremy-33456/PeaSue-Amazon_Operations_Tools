#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import copy
import pandas
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QFont
from PyQt5.QtWidgets import QHeaderView, QTableView, QProgressBar, QFileDialog, QPushButton


class TableView:
    def __init__(self, tableview: QTableView, name: str, sort: str, power: dict, output: QPushButton = None):
        self.category = 'table'
        self.name = name + '_' + sort
        self.output = output
        if self.output is not None:
            self.output.clicked.connect(self.export)
        self.sort = sort
        self.view = tableview
        self.model = QStandardItemModel(0, 0)
        self.view.setModel(self.model)
        self.header = []
        self.data = []
        self.extra = []
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.view.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.origin_data = [[], []]
        self.row_number = 0
        self.setted = False
        self.changed = False
        self.marked = False
        self.power = power[self.name]
        self.origin_setting = {'require': [], 'point': []}
        self.model.dataChanged.connect(self.change_condition_changed)

    def change_condition_changed(self):
        self.changed = True

    def set_content(self, content: list, header: list, require: list, extra: list = None, point: list = None,
                    pb: QProgressBar = None, start: int = 0, end: int = 100):
        self.setted = True
        self.model.clear()
        self.origin_setting = {'require': require, 'point': point}
        self.extra = []
        for row in range(0, len(content)):
            for column in range(0, len(content[row])):
                item = QStandardItem(str(content[row][column]))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                if 'sum' in require:
                    if row == len(content) - 1:
                        item.setBackground(Qt.yellow)
                if point:
                    if row in point:
                        item.setBackground(Qt.green)
                self.model.setItem(row, column, item)
            if not extra:
                self.extra.append(None)
            if pb is not None:
                pb.setValue(int((row + 1) / len(content) * (end - start)) + start)
            else:
                pass
        self.model.setHorizontalHeaderLabels(header)
        self.header = header
        self.data = content
        if extra:
            self.extra = extra
        self.origin_data = [copy.deepcopy(self.data), copy.deepcopy(self.extra)]
        self.row_number = self.model.rowCount()
        self.resize_width()
        self.changed = False

    def change(self, row: int, column: int, value: str):
        item = QStandardItem(value)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.model.setItem(row, column, item)
        self.data[row][column] = value
        if 'sum' in self.origin_setting['require']:
            if row == self.row_number - 1:
                item.setBackground(Qt.yellow)
        if self.origin_setting['point']:
            if row in self.origin_setting['point']:
                item.setBackground(Qt.green)

    def value(self, row: int, column: int):
        return self.model.item(row, column).text()

    def get_content(self):
        list_all = []
        for row in range(0, self.row_number):
            temp = []
            for column in range(0, self.model.columnCount()):
                temp.append(self.value(row, column))
            list_all.append(temp)
        return list_all

    def get_extra(self):
        return self.extra

    def get_content_column(self, column: int):
        list_all = []
        for row in range(0, self.row_number):
            list_all.append(self.value(row, column))
        return list_all

    def get_content_row(self, row: int):
        list_all = []
        for column in range(0, self.model.columnCount()):
            list_all.append(self.value(row, column))
        return list_all

    def get_content_by_header(self, header: list or str, system: str = 'str'):
        list_all = []
        if type(header) == list:
            for row in range(0, self.row_number):
                temp = []
                for item in header:
                    index = self.header.index(item)
                    if system == 'int':
                        temp.append(int(self.value(row, index)))
                    elif system == 'float':
                        temp.append(float(self.value(row, index)))
                    else:
                        temp.append(self.value(row, index))
                list_all.append(temp)
        else:
            index = self.header.index(header)
            for row in range(0, self.row_number):
                if system == 'int':
                    list_all.append(int(self.value(row, index)))
                elif system == 'float':
                    list_all.append(float(self.value(row, index)))
                else:
                    list_all.append(self.value(row, index))
        return list_all
    
    def get_selected_content(self):
        text = ''
        if self.setted:
            indexes = self.view.selectedIndexes()
            dict_index = {}
            for index in indexes:
                row, column = index.row(), index.column()
                if row in dict_index.keys():
                    dict_index[row].append(column)
                else:
                    dict_index[row] = [column]
            for row, columns in dict_index.items():
                row_data = ''
                for column in columns:
                    data = self.value(row, column)
                    if row_data:
                        row_data = row_data + '\t' + data
                    else:
                        row_data = data
                if text:
                    text = text + '\n' + row_data
                else:
                    text = row_data
        return text

    def get_selected_row(self):
        list_index = []
        if self.setted:
            indexes = self.view.selectedIndexes()
            for index in indexes:
                number = index.row()
                if number not in list_index:
                    list_index.append(number)
        return list_index

    def get_selected_column(self):
        list_index = []
        if self.setted:
            indexes = self.view.selectedIndexes()
            for index in indexes:
                number = index.column()
                if number not in list_index:
                    list_index.append(number)
        return list_index

    def clear(self):
        self.model.clear()
        self.data = []
        self.extra = []
        self.row_number = 0
        if self.name == 'keyword_setting':
            self.model.setHorizontalHeaderLabels(self.header)
            try:
                self.resize_width()
            except ZeroDivisionError:
                pass
        self.setted = False
        self.changed = True

    def mark(self):
        self.origin_data = [copy.deepcopy(self.data), copy.deepcopy(self.extra)]
        self.changed = False
        self.marked = True

    def back(self):
        require = self.origin_setting['require']
        point = self.origin_setting['point']
        if self.marked:
            self.set_content(self.origin_data[0], self.header, [], extra=self.origin_data[1], point=[])
        else:
            self.set_content(self.origin_data[0], self.header, require, extra=self.origin_data[1], point=point)

    def delete(self, list_delete: list):
        list_delete.sort(reverse=True)
        for index in list_delete:
            self.model.removeRow(index)
            del self.data[index]
            del self.extra[index]
        self.row_number = self.model.rowCount()
        if self.row_number == 0:
            self.model.clear()
            self.setted = False
        else:
            self.resize_width()
        self.changed = True

    def delete_point(self):
        deleted = False
        for i in range(self.row_number - 1, -1, -1):
            color = self.model.item(i, 0).background()
            if color == Qt.green:
                self.model.removeRow(i)
                del self.data[i]
                del self.extra[i]
                deleted = True
        if deleted:
            self.row_number = self.model.rowCount()
            if self.row_number == 0:
                self.model.clear()
                self.setted = False
            else:
                self.resize_width()
            self.changed = True

    def delete_sum(self):
        index = self.row_number - 1
        color = self.model.item(index, 0).background()
        if color == Qt.yellow:
            self.model.removeRow(index)
            del self.data[index]
            del self.extra[index]
            deleted = True
        else:
            deleted = False
        if deleted:
            self.row_number = self.model.rowCount()
            if self.row_number == 0:
                self.model.clear()
                self.setted = False
            else:
                self.resize_width()
            self.changed = True

    def insert(self, list_index: list, content: list):
        list_index.sort(reverse=True)
        for i in range(0, len(list_index)):
            item = QStandardItem(content[i][0])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.model.insertRow(list_index[i], item)
            for column in range(1, len(content[i])):
                item = QStandardItem(content[i][column])
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.model.setItem(list_index[i], column, item)
            self.data.insert(list_index[i], content[i])
            self.extra.insert(list_index[i], None)
        self.row_number = self.model.rowCount()
        self.resize_width()
        self.setted = True
        self.changed = True

    def add(self, content: list):
        for row in range(0, len(content)):
            for column in range(0, len(content[row])):
                item = QStandardItem(content[row][column])
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.model.setItem(self.row_number + row, column, item)
            self.data.append(content[row])
            self.extra.append(None)
        self.row_number = self.model.rowCount()
        self.resize_width()
        self.setted = True
        self.changed = True

    def export(self):
        df = pandas.DataFrame(self.data, columns=self.header)
        file_name = QFileDialog.getSaveFileName(caption='请选择路径', filter='*.xlsx', directory='file/%s.xlsx' % self.name)
        if file_name[0]:
            df.to_excel(file_name[0], index=False)

    def resize_width(self):
        font = QFont()
        font.setFamily("楷体")
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.view.horizontalHeader().setFont(font)
        if self.name == 'chart_performance' and '关键词' in self.header:
            self.view.horizontalHeader().resizeSection(0, 220)
            for index in range(1, len(self.header)):
                self.view.horizontalHeader().resizeSection(index, 60)
        else:
            main = self.power['main']
            dict_power = self.power['dict_power']
            length = (self.view.height() - 22) // 30
            width = self.view.width() - 2
            power = 0
            if self.row_number > length:
                width -= 17
            if self.row_number > 0:
                width -= 15
            if self.row_number > 9:
                width -= 7
            if self.row_number > 99:
                width -= 7
            if self.row_number > 999:
                width -= 7
            if self.row_number > 9999:
                width -= 7
            for i in range(0, len(self.header)):
                for item in dict_power.keys():
                    if self.header[i] in item:
                        power += dict_power[item]
                        break
            eve = width / power
            sum_value = 0
            index = 0
            list_info = []
            for i in range(0, len(self.header)):
                if self.header[i] == main:
                    index = i
                for item in dict_power.keys():
                    if self.header[i] in item:
                        list_info.append(int(dict_power[item] * eve))
                        sum_value += int(dict_power[item] * eve)
                        break
            list_info[index] += width - sum_value
            for index in range(0, len(self.header)):
                self.view.horizontalHeader().resizeSection(index, list_info[index])

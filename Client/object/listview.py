#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListView
from PyQt5.QtGui import QStandardItem, QStandardItemModel


class ListView:
    def __init__(self, listview: QListView, name: str, sort: str):
        self.category = 'list'
        self.name = name + '_' + sort
        self.sort = sort
        self.view = listview
        self.model = QStandardItemModel(0, 1)
        self.view.setModel(self.model)
        self.origin_data = []
        self.row_number = 0
        self.setted = False
        self.changed = False
        self.model.dataChanged.connect(self.change_condition_changed)

    def change_condition_changed(self):
        self.changed = True

    def set_content(self, content: list):
        self.setted = True
        self.model.clear()
        self.origin_data = content
        for row in range(0, len(content)):
            item = QStandardItem(content[row])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.model.setItem(row, 0, item)
        self.row_number = self.model.rowCount()
        self.changed = False

    def change(self, row: int, value: str):
        item = QStandardItem(value)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.model.setItem(row, 0, item)

    def value(self, row):
        return self.model.item(row, 0).text()

    def get_content(self):
        list_all = []
        for row in range(0, self.row_number):
            list_all.append(self.value(row))
        return list_all

    def get_selected_content(self):
        text = ''
        if self.setted:
            indexes = self.view.selectedIndexes()
            list_index = []
            for index in indexes:
                list_index.append(index.row())
            for row in list_index:
                row_data = self.value(row)
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

    def clear(self):
        self.model.clear()
        self.setted = False
        self.row_number = 0
        self.changed = True

    def mark(self):
        self.origin_data = self.get_content()
        self.changed = False

    def back(self):
        self.set_content(self.origin_data)
        self.changed = False

    def delete(self, list_delete: list):
        if isinstance(list_delete[0], str):
            list_now = self.get_content()
            list_index = []
            for item in list_delete:
                list_index.append(list_now.index(item))
        else:
            list_index = list_delete.copy()
        list_index.sort(reverse=True)
        for index in list_index:
            self.model.removeRow(index)
        self.row_number = self.model.rowCount()
        if self.row_number == 0:
            self.setted = False
        self.changed = True

    def add(self, list_add: list):
        for row in range(0, len(list_add)):
            item = QStandardItem(list_add[row])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.model.setItem(row + self.row_number, 0, item)
        self.row_number = self.model.rowCount()
        self.setted = True
        self.changed = True

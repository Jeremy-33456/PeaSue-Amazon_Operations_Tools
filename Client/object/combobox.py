#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from PyQt5.QtWidgets import QComboBox


def reset_value(box: QComboBox, content: list):
    count1 = box.count()
    count2 = len(content)
    if count1 > 0 and count2 > 0:
        box.blockSignals(True)
        box.clear()
        box.blockSignals(False)
        box.addItems(content)
    elif count1 == 0 and count2 > 0:
        box.addItems(content)
    elif count1 > 0 and count2 == 0:
        box.clear()
    else:
        box.currentIndexChanged.emit(1)


def reset_value_simple(box: QComboBox, content: list):
    box.clear()
    box.addItems(content)


def reset_value_silent(box: QComboBox, content: list):
    box.blockSignals(True)
    box.clear()
    box.addItems(content)
    box.blockSignals(False)


def get_all_text(box: QComboBox):
    count = box.count()
    list_all = []
    for i in range(0, count):
        list_all.append(box.itemText(i))
    return list_all


def set_text(box: QComboBox, choose: str, fault: int = 0):
    list_choose = get_all_text(box)
    try:
        index = list_choose.index(choose)
    except ValueError:
        index = fault
    box.setCurrentIndex(index)


def clear(box: QComboBox):
    box.blockSignals(True)
    box.clear()
    box.blockSignals(False)
    box.currentIndexChanged.emit(1)

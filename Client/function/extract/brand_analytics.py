#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import os
import pandas
from object.basic import Basic
from function import function
from PyQt5.QtCore import pyqtSignal


def main(basic: Basic, printer: pyqtSignal, category: str, store: str):
    list_file = os.listdir('%s/Brand Analytics/%s' % (basic.path[store], category))
    list_deny = basic.deny[category]
    for deny in list_deny:
        try:
            list_deny.append(basic.plural[deny])
        except KeyError:
            pass
    for file in list_file:
        printer.emit('正在导入%s-%s' % (category, file))
        data = pandas.read_csv('%s/Brand Analytics/%s/%s' % (basic.path[store], category, file))
        chip = data.columns[4].replace('查看=[', '').replace(']', '').split('-')
        date = '%s.%s' % (chip[0], str(int((int(chip[1]) + 2) / 3)))
        data = pandas.read_csv('%s/Brand Analytics/%s/%s' % (basic.path[store], category, file), header=1)
        for i in range(0, len(data['搜索词'])):
            keyword = data['搜索词'][i]
            if len(keyword) < 60 and not function.find_one(keyword, list_deny)[0]:
                rank = int(data['搜索频率排名'][i].replace(',', ''))
                basic.update_brand_analytics(category, keyword, rank, date)
    basic.commit()


def extract_brand(basic: Basic, printer: pyqtSignal, category: str, store: str):
    try:
        main(basic, printer, category, store)
        printer.emit('成功导入品牌分析')
    except Exception as ex:
        printer.emit('导入品牌分析失败：%s' % ex)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from advertisement.data import Data
from function import function
from object import tableview


class Work(Data):
    def __init__(self):
        super(Work, self).__init__()
        self.result_work = tableview.TableView(self.table1_work, 'result', 'work', self.basic.power,
                                               output=self.output_work)
        self.data_work = tableview.TableView(self.table2_work, 'data', 'work', self.basic.power,
                                             output=self.output_work_2)
        self.frequency_work.clicked.connect(self.keyword_frequency)
        self.tear_work.clicked.connect(self.keyword_tear)
        self.analyse_work.clicked.connect(self.work_analyse)
        self.category_work.currentIndexChanged.connect(self.product_change_work)
        self.category_work.addItems(self.basic.type)

    def product_change_work(self):
        self.product_work.clear()
        category = self.category_work.currentText()
        list_temp = []
        for name in self.basic.product_list:
            if self.basic.get_category(name) == category:
                list_temp.append(name)
        if len(list_temp) > 0:
            list_temp.insert(0, 'All')
        self.product_work.addItems(list_temp)

    def work_analyse(self):
        category = self.category_work.currentText()
        name = self.product_work.currentText()
        if name in ['', 'All']:
            list_deny = []
            list_fit = []
        else:
            list_fit = self.basic.get_fit_keyword(name)
            list_deny = self.basic.get_deny_work(name)
        temp = self.basic.get_brand_analytics(category)
        if len(list_fit) > 0:
            list_temp = []
            for item in temp:
                if function.find_one(item[0], list_fit)[0]:
                    list_temp.append([item[0], item[1]])
        else:
            list_temp = temp
        list_all = []
        for item in list_temp:
            if not function.find_one(item[0], list_deny)[0]:
                list_all.append([item[0], item[1]])
        self.progressBar.setValue(10)
        self.data_work.set_content(list_all, ['关键词', '最高排名'], [], pb=self.progressBar, start=10)
        self.progressBar.setValue(0)

    def keyword_frequency(self):
        from keywords.frequency import frequency
        list_all = frequency(self.input_work.toPlainText(), self.category_work.currentText(), self.basic,
                             self.progressBar)
        header = ['关键词', '权重']
        self.result_work.set_content(list_all, header, [], pb=self.progressBar, start=50)
        self.progressBar.setValue(0)

    def keyword_tear(self):
        from keywords.tear import tear
        list_all = tear(self.input_work.toPlainText(), self.category_work.currentText(), self.basic, self.progressBar)
        header = ['词数', '关键词', '权重']
        self.result_work.set_content(list_all, header, [])
        self.progressBar.setValue(0)

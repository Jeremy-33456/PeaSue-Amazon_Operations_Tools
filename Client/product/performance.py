#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from function import function
from object import tableview, date
from PyQt5.QtWidgets import QMessageBox
from product import calculate
from product.information import Information


class Performance(Information):
    def __init__(self):
        super(Performance, self).__init__()
        self.chart_performance = tableview.TableView(self.table1_performance, 'chart', 'performance', self.basic.power,
                                                     output=self.output_peformance)
        self.date_performance = date.Date(self.date1_performance, self.date2_performance, self.range_performance,
                                          self.choice_performance, 'performance', self.basic)
        self.product_performance.currentIndexChanged.connect(lambda: self.date_performance.refresh(
            self.product_performance.currentText()))
        self.analyse_performance.clicked.connect(self.show_chart_performance)
        self.choice_performance.addItems(['数据', '坑位', '利润'])
        self.choice_performance.currentIndexChanged.connect(lambda: self.date_performance.refresh(
            self.product_performance.currentText()))
        self.product_performance.addItems(['All'] + self.basic.product_list)

    def show_chart_performance(self):
        list_date = self.date_performance.list_date
        if len(list_date) > 0:
            name = self.product_performance.currentText()
            if name == 'All':
                item, name = '产品', function.connect(self.basic.product_list, ',')
            else:
                item = '日期'
            if self.choice_performance.currentText() == '数据':
                header = [item, '销售额', '折扣', '成本', '核算', '总流量', '自然流量', '站外单', '自然单', '总出单', '总转化率',
                          'CPC占比', '广告流量', '广告单', '点击率', '广告转化', '广告花费', '广告ACOS', '排名', '评价数', '星级']
                try:
                    list_all = calculate.read_performance(name, list_date, self.basic)
                    self.chart_performance.set_content(list_all, header, ['sum'], pb=self.progressBar)
                    self.progressBar.setValue(0)
                except Exception as ex:
                    QMessageBox.information(self, '失败', '数据读取失败：%s' % ex, QMessageBox.Yes)
            elif self.choice_performance.currentText() == '坑位':
                header = ['关键词', '类别']
                for item in list_date:
                    header.append(item[5:])
                try:
                    list_all = calculate.read_crawl(name, list_date, self.basic)
                    self.chart_performance.set_content(list_all, header, [])
                except Exception as ex:
                    QMessageBox.information(self, '失败', '数据读取失败：%s' % ex, QMessageBox.Yes)
            else:
                header = [item, '数量', '销售额', '佣金', '尾程', '折扣', '退货', '调整', '广告', '仓储费', '弃置', '其他',
                          '回款', '回款率', '进货', '头程', '毛利润', '毛利率', 'ROI']
                try:
                    list_all = calculate.read_profit(name, list_date, self.basic)
                    self.chart_performance.set_content(list_all, header, ['sum'], pb=self.progressBar)
                    self.progressBar.setValue(0)
                except Exception as ex:
                    QMessageBox.information(self, '失败', '数据读取失败：%s' % ex, QMessageBox.Yes)
        else:
            QMessageBox.information(self, '失败', '无数据可用', QMessageBox.Yes)

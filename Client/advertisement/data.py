#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from PyQt5.QtWidgets import QMessageBox
from advertisement import assist
from advertisement import count
from advertisement.setting import Setting
from function import function
from object import tableview, date, combobox, advertisement


class Data(Setting):
    def __init__(self):
        super(Data, self).__init__()
        self.chart_data = tableview.TableView(self.table1_data, 'chart', 'data', self.basic.power, self.output_data)
        self.date_data = date.Date(self.date1_data, self.date2_data, self.range_data, self.choice_data, 'data',
                                   self.basic)
        self.ad_data = advertisement.AdComplex(self.campaign_data, self.group_data, self.match_data, self.traffic_data,
                                               self.bid_data, self.variation_data, self.special_data, self.basic)
        self.product_data.currentIndexChanged.connect(lambda: self.date_data.refresh(self.product_data.currentText()))
        self.product_data.currentIndexChanged.connect(lambda: self.ad_data.refresh(self.product_data.currentText()))
        self.choice_data.currentIndexChanged.connect(self.choice_hide_data)
        self.contrast_data.clicked.connect(self.contrast_advertisement)
        self.analyse_data.clicked.connect(self.show_chart_data)
        self.choice_data.addItems(['调价', '关键词'])
        self.product_data.addItems(self.basic.product_list)

    def choice_hide_data(self):
        self.choice_date_data.clear()
        if self.choice_data.currentText() == '调价':
            self.choice_date_data.addItems(['总览', '一览', '每日'])
        else:
            self.choice_date_data.addItems(['总览', '一览'])

    def contrast_advertisement(self):
        name = self.product_data.currentText()
        campaign_data = self.campaign_data.currentText()
        group_data = self.group_data.currentText()
        header = self.chart_data.header.copy()
        choice = self.choice_data.currentText()
        date_choice = self.choice_date_data.currentText()
        if date_choice == '总览' and campaign_data == 'All Ad Campaigns':
            if self.product_setting.currentText() != self.product_data.currentText():
                combobox.set_text(self.product_setting, self.product_data.currentText())
        elif choice == '调价' and date_choice in ['一览', '每日'] and campaign_data != 'All Ad Campaigns':
            if self.product_setting.currentText() != name:
                combobox.set_text(self.product_setting, name)
            if self.campaign_setting.currentText() != campaign_data:
                combobox.set_text(self.campaign_setting, campaign_data)
            if self.group_setting.currentText() != group_data:
                combobox.set_text(self.group_setting, group_data)
        else:
            QMessageBox.information(self, '失败', '当前设置无法进行对比', QMessageBox.Yes)
            return
        name = self.product_setting.currentText()
        campaign_setting = self.campaign_setting.currentText()
        group_setting = self.group_setting.currentText()
        list_keyword, list_match = [], []
        list_temp = self.keyword_setting.get_content()
        list_content = self.chart_data.get_content()
        list_sales = self.chart_data.get_extra()
        category = self.basic.get_category(name)
        header_new = header[-8:]
        if date_choice == '每日':
            header_new.insert(0, '日期')
        else:
            header_new.insert(0, '投放')
        if group_setting == 'All' and date_choice != '每日':
            header_new.insert(0, '广告组')
        for i in range(0, len(list_temp)):
            if group_setting == 'All':
                match = assist.get_match(campaign_setting, list_temp[i][0])
                list_keyword.append([list_temp[i][0], list_temp[i][1]])
                list_match.append(match)
            else:
                match = assist.get_match(campaign_setting, group_setting)
                list_keyword.append([list_temp[i][0]])
                list_match.append(match)
        if date_choice == '总览' and campaign_setting == 'All Ad Campaigns':
            self.chart_setting.clear()
        else:
            list_all = count.sort_by_header(list_content, list_sales, list_keyword, list_match, header, category,
                                            self.basic)
            list_point = [len(list_all) - 1]
            self.chart_setting.set_content(list_all, header_new, [], point=list_point)
        self.disconnect_setting.setDisabled(False)

    def show_chart_data(self):
        date_choice = self.choice_date_data.currentText()
        list_date = self.date_data.list_date
        if len(list_date) > 0:
            name = self.product_data.currentText()
            choice = self.choice_data.currentText()
            header = ['投放', '展现', '点击', '点击率', 'CPC', '出单', '花费', '转化率', 'ACOS']
            if self.choice_data.currentText() == '关键词':
                header.insert(1, '关键词')
            if date_choice == '总览':
                if choice == '调价':
                    header.insert(0, '匹配')
                else:
                    del header[0]
            else:
                if self.special_data.currentText() in ['All', 'Special']:
                    header.insert(0, '特殊')
                if self.variation_data.currentText() in ['All', 'Defined']:
                    header.insert(0, '变体')
                if self.bid_data.currentText() in ['All', 'Defined']:
                    header.insert(0, '出价')
                if self.traffic_data.currentText() in ['All', 'Defined']:
                    header.insert(0, '流量')
                if self.match_data.currentText() in ['All', 'Sketchy', 'Unexact']:
                    header.insert(0, '匹配')
            if date_choice == '每日':
                header.insert(0, '日期')
            dict_attach = {}
            for item in self.ad_data.selected:
                temp = []
                if '匹配' in header:
                    temp.append(assist.get_match(item[0], item[1]))
                if '流量' in header:
                    temp.append(assist.get_traffic(item[0], item[1]))
                if '出价' in header:
                    temp.append(assist.get_bid(item[0], item[1]))
                if '变体' in header:
                    temp.append(assist.get_variation(item[0], item[1], self.ad_data.all_variation))
                if '特殊' in header:
                    temp_list = assist.get_special(name, item[0], item[1], self.ad_data.all_variation)
                    temp.append(function.connect(temp_list, '-'))
                dict_attach['%s|%s' % (item[0], item[1])] = temp
            list_all, list_sales, list_point = count.count_data(list_date, self.ad_data.selected, '%s-%s' % (
                choice, date_choice), dict_attach, self.basic)
            self.chart_data.set_content(list_all, header, [], extra=list_sales, point=list_point, pb=self.progressBar)
            self.progressBar.setValue(0)
        else:
            QMessageBox.information(self, '失败', '无数据可用', QMessageBox.Yes)

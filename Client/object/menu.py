#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
import datetime
from object import tableview, listview
from object import combobox
from keywords.work import Work
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QInputDialog, QMessageBox
from PyQt5.QtGui import QCursor
from function import function
from functools import partial
from advertisement import assist


class Menu(Work):
    def __init__(self):
        super(Menu, self).__init__()
        self.viewer = None
        self.menu = QMenu(self)
        self.storage_information.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.storage_information))
        self.chart_information.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.chart_information))
        self.ship_information.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.ship_information))
        self.chart_performance.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.chart_performance))
        self.chart_setting.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.chart_setting))
        self.phrase_deny_setting.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.phrase_deny_setting))
        self.exact_deny_setting.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.exact_deny_setting))
        self.asin_deny_setting.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.asin_deny_setting))
        self.keyword_setting.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.keyword_setting))
        self.chart_data.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.chart_data))
        self.result_work.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.result_work))
        self.data_work.view.customContextMenuRequested.connect(
            lambda: self.create_menu(self.data_work))

    def create_menu(self, chart: listview.ListView or tableview.TableView):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu.clear()
        content = chart.get_selected_content()
        list_row = chart.get_selected_row()
        if chart.category == 'table':
            list_column = chart.get_selected_column()
        else:
            list_column = [0]
        if content:
            action_copy = self.menu.addAction('复制')
            action_copy.triggered.connect(lambda: function.to_clipboard(content))
        if chart.setted:
            action_clear = self.menu.addAction('清除')
            action_clear.triggered.connect(chart.clear)
        if chart.changed:
            action_mark = self.menu.addAction('标记')
            action_mark.triggered.connect(chart.mark)
            action_redo = self.menu.addAction('复原')
            action_redo.triggered.connect(chart.back)
        if content:
            if chart.category == 'list':
                action_delete = self.menu.addAction('删除')
                action_delete.triggered.connect(lambda: chart.delete(list_row))
            elif chart.name in ['keyword_setting']:
                action_delete = self.menu.addAction('删除')
                action_delete.triggered.connect(lambda: self.delete_keyword(list_row))
            if chart.name in ['keyword_setting', 'chart_setting', 'chart_data']:
                list_item = content.split('\n')
                is_asin = True
                for item in list_item:
                    if item[0: 2] != 'b0':
                        is_asin = False
                        break
                if is_asin:
                    action_view = self.menu.addAction('查看')
                    action_view.triggered.connect(lambda: self.view_picture(list_item))
            if chart.name in ['chart_setting', 'chart_data', 'chart_performance', 'result_work', 'data_work']:
                if len(list_column) == 1:
                    header = list_column[0]
                    menu_select = self.menu.addMenu('筛选')
                    list_have = list(set(chart.get_content_column(header)))
                    if len(list_have) < 10:
                        action_select = menu_select.addAction('选择')
                        action_select.triggered.connect(partial(self.select, chart, '选择', '无', header, list_have))
                    menu_character = menu_select.addMenu('字符')
                    action_character = []
                    for item in ['包含', '不包含']:
                        action_character.append(menu_character.addAction(item))
                        action_character[-1].triggered.connect(partial(self.select, chart, '字符', item, header))
                    menu_size = menu_select.addMenu('大小')
                    action_size = []
                    for item in ['大于', '等于', '小于']:
                        action_size.append(menu_size.addAction(item))
                        action_size[-1].triggered.connect(partial(self.select, chart, '大小', item, header))
                    if chart.header[header] in ['关键词', '投放']:
                        menu_keyword = menu_select.addMenu('关键词')
                        action_keyword = []
                        for item in ['ASIN', '非ASIN', '出单词', '不出单词', '高ACOS词']:
                            action_keyword.append(menu_keyword.addAction(item))
                            action_keyword[-1].triggered.connect(partial(self.select_keyword, chart, item))
            if chart.name in ['chart_setting', 'chart_data']:
                if len(list_column) == 1:
                    menu_add = self.menu.addMenu('加入')
                    action_add_deny = menu_add.addAction('否定')
                    action_add_deny.triggered.connect(partial(self.add_deny, content))
                    menu_campaign, action_group, list_bid = [], [], []
                    list_cpc = chart.get_content_by_header('CPC')
                    for row in list_row:
                        if list_cpc[row]:
                            value = round(float(list_cpc[row]) + 0.1, 2)
                        else:
                            value = 'default'
                        list_bid.append(value)
                    for campaign in self.ad_setting.list_campaign:
                        list_group = assist.get_group(campaign, self.basic)
                        if len(list_group) == 0:
                            list_group.append('')
                        list_add = []
                        for group in list_group:
                            if assist.get_match(campaign, group) != 'Auto':
                                list_add.append(group)
                        if len(list_add) > 0:
                            menu_campaign.append(menu_add.addMenu(campaign))
                            if list_add == list_group and len(list_group) > 1:
                                list_add.insert(0, 'All')
                            for group in list_add:
                                mark = campaign, group, content, list_bid
                                action_group.append(menu_campaign[-1].addAction(group))
                                action_group[-1].triggered.connect(partial(self.add_keyword, mark))
            if chart.name == 'storage_information':
                if len(list_column) == 1 and chart.header[list_column[0]] == 'SKU':
                    action_ship = self.menu.addAction('在途')
                    action_ship.triggered.connect(partial(self.show_shipment, content))
            choice = self.choice_information.currentText()
            if chart.name == 'chart_information' and chart.setted and choice == '补货':
                menu_month = self.menu.addMenu('预测')
                action_month = []
                for month in self.basic.list_month:
                    action_month.append(menu_month.addAction(month))
                    action_month[-1].triggered.connect(partial(self.predict, month))
            if chart.name == 'chart_information' and chart.setted and choice == '库销比' and not chart.changed:
                action_fix = self.menu.addAction('修正')
                action_fix.triggered.connect(self.fix)
        if chart.category == 'list' or chart.name in ['keyword_setting']:
            menu_add_up = self.menu.addMenu('添加')
            if chart.name == 'keyword_setting':
                action_keyword_input = menu_add_up.addAction('输入')
                action_keyword_input.triggered.connect(lambda: self.add_keyword(''))
                action_keyword_clipboard = menu_add_up.addAction('剪切板')
                action_keyword_clipboard.triggered.connect(lambda: self.add_keyword('clipboard'))
            else:
                action_deny = menu_add_up.addAction('输入')
                action_deny.triggered.connect(partial(self.add, chart))
        if chart.name in ['keyword_setting']:
            list_content = self.keyword_setting.get_content()
            if len(list_column) == 1 and self.keyword_setting.header[list_column[0]] == '投放':
                menu_transfer = self.menu.addMenu('转移')
                action_transfer = []
                list_now = assist.get_group(self.campaign_setting.currentText(), self.basic)
                list_need, list_transfer = [], []
                list_campaign = assist.get_campaign(self.product_setting.currentText(), self.basic)
                list_campaign.remove(self.campaign_setting.currentText())
                for campaign in list_campaign:
                    list_temp = assist.get_group(campaign, self.basic)
                    if list_temp == list_now:
                        list_need.append(campaign)
                    elif len(list_temp) == 0:
                        if self.group_setting.currentText() == 'Exact':
                            list_need.append(campaign)
                    elif not self.group_setting.isVisible():
                        if len(list_temp) == 1 and list_temp[0] == 'Exact':
                            list_need.append(campaign)
                if '广告组' not in self.keyword_setting.header:
                    list_delete = list_row.copy()
                    for row in list_delete:
                        bid = list_content[row][1]
                        list_transfer.append([self.group_setting.currentText(), list_content[row][0], bid])
                else:
                    list_delete = list_row.copy()
                    for row in list_row:
                        group = self.keyword_setting.value(row, 0)
                        keyword = self.keyword_setting.value(row, 1)
                        for i in range(0, self.keyword_setting.row_number):
                            if self.keyword_setting.value(
                                    i, 1) == keyword and self.keyword_setting.value(i, 0) != group:
                                list_delete.append(i)
                    for row in list_delete:
                        bid = list_content[row][2]
                        list_transfer.append([list_content[row][0], list_content[row][1], bid])
                for need in list_need:
                    action_transfer.append(menu_transfer.addAction(need))
                    action_transfer[-1].triggered.connect(partial(self.transfer, list_delete, need, list_transfer))
            menu_adjust = self.menu.addMenu('调整')
            action_fix = menu_adjust.addAction('固定')
            action_rate = menu_adjust.addAction('比例')
            action_impression = menu_adjust.addAction('展现量')
            action_cpc = menu_adjust.addAction('CPC')
            action_impression.triggered.connect(partial(self.adjust, 'impression'))
            action_cpc.triggered.connect(partial(self.adjust, 'cpc'))
            action_fix.triggered.connect(partial(self.adjust, 'fix'))
            action_rate.triggered.connect(partial(self.adjust, 'rate'))
            action_check = self.menu.addAction('检查')
            action_check.triggered.connect(self.check)
        if chart.name in ['data_work']:
            action_exact = self.menu.addAction('精确')
            action_exact.triggered.connect(self.exact)
        if chart.name in ['keyword_setting', 'chart_data', 'data_work']:
            if list_column == [0] and len(list_row) == 1 and chart.header[list_column[0]] in ['投放', '关键词']:
                action_history = self.menu.addAction('历史')
                action_history.triggered.connect(partial(self.get_history, content))
        position = QCursor().pos()
        height = position.y()
        line = self.pos().y() + self.geometry().height()
        if height + self.menu.height() > line:
            height = line - self.menu.height()
        position.setY(height)
        self.menu.move(position)
        self.menu.show()

    def delete_keyword(self, list_row: list):
        if '广告组' not in self.keyword_setting.header:
            self.keyword_setting.delete(list_row)
        else:
            list_real = list_row.copy()
            for row in list_row:
                group = self.keyword_setting.value(row, 0)
                keyword = self.keyword_setting.value(row, 1)
                for i in range(0, self.keyword_setting.row_number):
                    if self.keyword_setting.value(i, 1) == keyword and self.keyword_setting.value(i, 0) != group:
                        list_real.append(i)
            self.keyword_setting.delete(list_real)

    def add(self, chart: listview.ListView, content: str = ''):
        result = True
        if not content:
            content, result = QInputDialog.getText(self, '提示', '请输入添加词：')
        if result:
            list_add = content.splitlines()
            list_now = chart.get_content()
            list_exist, list_no = [], []
            for word in list_add:
                if word[0: 2] == 'b0':
                    word = word.upper()
                if word in list_now:
                    list_exist.append(word)
                else:
                    list_no.append(word)
            if list_exist:
                tip = '已存在关键词' + function.connect(list_exist, ', ')
                result = QMessageBox.information(self, '提示', tip, QMessageBox.Yes | QMessageBox.No)
            else:
                result = 16384
            if result == 16384:
                chart.add(list_no)

    def add_deny(self, content: str):
        self.campaign_setting.setCurrentIndex(0)
        list_keyword = content.splitlines()
        list_exact, list_asin = [], []
        for keyword in list_keyword:
            if keyword[0: 2] == 'b0':
                list_asin.append(keyword)
            else:
                list_exact.append(keyword)
        if len(list_asin) > 0:
            self.add(self.asin_deny_setting, function.connect(list_asin, '\n'))
        if len(list_exact) > 0:
            self.add(self.exact_deny_setting, function.connect(list_exact, '\n'))

    def add_keyword(self, mark: str):
        from object import combobox
        do = True
        if mark == '':
            if 'Auto' in self.campaign_setting.currentText():
                list_choice = ['close-match', 'loose-match', 'complements', 'substitutes']
                list_temp = self.keyword_setting.get_content_by_header('投放')
                for temp in list_temp:
                    list_choice.remove(temp)
                result = QInputDialog.getItem(self, '提示', '请选择关键词：', list_choice)
            else:
                result = QInputDialog.getText(self, '提示', '请输入关键词：')
            list_keyword = result[0].split(', ')
            list_bid = []
            for i in range(0, len(list_keyword)):
                list_bid.append('default')
            if not result[1]:
                do = False
        elif mark == 'clipboard':
            list_item = function.read_clipboard().split('\n')
            list_keyword, list_bid = [], []
            for item in list_item:
                if '\t' in item:
                    chip = item.split('\t')
                    list_keyword.append(chip[0])
                    list_bid.append(chip[1])
                else:
                    list_keyword.append(item)
                    list_bid.append('default')
        else:
            combobox.set_text(self.campaign_setting, mark[0])
            combobox.set_text(self.group_setting, mark[1])
            list_keyword = mark[2].splitlines()
            list_bid = mark[3]
        if do:
            list_add = []
            for i in range(0, len(list_keyword)):
                bid = list_bid[i]
                if bid != 'default' and 'NO' in self.campaign_setting.currentText():
                    bid = round(float(bid) - 0.1, 2)
                if list_keyword[i][0: 2] == 'b0':
                    list_keyword[i] = list_keyword[i].upper()
                list_add.append([list_keyword[i], str(bid)])
            if self.group_setting.currentText() != 'All':
                self.keyword_setting.add(list_add)
            else:
                for group in self.ad_setting.list_group:
                    list_temp = []
                    for add in list_add:
                        list_temp.append(add.copy())
                    for i in range(0, len(list_temp)):
                        list_temp[i].insert(0, group)
                    list_index = []
                    list_group = self.keyword_setting.get_content_by_header('广告组')
                    for i in range(0, len(list_group)):
                        if list_group[i] == group:
                            list_index.append(i)
                    try:
                        index = list_index[-1] + 1
                        self.keyword_setting.insert(list(range(index, index + len(list_temp))), list_temp)
                    except IndexError:
                        self.keyword_setting.add(list_temp)

    def select(self, chart: tableview.TableView, mode: str, determine: str, index: int, list_have: list = None):
        list_all = []
        if mode == '字符':
            result = QInputDialog.getText(self, '提示', '请输入字符')
            if result[1]:
                chart.delete_point()
                chart.delete_sum()
                dict_temp = {'包含': True, '不包含': False}
                for row in range(0, chart.row_number):
                    if (result[0] in chart.value(row, index)) == dict_temp[determine]:
                        list_all.append(row)
        elif mode == '大小':
            result = QInputDialog.getDouble(self, '提示', '请输入数据', decimals=2)
            if result[1]:
                chart.delete_point()
                chart.delete_sum()
                for row in range(0, chart.row_number):
                    value = chart.value(row, index)
                    if value:
                        if '%' in value:
                            value = float(value.replace('%', '')) / 100
                        else:
                            value = float(value)
                        dict_temp = {'大于': value > result[0], '小于': value < result[0], '等于': value == result[0]}
                        if dict_temp[determine]:
                            list_all.append(row)
        else:
            result = QInputDialog.getItem(self, '提示', '请选择数据', list_have)
            if result[1]:
                for row in range(0, chart.row_number):
                    value = chart.value(row, index)
                    if value == result[0]:
                        list_all.append(row)
        if result[1]:
            result = function.find_add_delete(list(range(0, chart.row_number)), list_all)
            if result[0]:
                chart.delete(result[2])

    def select_keyword(self, chart: tableview.TableView, sign: str):
        list_all = []
        if sign == 'ASIN':
            chart.delete_point()
            chart.delete_sum()
            try:
                index = chart.header.index('关键词')
            except ValueError:
                index = chart.header.index('投放')
            for row in range(0, chart.row_number):
                if 'b0' in chart.value(row, index):
                    list_all.append(row)
        elif sign == '非ASIN':
            chart.delete_point()
            chart.delete_sum()
            try:
                index = chart.header.index('关键词')
            except ValueError:
                index = chart.header.index('投放')
            for row in range(0, chart.row_number):
                if 'b0' not in chart.value(row, index):
                    list_all.append(row)
        elif sign == '出单词':
            index = chart.header.index('出单')
            result = QInputDialog.getInt(self, '请输入', '最少出单数：', 3, 1, 9, 1)
            if result[1]:
                chart.delete_point()
                chart.delete_sum()
                for row in range(0, chart.row_number):
                    value = int(chart.value(row, index))
                    if value > result[0] - 1:
                        list_all.append(row)
        elif sign == '不出单词':
            index_order = chart.header.index('出单')
            index_click = chart.header.index('点击')
            result = QInputDialog.getInt(self, '请输入', '最少点击数：', 10, 1, 99, 1)
            if result[1]:
                chart.delete_point()
                chart.delete_sum()
                for row in range(0, chart.row_number):
                    value1 = int(chart.value(row, index_order))
                    value2 = int(chart.value(row, index_click))
                    if value1 == 0 and value2 > result[0] - 1:
                        list_all.append(row)
        else:
            index = chart.header.index('ACOS')
            result = QInputDialog.getInt(self, '请输入', '最低ACOS(%)：', 80, 1, 100, 10)
            if result[1]:
                chart.delete_point()
                chart.delete_sum()
                for row in range(0, chart.row_number):
                    value = chart.value(row, index)
                    if value:
                        value = float(value.replace('%', ''))
                        if value > result[0] - 0.001:
                            list_all.append(row)
        result = function.find_add_delete(list(range(0, chart.row_number)), list_all)
        if result[0]:
            chart.delete(result[2])

    def transfer(self, list_row: list, campaign: str, list_transfer: list):
        now = self.campaign_setting.currentText()
        if self.disconnect_setting.isEnabled():
            connect = True
            self.disconnect_setting.setDisabled(True)
        else:
            connect = False
        self.keyword_setting.delete(list_row)
        combobox.set_text(self.campaign_setting, campaign)
        dict_keyword = {}
        for item in list_transfer:
            try:
                dict_keyword[item[0]].append([item[1], item[2]])
            except KeyError:
                dict_keyword[item[0]] = [[item[1], item[2]]]
        for key in dict_keyword.keys():
            if self.group_setting.isVisible() or key == '':
                combobox.set_text(self.group_setting, key)
            function.to_clipboard(dict_keyword[key])
            self.add_keyword('clipboard')
        if connect:
            self.disconnect_setting.setDisabled(False)
        combobox.set_text(self.campaign_setting, now)

    def adjust(self, mode: str):
        if mode in ['impression', 'cpc'] and not self.chart_setting.setted:
            QMessageBox.information(self, '提示', '请先对比数据', QMessageBox.Yes)
        else:
            if mode == 'impression':
                result = QInputDialog.getInt(self, '请输入', '最低展现：', 500, 10, 10000, 10)
            elif mode == 'cpc':
                result = QInputDialog.getDouble(self, '请输入', '提高：', 0.1, 0, 1)
            elif mode == 'fix':
                result = QInputDialog.getDouble(self, '请输入', '差值：', 0.1, -1, 1, decimals=2)
            else:
                result = QInputDialog.getDouble(self, '请输入', '比例：', 1.0, 0, 10, decimals=2)
            if result[1]:
                list_change, list_row = [], []
                index_keyword = self.keyword_setting.header.index('投放')
                index_bid = self.keyword_setting.header.index('bid')
                if mode in ['impression', 'cpc']:
                    if mode == 'impression':
                        index_need = self.chart_setting.header.index('展现')
                    else:
                        index_need = self.chart_setting.header.index('CPC')
                else:
                    index_need = 0
                for row in range(0, self.keyword_setting.row_number):
                    bid_str = self.keyword_setting.value(row, index_bid)
                    if bid_str == 'default':
                        default = self.default_setting.text()
                        if '{' not in default:
                            bid = float(default)
                        else:
                            bid = float(json.loads(default)[self.keyword_setting.value(row, 0)])
                    else:
                        bid = float(bid_str)
                    keyword = self.keyword_setting.value(row, index_keyword)
                    if mode in ['impression', 'cpc']:
                        if mode == 'impression':
                            impression = int(self.chart_setting.value(row, index_need))
                            if impression < result[0]:
                                new = str(round((result[0] - impression) / result[0] * 0.1 + bid, 2))
                                list_change.append([keyword, str(bid), new])
                                list_row.append(row)
                        elif mode == 'cpc':
                            try:
                                cpc = str(round(float(self.chart_setting.value(row, index_need)) + result[0], 2))
                            except ValueError:
                                cpc = 'default'
                            if cpc != bid_str:
                                list_change.append([keyword, str(bid), cpc])
                                list_row.append(row)
                    elif mode == 'fix':
                        change = str(round(bid + result[0], 2))
                        list_change.append([keyword, str(bid), change])
                        list_row.append(row)
                    else:
                        change = str(round(bid * result[0], 2))
                        list_change.append([keyword, str(bid), change])
                        list_row.append(row)
                list_temp = []
                for change in list_change:
                    list_temp.append(change[0] + ': ' + change[1] + ' -> ' + change[2])
                result = QMessageBox.information(self, '提示', function.connect(list_temp, ', '),
                                                 QMessageBox.Yes | QMessageBox.No)
                if result == 16384:
                    for row in list_row:
                        self.keyword_setting.change(row, index_bid, list_change[list_row.index(row)][2])

    def check(self):
        index = self.keyword_setting.header.index('投放')
        category = self.basic.product.get_category(self.product_setting.currentText())
        if '广告组' not in self.keyword_setting.header:
            list_group = [self.group_setting.currentText()]
            dict_keyword = {}
        else:
            dict_keyword = {}
            for i in range(0, self.keyword_setting.row_number):
                try:
                    dict_keyword[self.keyword_setting.value(i, 0)].append(self.keyword_setting.value(i, 1))
                except KeyError:
                    dict_keyword[self.keyword_setting.value(i, 0)] = [self.keyword_setting.value(i, 1)]
            list_group = list(dict_keyword.keys())
        before = 1
        for group in list_group:
            if '广告组' not in self.keyword_setting.header:
                number1 = self.keyword_setting.row_number - 1
            else:
                number1 = len(dict_keyword[group]) - 1
            for row in range(0, number1):
                if '广告组' not in self.keyword_setting.header:
                    keyword1 = self.keyword_setting.value(row, index)
                else:
                    keyword1 = dict_keyword[group][row]
                list_temp = self.basic.keyword.simplify_split(keyword1, category)
                if assist.get_match(self.campaign_setting.currentText(), group) == 'Broad':
                    list_temp.sort()
                fake = function.connect(list_temp, ' ')
                if '广告组' not in self.keyword_setting.header:
                    number2 = self.keyword_setting.row_number
                else:
                    number2 = len(dict_keyword[group])
                for line in range(row + 1, number2):
                    if '广告组' not in self.keyword_setting.header:
                        keyword2 = self.keyword_setting.value(line, index)
                    else:
                        keyword2 = dict_keyword[group][line]
                    list_temp = self.basic.keyword.simplify_split(keyword2, category)
                    if assist.get_match(self.campaign_setting.currentText(), group) == 'Broad':
                        list_temp.sort()
                    if function.connect(list_temp, ' ') == fake:
                        QMessageBox.information(self, '提示', '存在相似关键词：%d.%s与%d.%s' %
                                                (row + before, keyword1, line + before, keyword2), QMessageBox.Yes)
                        return
            if '广告组' in self.keyword_setting.header:
                before += len(dict_keyword[group])
        QMessageBox.information(self, '提示', '不存在相似关键词', QMessageBox.Yes)

    def exact(self):
        name = self.product_work.currentText()
        if name not in ['All', '']:
            list_fit = self.basic.get_fit_keyword(name)
            category = self.basic.product.get_category(name)
            list_fit += self.basic.keyword.type_synonym[category]
            for fit in list_fit:
                if fit in self.basic.keyword.plural.keys():
                    list_fit.append(self.basic.keyword.plural[fit])
            list_fit += self.basic.keyword.no_use
            list_delete = []
            for i in range(0, self.data_work.row_number):
                keyword = self.data_work.value(i, 0)
                list_item = keyword.split(' ')
                for fit in list_fit:
                    if ' ' in fit:
                        list_temp = fit.split(' ')
                        list_index = []
                        for temp in list_temp:
                            try:
                                list_index.append(list_item.index(temp))
                            except ValueError:
                                break
                        if len(list_index) == len(list_temp):
                            judge = True
                            for j in range(0, len(list_index) - 1):
                                if list_index[j + 1] - list_index[j] > 1:
                                    judge = False
                            if judge:
                                list_index.sort(reverse=True)
                                for index in list_index:
                                    del list_item[index]
                judge = False
                for item in list_item:
                    if item not in list_fit:
                        judge = True
                        break
                if judge:
                    list_delete.append(i)
            self.data_work.delete(list_delete)

    def view_picture(self, list_item: list):
        from object import picture_viewer
        self.viewer = picture_viewer.PictureViewer(list_item, self.basic)
        self.viewer.show()

    def get_history(self, text: str):
        result = self.basic.get_history(text)
        if not result:
            QMessageBox.information(self, '提示', '暂无数据', QMessageBox.Yes)
        else:
            dict_rank = json.loads(result[0])
            dict_temp = {}
            for season in dict_rank.keys():
                year = season[0: 2]
                try:
                    dict_temp[year].append('%s: %s' % (season, dict_rank[season]))
                except KeyError:
                    dict_temp[year] = ['%s: %s' % (season, dict_rank[season])]
            list_temp = []
            for year in dict_temp.keys():
                list_temp.append(function.connect(dict_temp[year], ', '))
            QMessageBox.information(self, '提示', function.connect(list_temp, '\n'), QMessageBox.Yes)

    def show_shipment(self, content: str):
        list_all = []
        for sku in content.splitlines():
            name = self.product_information.currentText()
            list_need = [(self.basic.get_store(name), sku)]
            try:
                dict_child_gm = self.basic.child_gm[name]
            except KeyError:
                dict_child_gm = {}
            if sku in dict_child_gm.keys():
                for key in dict_child_gm[sku].keys():
                    list_need.append((key, dict_child_gm[sku][key]))
            for item in self.basic.shipment:
                if (item[0], item[2]) in list_need:
                    now = datetime.datetime.now()
                    start = datetime.datetime.strptime(item[4], "%Y-%m-%d")
                    diff = now - start
                    list_all.append([item[0], item[2], item[1], item[4], item[3], item[5], item[6] - diff.days])
        header = ['店铺', 'SKU', '货件编号', '日期', '数量', '渠道', '预计剩余']
        self.ship_information.set_content(list_all, header, [])

    def predict(self, month: str):
        name = self.product_information.currentText()
        dict_information = self.basic.get_information(name)
        category = self.basic.get_category(name)
        audience = dict_information['audience']
        season = dict_information['season']
        dict_rate = json.loads(self.basic.get_season(audience, category, season)[0])
        rate1, rate2 = 0, 0
        for date in self.date_information.list_date:
            rate1 += dict_rate[str(int(date[5: 7])) + '/' + str(int(date[8: 10]))]
        for item in list(dict_rate.keys()):
            if item.split('/')[0] == month.replace('月', ''):
                rate2 += dict_rate[item]
        rate = rate2 / rate1
        item1, orders = round(rate, 2), 0
        for row in range(0, self.chart_information.row_number):
            item2 = int(round(rate * int(self.chart_information.value(row, 1)), 0))
            self.chart_information.change(row, 2, str(item1))
            self.chart_information.change(row, 3, str(item2))
        self.chart_information.resize_width()

    def fix(self):
        name = self.product_information.currentText()
        dict_information = self.basic.get_information(name)
        category = self.basic.get_category(name)
        audience = dict_information['audience']
        season = dict_information['season']
        dict_rate = json.loads(self.basic.get_season(audience, category, season)[0])
        power = 0
        for date in self.date_information.list_date:
            power += dict_rate[str(int(date[5: 7])) + '/' + str(int(date[8: 10]))]
        day = len(self.date_information.list_date)
        for row in range(0, self.chart_information.row_number):
            order = int(self.chart_information.value(row, 1))
            for column in [2, 3]:
                start = self.date_information.list_date[-1]
                if self.chart_information.value(row, column):
                    need = 0
                    storage = round(float(self.chart_information.value(row, column)) * order / day, 0)
                    while True:
                        nex = function.get_day(start, 1)[1]
                        temp = dict_rate[str(int(nex[5: 7])) + '/' + str(int(nex[8: 10]))]
                        predict = order / power * temp
                        storage -= predict
                        need += 1
                        if storage < 1:
                            break
                        start = nex
                    self.chart_information.change(row, column, str(need))
        self.chart_information.resize_width()

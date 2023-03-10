#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM
import json

from PyQt5.QtWidgets import QMessageBox
from advertisement import count
from function import function
from object import listview, tableview, advertisement
from object import combobox
from product.performance import Performance


class Setting(Performance):
    def __init__(self):
        super(Setting, self).__init__()
        self.global_before = {}
        self.global_ad_data = {}
        self.strategy_setting.addItems(['固定竞价', '只降低', '提高和降低', '自动', '手动', '对访问优化', '对转化优化', '对曝光优化'])
        self.phrase_deny_setting = listview.ListView(self.list1_setting, 'phrase_deny', 'setting')
        self.exact_deny_setting = listview.ListView(self.list2_setting, 'exact_deny', 'setting')
        self.asin_deny_setting = listview.ListView(self.list3_setting, 'asin_deny', 'setting')
        self.deny_setting = {'phrase': self.phrase_deny_setting, 'exact': self.exact_deny_setting,
                             'asin': self.asin_deny_setting}
        self.keyword_setting = tableview.TableView(self.table1_setting, 'keyword', 'setting', self.basic.power)
        self.chart_setting = tableview.TableView(self.table2_setting, 'chart', 'setting', self.basic.power)
        self.ad_setting = advertisement.AdSimple(self.campaign_setting, self.group_setting, self.basic)
        self.product_setting.currentIndexChanged.connect(
            lambda: self.ad_setting.refresh(self.product_setting.currentText()))
        self.group_setting.currentIndexChanged.connect(self.operate_setting)
        self.extract_setting.clicked.connect(self.extract_file)
        self.save_setting.clicked.connect(lambda: self.save_data_setting(False))
        self.disconnect_setting.clicked.connect(self.cut_connect_setting)
        self.disconnect_setting.setDisabled(True)
        self.generate_setting.clicked.connect(self.generate_file)
        self.redo_setting.clicked.connect(self.show_data_setting)
        self.product_setting.addItems(self.basic.product_list)

    def read_data_setting(self):
        name = self.product_setting.currentText()
        self.global_ad_data.clear()
        data = self.basic.get_deny(name)
        self.global_ad_data['deny'] = {}
        list_item = ['phrase', 'exact', 'asin']
        for i in range(0, len(list_item)):
            if data[i] is None:
                self.global_ad_data['deny'][list_item[i]] = []
            else:
                self.global_ad_data['deny'][list_item[i]] = data[i].splitlines()
        data = self.basic.get_campaign(name)
        list_item = ['add', 'delete']
        for i in range(0, len(list_item)):
            self.global_ad_data['deny'][list_item[i]] = {}
            for item in data:
                self.global_ad_data['deny'][list_item[i]][item[0]] = json.loads(item[7 + i])
        dict_temp = {'budget': {}, 'page': {}, 'top': {}, 'strategy': {}, 'default': {}, 'keyword': {}}
        self.global_ad_data.update(dict_temp)
        for item in data:
            self.global_ad_data['budget'][item[0]] = float(item[3])
            self.global_ad_data['page'][item[0]] = float(item[4])
            self.global_ad_data['top'][item[0]] = float(item[5])
            self.global_ad_data['strategy'][item[0]] = json.loads(item[6])
            self.global_ad_data['default'][item[0]] = json.loads(item[9])
            self.global_ad_data['keyword'][item[0]] = json.loads(item[10])

    def backup_setting(self):
        dict_deny = {'phrase': self.phrase_deny_setting.get_content(),
                     'exact': self.exact_deny_setting.get_content(),
                     'asin': self.asin_deny_setting.get_content()}
        self.global_before = {'product': self.ad_setting.product, 'campaign': self.ad_setting.campaign.currentText(),
                              'group': self.ad_setting.group.currentText(), 'list_group': self.ad_setting.list_group,
                              'selected': self.ad_setting.selected.copy(), 'match': self.ad_setting.list_match.copy(),
                              'deny': dict_deny, 'keyword': self.keyword_setting.get_content()}

    def operate_setting(self):
        if len(self.global_before) > 0:
            self.save_data_setting(True)
        try:
            name = self.global_before['product']
            if name != self.product_setting.currentText():
                self.read_data_setting()
        except KeyError:
            self.read_data_setting()
        self.show_data_setting()

    def get_special_deny(self, category: str):
        list_result = []
        for item in self.ad_setting.selected:
            list_all = []
            for temp in ['add', 'delete']:
                try:
                    list_word = self.global_ad_data['deny'][temp][item[0]][category][item[1]]
                except KeyError:
                    list_word = []
                list_all.append(list_word)
            list_real = function.operate_add_delete(self.global_ad_data['deny'][category], list_all[0], list_all[1])
            list_result = function.find_cross_element(list_result, list_real)
        return list_result

    def show_data_setting(self):
        campaign = self.campaign_setting.currentText()
        group = self.group_setting.currentText()
        if campaign in ['All Ad Campaigns', '']:
            self.budget_setting.setDisabled(True)
            self.label_24.hide()
            self.label_26.hide()
            self.top_setting.hide()
            self.label_25.hide()
            self.label_27.hide()
            self.page_setting.hide()
            self.label_34.hide()
            self.strategy_setting.hide()
            self.label_30.hide()
            self.default_setting.hide()
            self.keyword_setting.model.clear()
            self.keyword_setting.view.setDisabled(True)
            if campaign == 'All Ad Campaigns':
                self.budget_setting.setText(str(function.sum_value(self.global_ad_data['budget'])))
                self.phrase_deny_setting.view.setDisabled(False)
                self.phrase_deny_setting.set_content(self.global_ad_data['deny']['phrase'])
                self.exact_deny_setting.view.setDisabled(False)
                self.exact_deny_setting.set_content(self.global_ad_data['deny']['exact'])
                self.asin_deny_setting.view.setDisabled(False)
                self.asin_deny_setting.set_content(self.global_ad_data['deny']['asin'])
                self.backup_setting()
            else:
                self.budget_setting.clear()
                self.phrase_deny_setting.clear()
                self.phrase_deny_setting.view.setDisabled(True)
                self.exact_deny_setting.clear()
                self.exact_deny_setting.view.setDisabled(True)
                self.asin_deny_setting.clear()
                self.asin_deny_setting.view.setDisabled(True)
                self.global_before.clear()
        else:
            self.budget_setting.setDisabled(False)
            self.budget_setting.setText(str(self.global_ad_data['budget'][campaign]))
            self.label_24.show()
            self.label_26.show()
            self.top_setting.show()
            self.top_setting.setText(str(self.global_ad_data['top'][campaign]))
            self.label_25.show()
            self.label_27.show()
            self.page_setting.show()
            self.page_setting.setText(str(self.global_ad_data['page'][campaign]))
            dict_strategy = self.global_ad_data['strategy'][campaign]
            if 'All' in dict_strategy.keys():
                self.label_34.show()
                self.strategy_setting.show()
                combobox.set_text(self.strategy_setting, self.basic.strategy[dict_strategy['All']])
            else:
                self.label_34.hide()
                self.strategy_setting.hide()
            if group not in ['All', '']:
                if 'All' not in dict_strategy.keys():
                    self.label_34.show()
                    self.strategy_setting.show()
                    combobox.set_text(self.strategy_setting, self.basic.strategy[dict_strategy[group]])
                self.label_30.show()
                self.default_setting.show()
                self.default_setting.setText(str(self.global_ad_data['default'][campaign][group]))
            else:
                self.label_30.hide()
                self.default_setting.hide()
                if group == 'All':
                    dict_temp = {}
                    for item in self.ad_setting.list_group:
                        dict_temp[item] = str(self.global_ad_data['default'][campaign][item])
                    self.default_setting.setText(str(dict_temp))
                else:
                    self.default_setting.clear()
            if len(self.ad_setting.list_match) == 0 or self.ad_setting.list_match[0] not in ['Exact', 'PT', 'CT', 'AT']:
                self.phrase_deny_setting.view.setDisabled(False)
                self.phrase_deny_setting.set_content(self.get_special_deny('phrase'))
                self.exact_deny_setting.view.setDisabled(False)
                self.exact_deny_setting.set_content(self.get_special_deny('exact'))
            else:
                self.phrase_deny_setting.clear()
                self.phrase_deny_setting.view.setDisabled(True)
                self.exact_deny_setting.clear()
                self.exact_deny_setting.view.setDisabled(True)
            if len(self.ad_setting.list_match) > 0 and self.ad_setting.list_match[0] in ['Auto', 'CT']:
                self.asin_deny_setting.view.setDisabled(False)
                self.asin_deny_setting.set_content(self.get_special_deny('asin'))
            else:
                self.asin_deny_setting.clear()
                self.asin_deny_setting.view.setDisabled(True)
            list_all = count.get_bid(campaign, group, self.global_ad_data['keyword'])
            header = ['投放', 'bid']
            if group == 'All':
                header.insert(0, '广告组')
            self.keyword_setting.view.setDisabled(False)
            self.keyword_setting.set_content(list_all, header, [])
            if self.disconnect_setting.isEnabled():
                if self.choice_date_data.currentText() == '总览':
                    if self.product_setting.currentText() != self.product_data.currentText():
                        combobox.set_text(self.product_data, self.product_setting.currentText())
                        self.show_chart_data()
                else:
                    if self.product_setting.currentText() != self.product_data.currentText():
                        combobox.set_text(self.product_data, self.product_setting.currentText())
                    combobox.set_text(self.campaign_data, self.campaign_setting.currentText())
                    combobox.set_text(self.group_data, self.group_setting.currentText())
                    self.show_chart_data()
                self.contrast_advertisement()
            self.backup_setting()

    def common_save_setting(self, category: str):
        list_word = self.deny_setting[category].get_content()
        if list_word != self.global_ad_data['deny'][category]:
            result = function.find_add_delete(self.global_ad_data['deny'][category], list_word)
            list_sign = ['add', 'delete']
            for sign in list_sign:
                for campaign in list(self.global_ad_data['deny'][sign].keys()):
                    changed = False
                    list_change = result[list_sign.index(sign) + 1]
                    for group in list(self.global_ad_data['deny'][sign][campaign][category].keys()):
                        removed = False
                        for word in list_change:
                            try:
                                self.global_ad_data['deny'][sign][campaign][category][group].remove(word)
                                removed = True
                            except ValueError:
                                pass
                        if removed:
                            changed = True
                            if len(self.global_ad_data['deny'][sign][campaign][category][group]) == 0:
                                del self.global_ad_data['deny'][sign][campaign][category][group]
                    if changed:
                        text_deny = json.dumps(self.global_ad_data['deny'][sign][campaign])
                        self.basic.change_special_deny(campaign, sign, text_deny)
            text_word = function.connect(list_word, '\r\n')
            self.basic.change_deny(self.global_before['product'], category, text_word)
            self.global_ad_data['deny'][category] = list_word

    def special_save_setting(self, category: str):
        list_word = self.deny_setting[category].get_content()
        campaign = self.global_before['campaign']
        list_sign = ['add', 'delete']
        if list_word != self.global_before['deny'][category]:
            result = function.find_add_delete(self.global_before['deny'][category], list_word)
            changed = {'add': False, 'delete': False}
            if self.global_before['group'] == 'All':
                list_group = self.global_before['list_group']
            else:
                list_group = [self.global_before['group']]
            for group in list_group:
                for sign in list_sign:
                    index = list_sign.index(sign)
                    list_word = result[index + 1]
                    if len(list_word) > 0:
                        reverse = list_sign[index * -1 - 1]
                        try:
                            list_reverse = self.global_ad_data['deny'][reverse][campaign][category][group]
                        except KeyError:
                            list_reverse = []
                        removed = False
                        for item in list_word:
                            if item in list_reverse:
                                self.global_ad_data['deny'][reverse][campaign][category][group].remove(item)
                                removed = True
                            else:
                                try:
                                    self.global_ad_data['deny'][sign][campaign][category][group].append(item)
                                except KeyError:
                                    self.global_ad_data['deny'][sign][campaign][category][group] = [item]
                                changed[sign] = True
                        if removed:
                            changed[reverse] = True
                            try:
                                if len(self.global_ad_data['deny'][reverse][campaign][category][group]) == 0:
                                    del self.global_ad_data['deny'][reverse][campaign][category][group]
                            except KeyError:
                                pass
            for sign in list_sign:
                if changed[sign]:
                    text_deny = json.dumps(self.global_ad_data['deny'][sign][campaign])
                    self.basic.change_special_deny(campaign, sign, text_deny)

    def save_data_setting(self, stop: bool):
        campaign = self.global_before['campaign']
        if campaign == 'All Ad Campaigns':
            self.common_save_setting('phrase')
            self.common_save_setting('exact')
            self.common_save_setting('asin')
        else:
            budget = float(self.budget_setting.text())
            strategy = self.basic.strategy[self.strategy_setting.currentText()]
            top = float(self.top_setting.text())
            page = float(self.page_setting.text())
            group = self.global_before['group']
            if len(self.global_before['match']) == 0 or self.global_before['match'][0] not in ['Exact', 'PT']:
                self.special_save_setting('phrase')
                self.special_save_setting('exact')
            if len(self.global_before['match']) > 0 and self.global_before['match'][0] == 'Auto':
                self.special_save_setting('asin')
            if self.global_ad_data['budget'][campaign] != budget:
                self.global_ad_data['budget'][campaign] = budget
                self.basic.change_budget(campaign, budget)
            if 'All' in self.global_ad_data['strategy'][campaign].keys():
                if self.global_ad_data['strategy'][campaign]['All'] != strategy:
                    self.global_ad_data['strategy'][campaign]['All'] = strategy
                    text_strategy = json.dumps(self.global_ad_data['strategy'][campaign])
                    self.basic.change_strategy(campaign, text_strategy)
            elif group not in ['All', '']:
                if self.global_ad_data['strategy'][campaign][group] != strategy:
                    self.global_ad_data['strategy'][campaign][group] = strategy
                    text_strategy = json.dumps(self.global_ad_data['strategy'][campaign])
                    self.basic.change_strategy(campaign, text_strategy)
            if self.global_ad_data['top'][campaign] != top:
                self.global_ad_data['top'][campaign] = top
                self.basic.change_top(campaign, top)
            if self.global_ad_data['page'][campaign] != page:
                self.global_ad_data['page'][campaign] = page
                self.basic.change_page(campaign, page)
            if group not in ['All', '']:
                default = float(self.default_setting.text())
                if self.global_ad_data['default'][campaign][group] != default:
                    self.global_ad_data['default'][campaign][group] = default
                    text_default = json.dumps(self.global_ad_data['default'][campaign])
                    self.basic.change_default(campaign, text_default)
            list_keyword = self.keyword_setting.get_content()
            if list_keyword != self.global_before['keyword']:
                if group != 'All':
                    self.global_ad_data['keyword'][campaign][group].clear()
                    for i in range(0, len(list_keyword)):
                        keyword = list_keyword[i][0]
                        if list_keyword[i][1] == 'default':
                            bid = 'default'
                        else:
                            bid = float(list_keyword[i][1])
                        self.global_ad_data['keyword'][campaign][group][keyword] = bid
                else:
                    self.global_ad_data['keyword'][campaign].clear()
                    for group in self.global_before['list_group']:
                        self.global_ad_data['keyword'][campaign][group] = {}
                    for i in range(0, len(list_keyword)):
                        group = list_keyword[i][0]
                        keyword = list_keyword[i][1]
                        if list_keyword[i][2] == 'default':
                            bid = 'default'
                        else:
                            bid = float(list_keyword[i][2])
                        self.global_ad_data['keyword'][campaign][group][keyword] = bid
                text_keyword = json.dumps(self.global_ad_data['keyword'][campaign])
                self.basic.change_keyword(campaign, text_keyword)
        self.basic.commit()
        if not stop:
            self.backup_setting()
            if self.disconnect_setting.isEnabled():
                self.contrast_advertisement()

    def cut_connect_setting(self):
        self.disconnect_setting.setDisabled(True)
        self.chart_setting.clear()

    def extract_file(self):
        from function.extract.setting import extract_setting
        extract_setting(self.product_setting.currentText(), self.basic)
        try:

            QMessageBox.information(self, '提示', '广告数据导入成功', QMessageBox.Yes)
        except Exception as ex:
            QMessageBox.information(self, '提示', '广告数据导入失败：%s' % ex, QMessageBox.Yes)

    def generate_file(self):
        self.save_data_setting(True)
        from function.generate.file import generate_file
        generate_file(self.basic, self.product_setting.currentText(), self.progressBar)
        try:

            QMessageBox.information(self, '成功', '批量文件导出成功', QMessageBox.Yes)
        except Exception as ex:
            QMessageBox.information(self, '失败', '批量文件导出失败：%s' % ex, QMessageBox.Yes)
        self.progressBar.setValue(0)

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from advertisement import assist
from PyQt5.QtWidgets import QComboBox
from object import combobox
from object.basic import Basic


class AdSimple:
    def __init__(self, campaign: QComboBox, group: QComboBox, basic: Basic):
        self.product = ''
        self.campaign = campaign
        self.group = group
        self.list_campaign = []
        self.list_group = []
        self.selected = []
        self.list_match = []
        self.level = 0
        self.selected_save = {}
        self.chain = 0
        self.campaign.currentIndexChanged.connect(self.group_change)
        self.group.currentIndexChanged.connect(self.match_change)
        self.basic = basic

    def refresh(self, name: str):
        self.product = name
        list_campaign = assist.get_campaign(name, self.basic)
        list_campaign = assist.match_sort(list_campaign)
        self.list_campaign = list_campaign.copy()
        if len(list_campaign) > 0:
            list_campaign.insert(0, 'All Ad Campaigns')
        combobox.reset_value(self.campaign, list_campaign)

    def group_change(self):
        self.level = 1
        self.chain = 1
        campaign = self.campaign.currentText()
        if campaign == 'All Ad Campaigns':
            list_campaign = self.list_campaign
        else:
            list_campaign = [campaign]
        list_group = []
        list_selected = []
        for campaign in list_campaign:
            list_result = assist.get_group(campaign, self.basic)
            if len(list_result) > 0:
                for group in list_result:
                    if group not in list_group:
                        list_group.append(group)
                    list_selected.append([campaign, group])
            else:
                list_selected.append([campaign, ''])
        self.list_group = list_group.copy()
        self.selected = list_selected
        self.selected_save[1] = self.selected.copy()
        if len(list_group) > 1:
            list_group.insert(0, 'All')
        if len(list_group) == 0:
            self.group.hide()
        else:
            self.group.show()
        combobox.reset_value(self.group, list_group)

    def match_change(self):
        level = 2
        group = self.group.currentText()
        self.correct(level)
        if group != 'All':
            list_selected = []
            for item in self.selected:
                if item[1] == group:
                    list_selected.append(item)
            self.selected = list_selected
        self.selected_save[level] = self.selected.copy()
        list_match = []
        for item in self.selected:
            result = assist.get_match(item[0], item[1])
            if result not in list_match:
                list_match.append(result)
        self.list_match = list_match
        self.chain = 0

    def correct(self, level: int):
        if self.chain == 0:
            if self.level > level - 1:
                self.selected = self.selected_save[level - 1].copy()
            self.level = level
            self.chain = 1

    def update(self, basic: Basic):
        self.basic = basic


class AdComplex(AdSimple):
    def __init__(self, campaign: QComboBox, group: QComboBox, match: QComboBox, traffic: QComboBox, bid: QComboBox,
                 variation: QComboBox, special: QComboBox, basic: Basic):
        super(AdComplex, self).__init__(campaign, group, basic)
        self.match = match
        self.list_match = []
        self.traffic = traffic
        self.list_traffic = []
        self.bid = bid
        self.list_bid = []
        self.all_variation = []
        self.variation = variation
        self.list_variation = []
        self.special = special
        self.list_special = []
        self.match.currentIndexChanged.connect(self.traffic_change)
        self.traffic.currentIndexChanged.connect(self.bid_change)
        self.bid.currentIndexChanged.connect(self.variation_change)
        self.variation.currentIndexChanged.connect(self.special_change)
        self.special.currentIndexChanged.connect(self.selected_change)

    def refresh(self, name: str):
        self.product = name
        list_campaign = assist.get_campaign(name, self.basic, 'all')
        list_campaign = assist.match_sort(list_campaign)
        self.list_campaign = list_campaign.copy()
        if len(list_campaign) > 1:
            list_campaign.insert(0, 'All Ad Campaigns')
        self.all_variation = self.basic.list_variation[self.basic.get_category(name)]
        combobox.reset_value(self.campaign, list_campaign)

    def match_change(self):
        level = 2
        group = self.group.currentText()
        self.correct(level)
        if group != 'All':
            list_selected = []
            for item in self.selected:
                if item[1] == group:
                    list_selected.append(item)
            self.selected = list_selected
        self.selected_save[level] = self.selected.copy()
        list_match = []
        for item in self.selected:
            result = assist.get_match(item[0], item[1])
            if result not in list_match:
                list_match.append(result)
        self.list_match = list_match.copy()
        if 'Broad' in list_match and 'Phrase' in list_match:
            list_match.append('Sketchy')
        if 'Auto' in list_match or 'CT' in list_match:
            if 'Broad' in list_match or 'Phrase' in list_match:
                list_match.append('Unexact')
        elif 'Auto' in list_match and 'CT' in list_match:
            list_match.append('Unexact')
        list_match = assist.match_sort(list_match)
        list_test = list_match.copy()
        if 'Sketchy' in list_match:
            list_test.remove('Broad')
            list_test.remove('Phrase')
        if 'Unexact' in list_match:
            if 'Auto' in list_test:
                list_test.remove('Auto')
            if 'CT' in list_test:
                list_test.remove('CT')
            if 'Broad' in list_test:
                list_test.remove('Broad')
            if 'Phrase' in list_test:
                list_test.remove('Phrase')
        if 'Sketchy' in list_match and 'Unexact' in list_match:
            if 'Broad' in list_match and 'Phrase' in list_match:
                list_test.remove('Sketchy')
        if len(list_test) > 1:
            list_match.insert(0, 'All')
        combobox.reset_value(self.match, list_match)

    def traffic_change(self):
        level = 3
        match = self.match.currentText()
        self.correct(level)
        if match == 'All':
            list_match = ['Auto', 'Broad', 'Phrase', 'Exact', 'PT', 'CT', 'AT']
        elif match == 'Sketchy':
            list_match = ['Broad', 'Phrase']
        elif match == 'Unexact':
            list_match = ['Auto', 'Broad', 'Phrase', 'CT']
        elif match == 'Manual':
            list_match = ['Broad', 'Phrase', 'Exact']
        else:
            list_match = [match]
        list_selected = []
        for item in self.selected:
            result = assist.get_match(item[0], item[1])
            if result in list_match:
                list_selected.append(item)
        self.selected = list_selected
        self.selected_save[level] = self.selected.copy()
        list_traffic = []
        for item in self.selected:
            result = assist.get_traffic(item[0], item[1])
            if result not in list_traffic:
                list_traffic.append(result)
        self.list_traffic = list_traffic.copy()
        list_test = []
        count = 0
        for item in ['Low', 'Medium', 'High']:
            if item in list_traffic:
                list_test.append(item)
                count += 1
        if count > 1:
            list_test.insert(0, 'Defined')
        if 'Undefined' in list_traffic:
            list_test.insert(0, 'Undefined')
        if count > 0 and 'Undefined' in list_traffic:
            list_test.insert(0, 'All')
        combobox.reset_value(self.traffic, list_test)

    def bid_change(self):
        level = 4
        traffic = self.traffic.currentText()
        self.correct(level)
        if traffic == 'All':
            list_traffic = ['Undefined', 'Low', 'Medium', 'High']
        elif traffic == 'Defined':
            list_traffic = ['Low', 'Medium', 'High']
        else:
            list_traffic = [traffic]
        list_selected = []
        for item in self.selected:
            result = assist.get_traffic(item[0], item[1])
            if result in list_traffic:
                list_selected.append(item)
        self.selected = list_selected
        self.selected_save[level] = self.selected.copy()
        list_bid = []
        for item in self.selected:
            result = assist.get_bid(item[0], item[1])
            if result not in list_bid:
                list_bid.append(result)
        self.list_bid = list_bid.copy()
        list_test = []
        count = 0
        for item in ['Low', 'Medium', 'High']:
            if item in list_bid:
                list_test.append(item)
                count += 1
        if count > 1:
            list_test.insert(0, 'Defined')
        if 'Undefined' in list_bid:
            list_test.insert(0, 'Undefined')
        if count > 0 and 'Undefined' in list_bid:
            list_test.insert(0, 'All')
        combobox.reset_value(self.bid, list_test)

    def variation_change(self):
        level = 5
        bid = self.bid.currentText()
        self.correct(level)
        if bid == 'All':
            list_bid = ['Undefined', 'Low', 'Medium', 'High']
        elif bid == 'Defined':
            list_bid = ['Low', 'Medium', 'High']
        else:
            list_bid = [bid]
        list_selected = []
        for item in self.selected:
            result = assist.get_bid(item[0], item[1])
            if result in list_bid:
                list_selected.append(item)
        self.selected = list_selected
        self.selected_save[level] = self.selected.copy()
        list_variation = []
        for item in self.selected:
            result = assist.get_variation(item[0], item[1], self.all_variation)
            if result not in list_variation:
                list_variation.append(result)
        self.list_variation = list_variation.copy()
        undefined = 0
        if 'Undefined' in list_variation:
            undefined = 1
            list_variation.remove('Undefined')
        definded = 0
        if len(list_variation) > 1:
            definded = 1
            list_variation.sort()
        if definded == 1:
            list_variation.insert(0, 'Defined')
        if undefined == 1:
            list_variation.insert(0, 'Undefined')
        if undefined == 1 and len(self.list_variation) > 1:
            list_variation.insert(0, 'All')
        combobox.reset_value(self.variation, list_variation)

    def special_change(self):
        level = 6
        variation = self.variation.currentText()
        self.correct(level)
        if variation == 'All':
            list_variation = ['Undefined'] + self.all_variation
        elif variation == 'Defined':
            list_variation = self.all_variation
        else:
            list_variation = [variation]
        list_selected = []
        for item in self.selected:
            result = assist.get_variation(item[0], item[1], self.all_variation)
            if result in list_variation:
                list_selected.append(item)
        self.selected = list_selected
        self.selected_save[level] = self.selected.copy()
        list_special = []
        for item in self.selected:
            result = assist.get_special(self.product, item[0], item[1], self.all_variation)
            for temp in result:
                if temp not in list_special:
                    list_special.append(temp)
        self.list_special = list_special.copy()
        normal = 0
        if 'Normal' in list_special:
            normal = 1
            list_special.remove('Normal')
        special = 0
        if len(list_special) > 1:
            special = 1
            list_special.sort()
        if special == 1:
            list_special.insert(0, 'Special')
        if normal == 1:
            list_special.insert(0, 'Normal')
        if normal == 1 and len(self.list_special) > 1:
            list_special.insert(0, 'All')
        combobox.reset_value(self.special, list_special)

    def selected_change(self):
        level = 7
        special = self.special.currentText()
        self.correct(level)
        list_selected = []
        for item in self.selected:
            if special == 'All':
                list_selected.append(item)
            elif special == 'Normal':
                result = assist.get_special(self.product, item[0], item[1], self.all_variation)
                if result == ['Normal']:
                    list_selected.append(item)
            elif special == 'Special':
                result = assist.get_special(self.product, item[0], item[1], self.all_variation)
                if result != ['Normal']:
                    list_selected.append(item)
            else:
                result = assist.get_special(self.product, item[0], item[1], self.all_variation)
                if special in result:
                    list_selected.append(item)
        self.selected = list_selected
        self.chain = 0

    def update(self, basic: Basic):
        self.basic = basic

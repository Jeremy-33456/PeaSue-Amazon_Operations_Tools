#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
import pymysql
from function import function


class Keyword:
    def __init__(self, user: str, session: str, cursor: pymysql.cursors):
        self.__data = {}
        for temp in ['keyword', 'audience', 'brand', 'color', 'size', 'plural']:
            cursor.callproc('get_%s' % temp, (user, session))
            self.__data[temp] = cursor.fetchall()
        self.type = [i[0] for i in self.__data['keyword']]
        self.audience = {'main': [], 'all': [], 'extra': [], 'synonym': {'none': []}}
        self.audisence = {'all': [], 'synonym': {}, 'belong': {}}
        self.plural, self.brand, self.size, self.type_synonym = {}, {}, {}, {}
        for item in self.__data['keyword']:
            self.brand[item[0]] = {'main': [], 'all': [], 'extra': [], 'synonym': {}, 'belong': {}}
        self.color = {'main': [], 'all': [], 'extra': [], 'title': [], 'synonym': {}, 'belong': {}}
        for item in self.__data['keyword']:
            self.size[item[0]] = {}
        for item in self.__data['audience']:
            self.audience['all'].append(item[0])
            list_temp = item[1].splitlines()
            if item[0] not in list_temp:
                self.audience['extra'].append(item[0])
            for temp in list_temp:
                if temp not in self.audience['main']:
                    self.audience['main'].append(temp)
                try:
                    self.audience['synonym'][temp].append(item[0])
                except KeyError:
                    self.audience['synonym'][temp] = [item[0]]
            list_temp = item[2].splitlines()
            self.audisence['all'] += list_temp
            self.audisence['synonym'][item[0]] = list_temp
            for temp in list_temp:
                self.audisence['belong'][temp] = item[0]
        for item in self.__data['brand']:
            for category in item[1].splitlines():
                self.brand[category]['main'].append(item[0])
                self.brand[category]['all'].append(item[0])
                self.brand[category]['synonym'][item[0]] = [item[0]]
                if item[2] is not None:
                    list_temp = item[2].splitlines()
                    self.brand[category]['all'] += list_temp
                    self.brand[category]['extra'] += list_temp
                    self.brand[category]['synonym'][item[0]] += list_temp
                    for brand in list_temp:
                        self.brand[category]['belong'][brand] = item[0]
        for item in self.__data['color']:
            self.color['main'].append(item[0])
            self.color['all'].append(item[0])
            self.color['title'].append(item[0].title())
            self.color['synonym'][item[0]] = [item[0]]
            if item[1] is not None:
                list_temp = item[1].splitlines()
                self.color['all'] += list_temp
                self.color['extra'] += list_temp
                self.color['synonym'][item[0]] += list_temp
                for temp in list_temp:
                    self.color['title'].append(temp.title())
                    self.color['belong'][temp] = item[0]
        for item in self.__data['size']:
            for category in item[2].splitlines():
                for audience in item[1].splitlines():
                    if audience not in self.size[category].keys():
                        self.size[category][audience] = {'main': [], 'all': [], 'extra': [], 'synonym': {},
                                                         'belong': {}}
                    self.size[category][audience]['main'].append(item[0])
                    self.size[category][audience]['all'].append(item[0])
                    self.size[category][audience]['synonym'][item[0]] = [item[0]]
                    if item[3] is not None:
                        list_temp = item[3].splitlines()
                        self.size[category][audience]['all'] += list_temp
                        self.size[category][audience]['extra'] += list_temp
                        self.size[category][audience]['synonym'][item[0]] += list_temp
                        for temp in list_temp:
                            self.size[category][audience]['belong'][temp] = item[0]
        for item in self.__data['plural']:
            self.plural[item[0]] = item[1]
        self.plural['reverse'] = function.reverse_dict(self.plural)
        self.variation1, self.variation2, self.list_variation = {}, {}, {}
        self.deny, self.selling_rate = {}, {}
        for item in self.__data['keyword']:
            self.variation1[item[0]] = item[1]
            if item[1] == '颜色':
                self.list_variation[item[0]] = self.color['title']
            elif item[1] == '尺码':
                self.list_variation[item[0]] = self.size[item[0]]['none']['main']
            if item[2] is not None:
                self.variation2[item[0]] = item[2]
            if item[3] is None:
                self.deny[item[0]] = []
            else:
                self.deny[item[0]] = item[3].splitlines()
            self.selling_rate[item[0]] = item[4]
            self.type_synonym[item[0]] = [item[0]]
            if item[5] is not None:
                self.type_synonym[item[0]] += item[5].splitlines()
        cursor.callproc('get_no_use', (user, session))
        self.no_use = json.loads(cursor.fetchone()[0])
        cursor.callproc('get_category_index', (user, session))
        self.category_index = json.loads(cursor.fetchone()[0])
        self.index_category = function.reverse_dict(self.category_index)

    def simplify_split(self, keyword, category):
        list_word = keyword.split(' ')
        list_temp = []
        for word in list_word:
            if word in list(self.plural.keys()):
                list_temp.append(self.plural[word])
            elif word in self.brand[category]['extra']:
                list_temp.append(self.brand[category]['belong'][word])
            elif word in self.audisence['all']:
                temp = self.audisence['belong'][word]
                if temp in list(self.plural.keys()):
                    temp = self.plural[temp]
                list_temp.append(temp)
            elif word not in self.no_use:
                list_temp.append(word)
        return list_temp

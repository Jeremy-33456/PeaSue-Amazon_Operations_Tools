#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from object.basic import Basic
from function import function
from keywords import help


def frequency(text: str, category: str, basic: Basic, pb=None):
    list_hang = text.strip().split('\n')
    if list_hang[0].find('\t') == -1:
        list_keyword, list_power = [], []
        for hang in list_hang:
            list_keyword.append(help.prepare(hang, category))
            list_power.append(1)
    else:
        list_keyword, list_power = [], []
        for hang in list_hang:
            chip = hang.split('\t')
            list_keyword.append(help.prepare(chip[0], category))
            list_power.append(int(chip[1]))
    dict_plural = basic.plural
    list_keys = list(dict_plural.keys())
    list_values = list(dict_plural.values())
    dict_weight, dict_power = {}, {}
    for i in range(0, len(list_hang)):
        search_terms = list_keyword[i].strip()
        power = list_power[i]
        list_word = search_terms.split(' ')
        for word in list_word:
            if word in list_keys:
                try:
                    dict_weight[(dict_plural[word], word)] += power
                except KeyError:
                    dict_weight[(dict_plural[word], word)] = power
                word = dict_plural[word]
            else:
                if word in list_values:
                    try:
                        dict_weight[(word, word)] += power
                    except KeyError:
                        dict_weight[(word, word)] = power
            try:
                dict_power[word] += power
            except KeyError:
                dict_power[word] = power
        if pb:
            pb.setValue(int(i + 1 / len(list_hang) * 50))
    list_word = function.sort_dict_key(dict_power, True)
    list_all = []
    for i in range(0, len(list_word)):
        word = list_word[i][0]
        list_item = []
        for item in list(dict_weight.keys()):
            if item[0] == word:
                list_item.append(item)
        if len(list_item) > 1:
            if dict_weight[list_item[0]] > dict_weight[list_item[1]]:
                add = list_item[0][1]
            else:
                add = list_item[1][1]
        else:
            add = word
        list_all.append([add, dict_power[word]])
        if pb:
            pb.setValue(int(i + 1 / len(list_word) * 50) + 50)
    return list_all

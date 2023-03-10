#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from keywords import help
from function import function
from object.basic import Basic


def tear(text: str, category: str, basic: Basic, pb=None):
    list_row = text.strip().split('\n')
    if list_row[0].find('\t') == -1:
        list_keyword, list_power = [], []
        for row in list_row:
            list_keyword.append(help.prepare(row, category))
            list_power.append(1)
    else:
        list_keyword, list_power = [], []
        for row in list_row:
            chip = row.split('\t')
            list_keyword.append(help.prepare(chip[0], category))
            list_power.append(int(chip[1]))
    dict_power = {}
    dict_plural = basic.plural
    list_keys = list(dict_plural.keys())
    list_values = list(dict_plural.values())
    dict_line = {}
    for i in range(0, len(list_row)):
        search_terms = list_keyword[i].strip()
        power = list_power[i]
        list_word = search_terms.split(' ')
        for j in range(0, len(list_word) - 1):
            list_number = [[j, j+1], [j, j+2], [j, j+1, j+2], [j, j+1, j+3], [j, j+2, j+3], [j, j+1, j+2, j+3],
                           [j, j+2, j+3, j+4], [j, j+1, j+3, j+4], [j, j+1, j+2, j+4], [j, j+1, j+2, j+3, j+4],
                           [j, j+1, j+2, j+3, j+5], [j, j+1, j+2, j+4, j+5], [j, j+1, j+3, j+4, j+5],
                           [j, j+2, j+3, j+4, j+5]]
            try:
                for number_group in list_number:
                    temp, list_line = [], []
                    for number in number_group:
                        if list_word[number] in list_keys:
                            list_line.append([number_group.index(number), list_word[number]])
                            list_word[number] = dict_plural[list_word[number]]
                        else:
                            if list_word[number] in list_values:
                                list_line.append([number_group.index(number), list_word[number]])
                        temp.append(list_word[number])
                    keyword = function.connect(temp, ' ')
                    for item in list_line:
                        list_temp = [keyword]
                        for line in item:
                            list_temp.append(line)
                        try:
                            dict_line[tuple(list_temp)] += power
                        except KeyError:
                            dict_line[tuple(list_temp)] = power
                    try:
                        dict_power[keyword] += power
                    except KeyError:
                        dict_power[keyword] = power
            except IndexError:
                pass
        if pb:
            pb.setValue(int(i + 2 / len(list_row) * 25))
    list_keyword = function.sort_dict_key(dict_power, True)
    list_all = []
    for item in list_keyword:
        keyword = item[0]
        chip = keyword.split(' ')
        list_line = []
        for line in list(dict_line.keys()):
            if line[0] == keyword:
                list_line.append(line)
        dict_number = {}
        for line in list_line:
            try:
                dict_number[line[1]].append(line[2])
            except KeyError:
                dict_number[line[1]] = [line[2]]
        for number in list(dict_number.keys()):
            if len(dict_number[number]) == 1:
                chip[number] = dict_number[number][0]
            else:
                if dict_line[(keyword, number, dict_number[number][0])] > dict_line[
                        (keyword, number, dict_number[number][1])]:
                    chip[number] = dict_number[number][0]
                else:
                    chip[number] = dict_number[number][1]
        keyword = function.connect(chip, ' ')
        power = item[1]
        number = keyword.count(' ') + 1
        list_all.append([number, keyword, power])
        if pb:
            pb.setValue(int(list_keyword.index(item) + 1 / len(list_keyword) * 25) + 25)
    return list_all

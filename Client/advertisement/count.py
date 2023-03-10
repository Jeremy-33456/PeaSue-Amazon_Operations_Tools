#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from function import function
from object.basic import Basic


def count_data(list_date: list, list_select: list, choice: str, dict_attach: dict, basic: Basic):
    list_all, list_sales, list_point = [], [], []
    list_temp, number = [], len(list(dict_attach.values())[0])
    for select in list_select:
        list_temp.append('%s|%s' % (select[0], select[1]))
    selects = function.connect(list_temp, ',')
    if choice == '调价-总览':
        dates = function.connect(list_date, ',')
        dict_match = {}
        for key in dict_attach.keys():
            try:
                dict_match[dict_attach[key][0]].append(key)
            except KeyError:
                dict_match[dict_attach[key][0]] = [key]
        for key in dict_match.keys():
            selects_temp = function.connect(dict_match[key], ',')
            temp = basic.get_targeting_ignore(selects_temp, dates)
            if temp:
                for item in temp:
                    list_all.append([key] + list(item)[0: -1])
                    list_sales.append(item[-1])
        temp = basic.get_targeting_all(selects, dates)
        list_all.append(['All', 'All'] + list(temp)[0: -1])
        list_sales.append(temp[-1])
        list_point.append(len(list_all) - 1)
    elif choice == '调价-一览':
        dates = function.connect(list_date, ',')
        temp = basic.get_targeting_sum(selects, dates)
        if temp:
            for item in temp:
                temp = '%s|%s' % (item[0], item[1])
                list_all.append(dict_attach[temp].copy() + list(item)[2: -1])
                list_sales.append(item[-1])
            temp = basic.get_targeting_all(selects, dates)
            list_temp = []
            for i in range(0, number + 1):
                list_temp.append('All')
            list_temp += list(temp)[0: -1]
            list_all.append(list_temp)
            list_sales.append(temp[-1])
            list_point.append(len(list_all) - 1)
    elif choice == '调价-每日':
        for date in list_date:
            temp = basic.get_targeting_detail(selects, date)
            if temp:
                for item in temp:
                    temp = '%s|%s' % (item[0], item[1])
                    list_temp = dict_attach[temp].copy() + list(item)[2: -1]
                    list_temp.insert(0, date)
                    list_all.append(list_temp)
                    list_sales.append(item[-1])
                temp = basic.get_targeting_all(selects, date)
                list_temp = [date]
                for i in range(0, number + 1):
                    list_temp.append('All')
                list_temp += list(temp)[0: -1]
                list_all.append(list_temp)
                list_sales.append(temp[-1])
                list_point.append(len(list_all) - 1)
    elif choice == '关键词-总览':
        dates = function.connect(list_date, ',')
        temp = basic.get_search_terms_ignore(selects, dates)
        if temp:
            for item in temp:
                list_all.append(list(item)[0: -1])
                list_sales.append(item[-1])
            temp = basic.get_search_terms_all(selects, dates)
            list_all.append(['All'] + list(temp)[0: -1])
            list_sales.append(temp[-1])
            list_point.append(len(list_all) - 1)
    elif choice == '关键词-一览':
        dates = function.connect(list_date, ',')
        temp = basic.get_search_terms_sum(selects, dates)
        if temp:
            for item in temp:
                temp = '%s|%s' % (item[0], item[1])
                list_all.append(dict_attach[temp].copy() + list(item)[2: -1])
                list_sales.append(item[-1])
            temp = basic.get_search_terms_all(selects, dates)
            list_temp = []
            for i in range(0, number + 2):
                list_temp.append('All')
            list_temp += list(temp)[0: -1]
            list_all.append(list_temp)
            list_sales.append(temp[-1])
            list_point.append(len(list_all) - 1)
    return list_all, list_sales, list_point


def sort_by_header(list_content: list, list_sales: list, list_keyword: list, list_match: list, header: list,
                   category: str, basic: Basic):
    list_all, temp = [], [0, 0, 0, 0, 0]
    if '日期' in header:
        index = header.index('投放')
        for i in range(0, len(list_content)):
            if list_content[i][index] == 'All':
                list_all.append([list_content[i][0]] + list_content[i][-8:])
                temp[0] += int(list_content[i][index + 1])
                temp[1] += int(list_content[i][index + 2])
                temp[2] += int(list_content[i][index + 5])
                temp[3] += float(list_content[i][index + 6])
                temp[4] += list_sales[i]
        if temp[0] == 0:
            ctr = ''
        else:
            ctr = '{:.2%}'.format(temp[1] / temp[0])
        if temp[1] == 0:
            cpc, cvr = '', ''
        else:
            cpc = str(round(temp[3] / temp[1], 2))
            cvr = '{:.2%}'.format(temp[2] / temp[1])
        if temp[4] == 0:
            acos = ''
        else:
            acos = '{:.2%}'.format(temp[3] / temp[4])
        temp_list = ['All', str(temp[0]), str(temp[1]), ctr, cpc, str(temp[2]), str(round(temp[3], 2)), cvr, acos]
        list_all.append(temp_list)
    else:
        if header[0] in ['投放', '关键词']:
            index, list_phrase = 0, []
        else:
            index, list_phrase = 1, list(set([item[0] for item in list_content]))
        temp_all, list_exist = [0, 0, 0, 0, 0], []
        for i in range(0, len(list_keyword)):
            temp = [0, 0, 0, 0, 0]
            list_word = basic.simplify_split(list_keyword[i][-1], category)
            if list_match[i] == 'Broad':
                list_word.sort()
            number = len(list_keyword[i])
            for j in range(0, len(list_content)):
                judge = True
                if number == 2 and index == 1 and list_keyword[i][0] in list_phrase:
                    judge = list_keyword[i][0] == list_content[j][0]
                elif number == 1 and index == 1:
                    judge = list_match[i] == list_content[j][0]
                if judge:
                    list_temp = basic.simplify_split(list_content[j][index], category)
                    if header[index] == '投放':
                        if list_match[i] == 'Broad':
                            list_temp.sort()
                            result = list_temp == list_word
                        elif list_match[i] in ['Phrase', 'Exact']:
                            result = list_temp == list_word
                        else:
                            result = list_keyword[i][-1] == list_content[j][index]
                    else:
                        if list_match[i] == 'Broad':
                            result = True
                            for keyword_temp in list_word:
                                if keyword_temp not in list_temp:
                                    result = False
                                    break
                        elif list_match[i] == 'Phrase':
                            result = function.connect(list_word, ' ') in function.connect(list_temp, ' ')
                        elif list_match[i] == 'Exact':
                            result = list_temp == list_word
                        elif list_match[i] in ['PT', 'CT']:
                            result = list_keyword[i][-1] == list_content[j][index].upper()
                        else:
                            result = False
                    if result:
                        temp[0] += int(list_content[j][index + 1])
                        temp[1] += int(list_content[j][index + 2])
                        temp[2] += int(list_content[j][index + 5])
                        temp[3] += float(list_content[j][index + 6])
                        temp[4] += list_sales[j]
                        if j not in list_exist:
                            temp_all[0] += int(list_content[j][index + 1])
                            temp_all[1] += int(list_content[j][index + 2])
                            temp_all[2] += int(list_content[j][index + 5])
                            temp_all[3] += float(list_content[j][index + 6])
                            temp_all[4] += list_sales[j]
                            list_exist.append(j)
            if temp[0] == 0:
                ctr = ''
            else:
                ctr = '{:.2%}'.format(temp[1] / temp[0])
            if temp[1] == 0:
                cpc, cvr = '', ''
            else:
                cpc = str(round(temp[3] / temp[1], 2))
                cvr = '{:.2%}'.format(temp[2] / temp[1])
            if temp[4] == 0:
                acos = ''
            else:
                acos = '{:.2%}'.format(temp[3] / temp[4])
            temp_list = list_keyword[i] + [str(temp[0]), str(temp[1]), ctr, cpc, str(temp[2]), str(round(temp[3], 2)),
                                           cvr, acos]
            list_all.append(temp_list)
        if temp_all[0] == 0:
            ctr = ''
        else:
            ctr = '{:.2%}'.format(temp_all[1] / temp_all[0])
        if temp_all[1] == 0:
            cpc, cvr = '', ''
        else:
            cpc = str(round(temp_all[3] / temp_all[1], 2))
            cvr = '{:.2%}'.format(temp_all[2] / temp_all[1])
        if temp_all[4] == 0:
            acos = ''
        else:
            acos = '{:.2%}'.format(temp_all[3] / temp_all[4])
        temp_list = []
        for i in range(0, len(list_keyword[0])):
            temp_list.append('All')
        temp_list += [str(temp_all[0]), str(temp_all[1]), ctr, cpc, str(temp_all[2]), str(round(temp_all[3], 2)),
                      cvr, acos]
        list_all.append(temp_list)
    return list_all


def get_bid(campaign: str, group: str, keyword_bid: dict):
    list_bid = []
    for item in list(keyword_bid[campaign].keys()):
        if group == 'All':
            for keyword in list(keyword_bid[campaign][item].keys()):
                list_bid.append([item, keyword, str(keyword_bid[campaign][item][keyword])])
        elif item == group:
            for keyword in list(keyword_bid[campaign][item].keys()):
                list_bid.append([keyword, str(keyword_bid[campaign][item][keyword])])
    return list_bid

#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
from function import function
from object.basic import Basic


def count_storage(name: str, header: list, variation: str, basic: Basic, variation1: str, variation2: str):
    dict_discount = basic.discount
    list_all = []
    if ',' not in name:
        dict_sign = basic.get_sign(name)
        list_sign = []
        for sign in dict_sign.values():
            if variation == 'All' or variation == sign.split('|')[0].title():
                list_sign.append(sign)
        text_sign = function.connect(list_sign, ',')
        dict_child = function.reverse_dict(dict_sign)
        list_temp = basic.get_storage_detail(name, text_sign)
        all_discount, all_coupon = 0, []
        for i in range(0, len(list_temp)):
            sign = list_temp[i][0]
            child = dict_child[sign]
            chip = sign.split('|')
            temp = [child]
            if variation1 in header:
                temp.append(chip[0].title())
            if variation2 in header:
                temp.append(chip[1].title())
            temp.append(float(list_temp[i][1]))
            if (name, sign) in list(dict_discount.keys()):
                coupon = dict_discount[(name, sign)][1]
                if coupon < 1:
                    discount = '{:.0%}'.format(coupon)
                    price = round(float(list_temp[i][1]) * (1 - coupon), 2)
                else:
                    discount = coupon
                    price = round(float(list_temp[i][1]) - coupon, 2)
                style = dict_discount[(name, sign)][0]
            else:
                discount, style = '', ''
                price = float(list_temp[i][1])
            temp.append(style)
            if style not in all_coupon:
                all_coupon.append(style)
            temp.append(discount)
            all_discount += (float(list_temp[i][1]) - price) * list_temp[i][5]
            temp.append(price)
            temp += list(list_temp[i])[2:]
            list_all.append(temp)
        list_temp = list(basic.get_storage_sum(name, text_sign))
        if all_discount == 0 or list_temp[4] == 0:
            discount = ''
        else:
            discount = round(all_discount / float(list_temp[4]), 2)
        if discount == '':
            per = ''
        else:
            per = '{:.0%}'.format(discount / float(list_temp[0]))
        if discount == '':
            if list_temp[0] == '':
                real = ''
            else:
                real = float(list_temp[0])
        else:
            real = round(float(list_temp[0]) - discount, 2)
        if len(all_coupon) > 1:
            coupon_temp = '混合'
        elif len(all_coupon) == 1:
            coupon_temp = all_coupon[0]
        else:
            coupon_temp = ''
        list_temp = ['All', list_temp[0], coupon_temp, per, real] + list(list_temp)[1:]
        if variation2 in header:
            list_temp.insert(1, 'All')
        if variation1 in header:
            list_temp.insert(1, 'All')
        list_all.append(list_temp)
    else:
        list_temp = basic.get_storage_sort(name)
        all_discount, all_coupon = 0, []
        for i in range(0, len(list_temp)):
            temp_discount, temp_coupon = 0, []
            product = list_temp[i][0]
            temp = [product, list_temp[i][2]]
            for item in list_temp[i][1].split(','):
                chip = item.split('#')
                sign = chip[0]
                price = float(chip[1])
                warehouse = int(chip[2])
                if (product, sign) in list(dict_discount.keys()):
                    coupon = dict_discount[(product, sign)][1]
                    if coupon < 1:
                        discount = coupon * price
                    else:
                        discount = coupon
                    style = dict_discount[(product, sign)][0]
                    if style not in temp_coupon:
                        temp_coupon.append(style)
                    if style not in all_coupon:
                        all_coupon.append(style)
                    temp_discount += discount * warehouse
            temp.append(function.connect(temp_coupon, '&'))
            all_discount += temp_discount
            if temp_discount == 0 or list_temp[i][6] == 0:
                discount = ''
            else:
                discount = round(temp_discount / float(list_temp[i][6]), 2)
            if discount == '':
                per = ''
            else:
                per = '{:.0%}'.format(discount / float(list_temp[i][2]))
            temp.append(per)
            if discount == '':
                if list_temp[0] == '':
                    real = ''
                else:
                    real = float(list_temp[i][2])
            else:
                real = round(float(list_temp[i][2]) - discount, 2)
            temp.append(real)
            temp += list(list_temp[i])[3:]
            list_all.append(temp)
        list_temp = list(basic.get_storage_all(name))
        if all_discount == 0 or list_temp[4] == 0:
            discount = ''
        else:
            discount = round(all_discount / float(list_temp[4]), 2)
        if discount == '':
            per = ''
        else:
            per = '{:.0%}'.format(discount / float(list_temp[0]))
        if discount == '':
            if list_temp[0] == '':
                real = ''
            else:
                real = float(list_temp[0])
        else:
            real = round(float(list_temp[0]) - discount, 2)
        if len(all_coupon) > 1:
            coupon_temp = '混合'
        elif len(all_coupon) == 1:
            coupon_temp = all_coupon[0]
        else:
            coupon_temp = ''
        list_temp = ['All', list_temp[0], coupon_temp, per, real] + list(list_temp)[1:]
        list_all.append(list_temp)
    return list_all


def count_data(choice: str, list_date: list, list_child: list, data_temp: dict, list_storage: list):
    list_all = []
    if choice == '补货':
        orders = 0
        for row in range(0, len(list_child)):
            temp = [list_child[row], data_temp['orders'][list_child[row]], '', '']
            orders += data_temp['orders'][list_child[row]]
            list_all.append(temp)
        list_all.append(['All', orders, '', ''])
        return list_all
    elif choice == '退货率':
        orders = 0
        refund = 0
        for row in range(0, len(list_child)):
            if data_temp['orders'][list_child[row]] > 0:
                rate = '{:.2%}'.format(data_temp['refund'][list_child[row]] / data_temp['orders'][list_child[row]])
            else:
                rate = ''
            temp = [list_child[row], data_temp['orders'][list_child[row]], data_temp['refund'][list_child[row]], rate]
            orders += data_temp['orders'][list_child[row]]
            refund += data_temp['refund'][list_child[row]]
            list_all.append(temp)
        if orders > 0:
            rate = '{:.2%}'.format(refund / orders)
        else:
            rate = ''
        list_all.append(['All', orders, refund, rate])
        return list_all
    else:
        orders = 0
        for row in range(0, len(list_child)):
            orders += data_temp['orders'][list_child[row]]
            if data_temp['orders'][list_child[row]] > 0:
                rate1 = round(list_storage[0][row] / data_temp['orders'][list_child[row]] * len(list_date), 1)
                rate2 = round(list_storage[1][row] / data_temp['orders'][list_child[row]] * len(list_date), 1)
            else:
                rate1 = ''
                rate2 = ''
            temp = [list_child[row], data_temp['orders'][list_child[row]], rate1, rate2]
            list_all.append(temp)
        if orders > 0:
            rate1 = round(list_storage[0][-1] / orders * len(list_date), 1)
            rate2 = round(list_storage[1][-1] / orders * len(list_date), 1)
        else:
            rate1 = ''
            rate2 = ''
        list_all.append(['All', orders, rate1, rate2])
        return list_all


def read_performance(name: str, list_date: list, basic: Basic):
    dates = function.connect(list_date, ',')
    if ',' not in name:
        list_all = list(basic.get_performance_detail(name, dates))
        list_temp = list(basic.get_performance_sum(name, dates))
        list_temp.insert(0, '总计')
        list_temp += ['', '', '']
        list_all.append(list_temp)
    else:
        list_all = []
        for product in name.split(','):
            temp = basic.get_performance_sum(product, dates)
            if temp[0] is not None:
                list_temp = list(temp)
                list_temp.insert(0, product)
                temp = basic.get_crawl(product, dates)
                if len(temp) == 0:
                    list_crawl = ['', '', '']
                else:
                    list_crawl = list(temp[-1])[3:]
                list_temp += list_crawl
                list_all.append(list_temp)
        temp = list(basic.get_performance_sum(name, dates)) + ['', '', '']
        temp.insert(0, '总计')
        list_all.append(temp)
    return list_all


def read_crawl(name: str, list_date: list, basic: Basic):
    list_all = []
    list_keyword = basic.get_search(name)
    if len(list_keyword) == 0:
        mode = 1
    else:
        mode = 2
    list_temp = basic.get_crawl(name, function.connect(list_date, ','))
    data = {}
    for date in list_date:
        for temp in list_temp:
            if temp[0] == date:
                if mode == 2:
                    for keyword in list_keyword:
                        try:
                            data['%s|%s|nature' % (date, keyword)] = json.loads(temp[1])[keyword]
                        except KeyError:
                            pass
                        try:
                            data['%s|%s|sponsored' % (date, keyword)] = json.loads(temp[2])[keyword]
                        except KeyError:
                            pass
                    break
                else:
                    for keyword in json.loads(temp[1]).keys():
                        data['%s|%s|nature' % (date, keyword)] = json.loads(temp[1])[keyword]
                        if keyword not in list_keyword:
                            list_keyword.append(keyword)
                    for keyword in json.loads(temp[2]).keys():
                        data['%s|%s|sponsored' % (date, keyword)] = json.loads(temp[2])[keyword]
                        if keyword not in list_keyword:
                            list_keyword.append(keyword)
    for keyword in list_keyword:
        temp1 = [keyword, '自然']
        temp2 = [keyword, '广告']
        for date in list_date:
            try:
                if data['%s|%s|nature' % (date, keyword)]:
                    temp_nature = data['%s|%s|nature' % (date, keyword)]
                else:
                    temp_nature = 'None'
                temp1.append(temp_nature)
            except KeyError:
                temp1.append('')
            try:
                if data['%s|%s|sponsored' % (date, keyword)]:
                    temp_sponsored = data['%s|%s|sponsored' % (date, keyword)]
                else:
                    temp_sponsored = 'None'
                temp2.append(temp_sponsored)
            except KeyError:
                temp2.append('')
        list_all.append(temp1)
        list_all.append(temp2)
    return list_all


def read_profit(name: str, list_date: list, basic: Basic):
    dates = function.connect(list_date, ',')
    if ',' not in name:
        list_all = list(basic.get_profit_detail(name, dates))
        list_temp = list(basic.get_profit_sum(name, dates))
        list_temp.insert(0, '总计')
        list_all.append(list_temp)
    else:
        list_all = []
        for product in name.split(','):
            temp = basic.get_profit_sum(product, dates)
            if temp[0] is not None:
                list_temp = list(temp)
                list_temp.insert(0, product)
                list_all.append(list_temp)
        temp = list(basic.get_profit_sum(name, dates))
        temp.insert(0, '总计')
        list_all.append(temp)
    return list_all

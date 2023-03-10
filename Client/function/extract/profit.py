#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import os
import json
import pandas
import datetime
from object.basic import Basic
from function import function
from PyQt5.QtCore import pyqtSignal


def main(basic: Basic, printer: pyqtSignal):
    list_date = []
    dict_quantity, dict_sales, dict_selling, dict_fba, dict_coupon, dict_other = {}, {}, {}, {}, {}, {}
    dict_refund, dict_adjust, dict_storage, dict_ad, dict_disposal = {}, {}, {}, {}, {}
    dict_price, dict_transport, dict_return = {}, {}, {}
    for store in basic.store_all:
        printer.emit('正在读取%s店文件' % store)
        data_drr = pandas.read_csv('%s/Profit/date range report.csv' % basic.path[store], header=7)
        data_sp = pandas.read_csv('%s/Profit/ad fee - SP.csv' % basic.path[store])
        data_sb = pandas.read_excel('%s/Profit/ad fee - SB.xlsx' % basic.path[store], sheet_name=0)
        data_sd = pandas.read_excel('%s/Profit/ad fee - SD.xlsx' % basic.path[store], sheet_name=0)
        data_dp = function.open_txt_as_chart('%s/Profit/Orders/removal.txt' % basic.path[store], '\t')
        list_name = basic.name_in_store(store)
        dict_sign, dict_child, dict_belong = {}, {}, {}
        for name in list_name:
            if basic.is_gm(name):
                name = basic.get_origin(name)
                dict_temp = basic.get_sign_gm(name, store)
            else:
                dict_temp = basic.get_sign(name)
            dict_temp.update(basic.get_change(name))
            dict_child[name] = dict_temp.copy()
            for sku in dict_temp.keys():
                dict_belong[sku] = name
            dict_sign.update(dict_temp)
        list_child = list(dict_sign.keys())
        dict_order = {'Retrocharge': {}, 'Return_fee': {}, 'Adjust': {}}
        dict_disposal_temp = {}
        list_date_temp = []
        printer.emit('正在整理利润文件')
        for i in range(0, len(data_drr['type'])):
            chip = data_drr['date/time'][i].split(' ')
            month = datetime.datetime.strptime(chip[0], '%b').strftime('%m')
            day = '%02d' % int(chip[1].replace(',', ''))
            date = '%s.%s.%s' % (chip[2], month, day)
            if date not in list_date:
                list_date.append(date)
            if date not in list_date_temp:
                list_date_temp.append(date)
            if pandas.isnull(data_drr['sku'][i]):
                sku = ''
            else:
                sku = data_drr['sku'][i]
            if data_drr['type'][i] == 'Order':
                if sku in list_child:
                    name = dict_belong[sku]
                    try:
                        dict_quantity[(date, name)] += int(data_drr['quantity'][i])
                    except KeyError:
                        dict_quantity[(date, name)] = int(data_drr['quantity'][i])
                    sales = float(data_drr['product sales'][i]) + float(data_drr['product sales tax'][i])
                    try:
                        dict_sales[(date, name)] += sales
                    except KeyError:
                        dict_sales[(date, name)] = sales
                    coupon = float(data_drr['promotional rebates'][i]) + float(data_drr['promotional rebates tax'][i])
                    try:
                        dict_coupon[(date, name)] += coupon
                    except KeyError:
                        dict_coupon[(date, name)] = coupon
                    selling = float(data_drr['selling fees'][i])
                    try:
                        dict_selling[(date, name)] += selling
                    except KeyError:
                        dict_selling[(date, name)] = selling
                    fba = float(data_drr['fba fees'][i])
                    try:
                        dict_fba[(date, name)] += fba
                    except KeyError:
                        dict_fba[(date, name)] = fba
                    summary = sales + coupon + selling + fba
                    try:
                        dict_other[(date, name)] += float(data_drr['total'][i]) - summary
                    except KeyError:
                        dict_other[(date, name)] = float(data_drr['total'][i]) - summary
                    fee_temp = basic.get_price(name, sku)
                    try:
                        dict_price[(date, name)] += int(data_drr['quantity'][i]) * fee_temp[0] * -1
                    except KeyError:
                        dict_price[(date, name)] = int(data_drr['quantity'][i]) * fee_temp[0] * -1
                    try:
                        dict_transport[(date, name)] += int(data_drr['quantity'][i]) * fee_temp[1] * -1
                    except KeyError:
                        dict_transport[(date, name)] = int(data_drr['quantity'][i]) * fee_temp[1] * -1
            elif data_drr['type'][i] == 'Order_Retrocharge':
                try:
                    dict_order['Retrocharge'][(date, data_drr['order id'][i])] += float(data_drr['total'][i])
                except KeyError:
                    dict_order['Retrocharge'][(date, data_drr['order id'][i])] = float(data_drr['total'][i])
            elif data_drr['type'][i] == 'Refund':
                if sku in list_child:
                    name, sign = dict_belong[sku], dict_sign[sku]
                    try:
                        dict_refund[(date, name)] += float(data_drr['total'][i])
                    except KeyError:
                        dict_refund[(date, name)] = float(data_drr['total'][i])
                    try:
                        dict_return[(date, name, sign)] += int(data_drr['quantity'][i])
                    except KeyError:
                        dict_return[(date, name, sign)] = int(data_drr['quantity'][i])
            elif data_drr['type'][i] == 'FBA Customer Return Fee':
                if data_drr['total'][i] != 0:
                    try:
                        dict_order['Return_fee'][(date, data_drr['order id'][i])] += float(data_drr['total'][i])
                    except KeyError:
                        dict_order['Return_fee'][(date, data_drr['order id'][i])] = float(data_drr['total'][i])
            elif data_drr['type'][i] == 'Adjustment':
                if sku in list_child:
                    name = dict_belong[sku]
                    try:
                        dict_adjust[(date, name)] += float(data_drr['total'][i])
                    except KeyError:
                        dict_adjust[(date, name)] = float(data_drr['total'][i])
            elif data_drr['type'][i] == 'Fee Adjustment':
                try:
                    dict_order['Adjust'][(date, data_drr['order id'][i])] += float(data_drr['total'][i])
                except KeyError:
                    dict_order['Adjust'][(date, data_drr['order id'][i])] = float(data_drr['total'][i])
            elif data_drr['type'][i] == 'FBA Inventory Fee':
                if data_drr['description'][i] == 'FBA Removal Order: Disposal Fee':
                    order = data_drr['order id'][i]
                    if order not in list(dict_disposal_temp.keys()):
                        dict_disposal_temp[order] = date
            elif pandas.isnull(data_drr['type'][i]):
                if 'Early Reviewer Program fee for asin' in data_drr['description'][i]:
                    asin = data_drr['description'][i].replace('Early Reviewer Program fee for asin', '').strip()
                    name = function.reverse_dict(basic.asin)[asin]
                    try:
                        dict_other[(date, name)] += float(data_drr['total'][i])
                    except KeyError:
                        dict_other[(date, name)] = float(data_drr['total'][i])
                else:
                    result = function.find_one(data_drr['description'][i], list_name)
                    if result[0]:
                        try:
                            dict_coupon[(date, result[1])] += float(data_drr['total'][i])
                        except KeyError:
                            dict_coupon[(date, result[1])] = float(data_drr['total'][i])
        printer.emit('正在整理广告文件')
        for data in [data_sp, data_sb, data_sd]:
            for i in range(0, len(data['广告活动名称'])):
                try:
                    chip = data['日期'][i].split(' ')
                    month = datetime.datetime.strptime(chip[0], '%b').strftime('%m')
                    day = '%02d' % int(chip[1].replace(',', ''))
                    date = '%s.%s.%s' % (chip[2], month, day)
                except AttributeError:
                    date = str(data['日期'][i])[0: 10].replace('-', '.')
                result = function.find_one(data['广告活动名称'][i], list_name)
                if result[0]:
                    if basic.is_gm(result[1]):
                        temp = basic.get_origin(result[1])
                    else:
                        temp = result[1]
                    try:
                        dict_ad[(date, temp)] += float(str(data['花费'][i]).replace('$', '')) * -1
                    except KeyError:
                        dict_ad[(date, temp)] = float(str(data['花费'][i]).replace('$', '')) * -1
        month = []
        for date in list_date_temp:
            temp = '%s_%d' % (date[0: 4], int(date[5: 7]))
            if temp not in month:
                month.append(temp)
        dict_asin = {}
        for name in list_name:
            if basic.is_gm(name):
                name = basic.get_origin(name)
            for sku in list(dict_child[name].keys()):
                dict_asin[basic.get_asin(name)[sku]] = name
        printer.emit('正在整理仓储文件')
        for item in month:
            chip = item.split('_')
            if chip[1] == '1':
                temp = '%d_12' % (int(chip[0]) - 1)
            else:
                temp = '%s_%d' % (chip[0], int(chip[1]) - 1)
            a = {'1': 31, '3': 31, '4': 30, '5': 31, '6': 30, '7': 31, '8': 31, '9': 30, '10': 31, '11': 30, '12': 31}
            if int(chip[0]) % 4 == 0:
                a['2'] = 29
            else:
                a['2'] = 28
            day = a[chip[1]]
            data = function.open_txt_as_chart('%s/Storage/storage fee_%s.txt' % (basic.path[store], temp), '\t')
            dict_fee = {}
            for i in range(0, len(data['asin'])):
                asin = data['asin'][i]
                if asin in dict_asin.keys():
                    try:
                        dict_fee[dict_asin[asin]] += float(data['estimated_monthly_storage_fee'][i])
                    except KeyError:
                        dict_fee[dict_asin[asin]] = float(data['estimated_monthly_storage_fee'][i])
            for name in list_name:
                if basic.is_gm(name):
                    name = basic.get_origin(name)
                try:
                    dict_storage['%s_%s' % (chip[0], chip[1].zfill(2)), name] += dict_fee[name] / day * -1
                except KeyError:
                    dict_storage['%s_%s' % (chip[0], chip[1].zfill(2)), name] = dict_fee[name] / day * -1
        list_order = []
        for key in list(dict_order.keys()):
            for item in list(dict_order[key].keys()):
                order = item[1]
                if order not in list_order:
                    list_order.append(order)
        list_file = os.listdir('%s/Profit/Orders' % basic.path[store])
        list_file.sort(reverse=True)
        list_file.remove('removal.txt')
        dict_name = {}
        printer.emit('正在整理订单文件')
        for file in list_file:
            data = function.open_txt_as_chart('%s/Profit/Orders/%s' % (basic.path[store], file), '\t')
            for i in range(0, len(data['amazon-order-id'])):
                order = data['amazon-order-id'][i]
                sku = data['sku'][i]
                if order in list_order:
                    list_order.remove(order)
                    if sku in list_child:
                        dict_name[order] = dict_belong[sku]
                    else:
                        dict_name[order] = 'other'
                    if len(list_order) == 0:
                        break
            if len(list_order) == 0:
                break
        if len(list_order) > 0:
            raise ValueError('未找到订单：%s' % function.connect(list_order, ', '))
        for key in list(dict_order.keys()):
            for item in list(dict_order[key].keys()):
                date = item[0]
                name = dict_name[item[1]]
                if name in list_name:
                    if basic.is_gm(name):
                        name = basic.get_origin(name)
                    if key == 'Retrocharge':
                        try:
                            dict_adjust[date, name] += dict_order[key][item]
                        except KeyError:
                            dict_adjust[date, name] = dict_order[key][item]
                    elif key == 'Return_fee':
                        try:
                            dict_refund[date, name] += dict_order[key][item]
                        except KeyError:
                            dict_refund[date, name] = dict_order[key][item]
                    else:
                        try:
                            dict_adjust[date, name] += dict_order[key][item]
                        except KeyError:
                            dict_adjust[date, name] = dict_order[key][item]
        list_exist = []
        printer.emit('正在整理弃置文件')
        for i in range(0, len(data_dp['order-id'])):
            order = data_dp['order-id'][i]
            if order in list(dict_disposal_temp.keys()):
                if order not in list_exist:
                    list_exist.append(order)
                sku = data_dp['sku'][i]
                if sku in list_child:
                    date = dict_disposal_temp[order]
                    name = dict_belong[sku]
                    if not pandas.isnull(data_dp['removal-fee'][i]):
                        try:
                            dict_disposal[date, name] += float(data_dp['removal-fee'][i]) * -1
                        except KeyError:
                            dict_disposal[date, name] = float(data_dp['removal-fee'][i]) * -1
                    try:
                        dict_quantity[date, name] += float(data_dp['disposed-quantity'][i])
                    except KeyError:
                        dict_quantity[date, name] = float(data_dp['disposed-quantity'][i])
        if len(list_exist) < len(dict_disposal_temp):
            list_lack = function.find_add_delete(list(dict_disposal_temp.keys()), list_exist)[2]
            raise(ValueError('未找到订单号：%s' % function.connect(list_lack, ', ')))
    for name in basic.product_list:
        printer.emit('正在汇总%s的数据' % name)
        for date in list_date:
            try:
                temp = basic.get_child_data(name, date)
                dict_orders = json.loads(temp[0])
            except TypeError:
                dict_orders = {}
            dict_refunds = {}
            dict_temp = basic.get_sign(name)
            for sku in list(dict_temp.keys()):
                try:
                    dict_refunds[dict_temp[sku]] = dict_return[date, name, dict_temp[sku]]
                except KeyError:
                    dict_refunds[dict_temp[sku]] = 0
            text_orders = json.dumps(dict_orders)
            text_refund = json.dumps(dict_refunds)
            basic.update_child_data(name, date, text_orders, text_refund)
        for date in list_date:
            try:
                quantity = dict_quantity[date, name]
            except KeyError:
                quantity = 0
            try:
                sales = dict_sales[date, name]
            except KeyError:
                sales = 0
            try:
                selling = dict_selling[date, name]
            except KeyError:
                selling = 0
            try:
                fba = dict_fba[date, name]
            except KeyError:
                fba = 0
            try:
                coupon = dict_coupon[date, name]
            except KeyError:
                coupon = 0
            try:
                refund = dict_refund[date, name]
            except KeyError:
                refund = 0
            try:
                adjust = dict_adjust[date, name]
            except KeyError:
                adjust = 0
            try:
                advertisement = dict_ad[date, name]
            except KeyError:
                advertisement = 0
            try:
                storage = dict_storage[date[0: 7].replace('.', '_'), name]
            except KeyError:
                storage = 0
            try:
                disposal = dict_disposal[date, name]
            except KeyError:
                disposal = 0
            try:
                other = dict_other[date, name]
            except KeyError:
                other = 0
            try:
                price = dict_price[date, name]
            except KeyError:
                price = 0
            try:
                transport = dict_transport[date, name]
            except KeyError:
                transport = 0
            basic.update_profit(name, date, quantity, sales, selling, fba, coupon, refund, adjust, advertisement,
                                storage, disposal, other, price, transport)
    basic.commit()


def extract_profit(basic: Basic, printer: pyqtSignal):
    try:
        main(basic, printer)
        printer.emit('成功导入利润数据')
    except Exception as ex:
        printer.emit('导入利润数据失败：%s' % ex)

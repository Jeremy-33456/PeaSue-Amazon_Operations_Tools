#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM
import json
import os
import pandas
from object.basic import Basic
from function import function
from PyQt5.QtCore import pyqtSignal


def main(basic: Basic, printer: pyqtSignal):
    dict_coupon = basic.coupon
    dict_asin = basic.asin
    list_delete_all = []
    for name in basic.product_list:
        printer.emit('正在整理%s的数据' % name)
        store = basic.get_store(name)
        path = basic.path[store]
        dict_fba = {}
        selling_rate = basic.selling_rate[basic.get_category(name)]
        refund_rate = basic.get_information(name)['refund']
        storage_fee = 0
        for item in basic.get_storage_single(name):
            dict_fba[item[2]] = json.loads(item[3])
            storage_fee += item[13]
        for file in os.listdir(path + '/Performance'):
            if file[-4:] == '.txt' and file[0: 2] == '20':
                list_delete, delete = [], False
                dict_child = basic.get_sign(name)
                dict_fee = {}
                for item in list(dict_child.keys()):
                    temp_fee = basic.get_price(name, item)
                    dict_fee[item] = float(temp_fee[0]) + float(temp_fee[1])
                store = basic.get_store(name)
                path = basic.path[store]
                date = file[0: 10]
                yr = file[2: 4]
                year = file[0: 4]
                month = str(int(file[5: 7]))
                day = str(int(file[8: 10]))
                a = {'1': 31, '3': 31, '4': 30, '5': 31, '6': 30, '7': 31, '8': 31,
                     '9': 30, '10': 31, '11': 30, '12': 31}
                if int(year) % 4 == 0:
                    a['2'] = 29
                else:
                    a['2'] = 28
                try:
                    temp = basic.get_child_data(name, date)
                    dict_refund = json.loads(temp[1])
                except TypeError:
                    dict_refund = {}
                dict_orders = {}
                for sku in list(dict_child.keys()):
                    dict_orders[dict_child[sku]] = 0
                dict_change = basic.get_change(name)
                data = {"Sales": 0, "Discount": 0, "Cost": 0, "All_flows": 0, "Nature_flows": 0,
                        "Discount_orders": 0, "All_orders": 0, "Ad_impressions": 0, "Ad_flows": 0, "Ad_orders": 0,
                        "Ad_spend": 0, "Ad_sales": 0}
                data_order = function.open_txt_as_chart('%s/Performance/%s.txt' % (path, date), '\t')
                if '%s/Performance/%s.txt' % (path, date) not in list_delete:
                    list_delete.append('%s/Performance/%s.txt' % (path, date))
                for i in range(0, len(data_order['sku'])):
                    list_temp = list(dict_child.keys()) + list(dict_change.keys())
                    if data_order['sku'][i] in list_temp and data_order['item-status'][i] != 'Cancelled' and data_order[
                            'sales-channel'][i] != 'Non-Amazon':
                        if data_order['sku'][i] in dict_child.keys():
                            sku = data_order['sku'][i]
                        else:
                            sku = dict_change[data_order['sku'][i]]
                        data["All_orders"] += int(data_order['quantity'][i])
                        cost = int(data_order['quantity'][i]) * (dict_fee[sku] + dict_fba[dict_child[sku]][data_order[
                            'currency'][i]] / basic.rate[data_order['currency'][i]])
                        data['Cost'] += (1 + refund_rate) * cost
                        if selling_rate > 0.16:
                            data['Cost'] += int(data_order['quantity'][i]) * 3.41 * refund_rate
                        if not pandas.isnull(data_order['item-price'][i]):
                            data["Sales"] += float(data_order['item-price'][i]) / basic.rate[data_order['currency'][i]]
                        discount = 0
                        try:
                            ids = data_order['promotion-ids '][i]
                        except KeyError:
                            ids = data_order['promotion-ids'][i]
                        if not pandas.isnull(ids):
                            for promotion_id in str(ids).replace('è´­ä¹°æ  æ £', '购买折扣').split(','):
                                if promotion_id in dict_coupon.keys():
                                    if dict_coupon[promotion_id][1] >= 1:
                                        discount += dict_coupon[promotion_id][1]
                                    else:
                                        discount += dict_coupon[promotion_id][1] * float(
                                            data_order['item-price'][i])
                                    if dict_coupon[promotion_id][0] in ['购买折扣', '社交促销']:
                                        data["Discount_orders"] += 1
                                else:
                                    if'US Core Free Shipping Promotion' not in promotion_id and 'PAWS' not in \
                                            promotion_id and 'Duplicated' not in promotion_id:
                                        raise ValueError('找到未记录的促销码：' + promotion_id)
                        if not pandas.isnull(data_order['item-promotion-discount'][i]):
                            data["Discount"] += float(data_order['item-promotion-discount'][i]) / basic.rate[
                                data_order['currency'][i]]
                        else:
                            data["Discount"] += discount / basic.rate[data_order['currency'][i]]
                        dict_orders[dict_child[sku]] += int(data_order['quantity'][i])
                flows = 0
                try:
                    data_sales = pandas.read_csv('%s/Performance/BusinessReport-%s-%s-%s.csv' % (path, day, month, yr))
                    if '%s/Performance/BusinessReport-%s-%s-%s.csv' % (path, day, month, yr) not in list_delete:
                        list_delete.append('%s/Performance/BusinessReport-%s-%s-%s.csv' % (path, day, month, yr))
                    for i in range(0, len(data_sales['（父）ASIN'])):
                        if data_sales['（父）ASIN'][i] == dict_asin[name]:
                            data["All_flows"] = int(data_sales['会话次数 – 总计'][i])
                            flows = int(data_sales['页面浏览量 – 总计'][i])
                            break
                    delete = True
                except FileNotFoundError:
                    pass
                try:
                    data_campaign = pandas.read_csv('%s/Performance/Campaigns_%s月_%s_%s.csv' % (path, month, day,
                                                                                                year))
                    if '%s/Performance/Campaigns_%s月_%s_%s.csv' % (path, month, day, year) not in list_delete:
                        list_delete.append('%s/Performance/Campaigns_%s月_%s_%s.csv' % (path, month, day, year))
                    for i in range(0, len(data_campaign['广告活动'])):
                        if data_campaign['广告活动'][i].find(name) != -1:
                            data["Ad_flows"] += int(data_campaign['点击次数'][i])
                            data["Ad_orders"] += int(data_campaign['订单'][i])
                            data["Ad_spend"] += float(data_campaign['花费(USD)'][i])
                            data["Ad_impressions"] += int(data_campaign['曝光量'][i])
                            data["Ad_sales"] += float(data_campaign['销售额(USD)'][i])
                except FileNotFoundError:
                    pass
                if basic.have_gm(name):
                    list_store = basic.get_gm_store(name)
                    for store in list_store:
                        path = basic.path[store]
                        dict_gm = basic.get_sign_gm(name, store)
                        orders, added = 0, False
                        try:
                            data_order = function.open_txt_as_chart('%s/Performance/%s.txt' % (path, date), '\t')
                            if '%s/Performance/%s.txt' % (path, date) not in list_delete:
                                list_delete.append('%s/Performance/%s.txt' % (path, date))
                            for i in range(0, len(data_order['sku'])):
                                list_temp = list(dict_gm.keys()) + list(dict_change.keys())
                                if data_order['sku'][i] in list_temp and data_order['item-status'][
                                        i] != 'Cancelled' and data_order['sales-channel'][i] != 'Non-Amazon':
                                    if data_order['sku'][i] in dict_gm.keys():
                                        sku = function.reverse_dict(dict_child)[dict_gm[data_order['sku'][i]]]
                                    else:
                                        sku = dict_change[data_order['sku'][i]]
                                    orders += int(data_order['quantity'][i])
                                    data['Cost'] += int(data_order['quantity'][i]) * dict_fee[sku]
                                    data['Cost'] += int(data_order['quantity'][i]) * dict_fba[dict_child[sku]][
                                        data_order['currency'][i]] / basic.rate[data_order['currency'][i]]
                                    if not pandas.isnull(data_order['item-price'][i]):
                                        data["Sales"] += float(data_order['item-price'][i]) / basic.rate[
                                            data_order['currency'][i]]
                                    discount = 0
                                    try:
                                        ids = data_order['promotion-ids '][i]
                                    except KeyError:
                                        ids = data_order['promotion-ids'][i]
                                    if not pandas.isnull(ids):
                                        for promotion_id in str(ids).replace('è´­ä¹°æ  æ £', '购买折扣').split(','):
                                            if promotion_id in dict_coupon.keys():
                                                if dict_coupon[promotion_id][1] >= 1:
                                                    discount += dict_coupon[promotion_id][1]
                                                else:
                                                    discount += dict_coupon[promotion_id][1] * float(
                                                        data_order['item-price'][i])
                                                if dict_coupon[promotion_id][0] in ['购买折扣', '社交促销']:
                                                    data["Discount_orders"] += 1
                                            else:
                                                if 'US Core Free Shipping Promotion' not in promotion_id and 'PAWS' \
                                                        not in promotion_id and 'Duplicated' not in promotion_id:
                                                    raise ValueError('找到未记录的促销码：' + promotion_id)
                                    if not pandas.isnull(data_order['item-promotion-discount'][i]):
                                        data["Discount"] += data_order['item-promotion-discount'][i] / basic.rate[
                                            data_order['currency'][i]]
                                    else:
                                        data["Discount"] += discount / basic.rate[data_order['currency'][i]]
                                    dict_orders[dict_child[sku]] += int(data_order['quantity'][i])
                        except FileNotFoundError:
                            pass
                        try:
                            data_sales = pandas.read_csv(
                                '%s/Performance/BusinessReport-%s-%s-%s.csv' % (path, day, month, yr))
                            if '%s/Performance/BusinessReport-%s-%s-%s.csv' % (path, day, month, yr) not in list_delete:
                                list_delete.append(
                                    '%s/Performance/BusinessReport-%s-%s-%s.csv' % (path, day, month, yr))
                            for i in range(0, len(data_sales['（父）ASIN'])):
                                if data_sales['（父）ASIN'][i] == dict_asin[name]:
                                    if data["All_flows"] == 0:
                                        data["All_flows"] = int(data_sales['会话次数 – 总计'][i])
                                    if flows == 0:
                                        flows = int(data_sales['页面浏览量 – 总计'][i])
                                    break
                            delete = True
                        except FileNotFoundError:
                            pass
                        data["All_orders"] += orders
                        try:
                            data_campaign = pandas.read_csv('%s/Performance/Campaigns_%s月_%s_%s.csv' % (path, month,
                                                                                                        day, year))
                            if '%s/Performance/Campaigns_%s月_%s_%s.csv' % (path, month, day, year) not in list_delete:
                                list_delete.append('%s/Performance/Campaigns_%s月_%s_%s.csv' % (path, month, day, year))
                            for i in range(0, len(data_campaign['广告活动'])):
                                if basic.get_gm_name(name, store) in data_campaign['广告活动'][i]:
                                    data["Ad_flows"] += int(data_campaign['点击次数'][i])
                                    data["Ad_orders"] += int(data_campaign['订单'][i])
                                    data["Ad_spend"] += float(data_campaign['花费(USD)'][i])
                                    data["Ad_impressions"] += int(data_campaign['曝光量'][i])
                                    data["Ad_sales"] += float(data_campaign['销售额(USD)'][i])
                        except FileNotFoundError:
                            pass
                if flows - data["Ad_flows"] > 0:
                    data['Nature_flows'] = flows - data["Ad_flows"]
                else:
                    data['Nature_flows'] = 0
                if data["Sales"] - data["Discount"] > 2 * data["All_orders"]:
                    selling_fee = selling_rate * (data["Sales"] - data["Discount"])
                else:
                    selling_fee = 0.3 * data["All_orders"]
                data['Cost'] += selling_fee * (1 + refund_rate * 0.2) + storage_fee / a[month]
                basic.update_performance(name, date, data['Sales'], data['Discount'], data['Cost'], data['All_flows'],
                                         data['Nature_flows'], data['Discount_orders'], data['All_orders'],
                                         data['Ad_impressions'], data['Ad_flows'], data['Ad_orders'], data['Ad_spend'],
                                         data['Ad_sales'])
                text_orders = json.dumps(dict_orders)
                text_refund = json.dumps(dict_refund)
                basic.update_child_data(name, date, text_orders, text_refund)
                if delete:
                    for item in list_delete:
                        if item not in list_delete_all:
                            list_delete_all.append(item)
    basic.commit()
    import send2trash
    for path in list_delete_all:
        send2trash.send2trash(path.replace('/', '\\'))


def extract_performance(basic: Basic, printer: pyqtSignal):
    try:
        main(basic, printer)
        printer.emit('成功导入产品数据')
    except Exception as ex:
        printer.emit('导入产品数据失败：%s' % ex)

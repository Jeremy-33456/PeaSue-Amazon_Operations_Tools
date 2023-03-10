#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import time
import json
from datetime import datetime
from pytz import utc, timezone
from object.basic import Basic
from PyQt5.QtCore import pyqtSignal
from function.function import open_txt_as_chart


def main(basic: Basic, printer: pyqtSignal):
    dict_fba_fee, dict_manage_fba, dict_fba_storage, dict_storage_fee = {}, {}, {}, {}
    year = int(time.strftime("%Y", time.localtime()))
    month = int(time.strftime("%m", time.localtime()))
    if month == 1:
        last = '%d_12' % (year - 1)
    else:
        last = '%d_%d' % (year, month - 1)
    for store in basic.store_all:
        printer.emit('正在读取%s店的库存数据' % store)
        path = basic.path[store] + '/Storage'
        dict_fba_fee[store] = open_txt_as_chart('%s/fba fee.txt' % path, '\t')
        dict_manage_fba[store] = open_txt_as_chart('%s/manage fba.txt' % path, '\t')
        dict_fba_storage[store] = open_txt_as_chart('%s/fba storage.txt' % path, '\t')
        dict_storage_fee[store] = open_txt_as_chart('%s/storage fee_%s.txt' % (path, last), '\t')
    for name in basic.product_list:
        printer.emit('正在处理产品：%s' % name)
        store = basic.get_store(name)
        data_fba_fee, data_manage_fba = dict_fba_fee[store], dict_manage_fba[store]
        data_fba_storage, data_storage_fee = dict_fba_storage[store], dict_storage_fee[store]
        dict_sign = basic.get_sign(name)
        list_child = list(dict_sign.keys())
        dict_storage = {}
        dict_asin = basic.get_asin(name)
        for item in basic.get_storage_single(name):
            list_temp = [json.loads(item[3])]
            for i in range(4, 15):
                list_temp.append(item[i])
            dict_storage[item[2]] = list_temp
        for child in list_child:
            dict_storage[dict_sign[child]][-2] = 0
        for i in range(0, len(data_fba_fee['sku'])):
            sku = str(data_fba_fee['sku'][i])
            if sku in list_child:
                try:
                    dict_storage[dict_sign[sku]][0][data_fba_fee['currency'][i]] = float(
                        data_fba_fee['expected-fulfillment-fee-per-unit'][i])
                except KeyError:
                    dict_storage[dict_sign[sku]][0] = {data_fba_fee['currency'][i]: float(
                        data_fba_fee['expected-fulfillment-fee-per-unit'][i])}
                except ValueError:
                    pass
        for i in range(0, len(data_storage_fee['asin'])):
            asin = str(data_storage_fee['asin'][i])
            sku = ''
            for item in list(dict_asin.keys()):
                if dict_asin[item] == asin:
                    sku = item
                    break
            if sku in list_child:
                dict_storage[dict_sign[sku]][-2] += float(data_storage_fee['estimated_monthly_storage_fee'][i])
        for i in range(0, len(data_manage_fba['sku'])):
            sku = str(data_manage_fba['sku'][i])
            if sku in list_child:
                dict_storage[dict_sign[sku]][1] = float(data_manage_fba['your-price'][i])
                dict_storage[dict_sign[sku]][2] = int(data_manage_fba['afn-fulfillable-quantity'][i])
                dict_storage[dict_sign[sku]][3] = int(data_manage_fba['afn-warehouse-quantity'][i])
                dict_storage[dict_sign[sku]][4] = int(data_manage_fba['afn-total-quantity'][i])
        for child in list_child:
            if child not in data_manage_fba['sku'].values:
                dict_storage[dict_sign[child]][2] = 0
                dict_storage[dict_sign[child]][3] = 0
                dict_storage[dict_sign[child]][4] = 0
        for i in range(0, len(data_fba_storage['sku'])):
            sku = str(data_fba_storage['sku'][i])
            if sku in list_child:
                dict_storage[dict_sign[sku]][5] = int(data_fba_storage['inv-age-0-to-90-days'][i])
                dict_storage[dict_sign[sku]][6] = int(data_fba_storage['inv-age-91-to-180-days'][i])
                dict_storage[dict_sign[sku]][7] = int(data_fba_storage['inv-age-181-to-270-days'][i])
                dict_storage[dict_sign[sku]][8] = int(data_fba_storage['inv-age-271-to-365-days'][i])
                dict_storage[dict_sign[sku]][9] = int(data_fba_storage['inv-age-365-plus-days'][i])
                dict_storage[dict_sign[sku]][-1] = int(data_fba_storage['estimated-excess-quantity'][i])
        for child in list_child:
            if child not in data_fba_storage['sku'].values:
                dict_storage[dict_sign[child]][5] = 0
                dict_storage[dict_sign[child]][6] = 0
                dict_storage[dict_sign[child]][7] = 0
                dict_storage[dict_sign[child]][8] = 0
                dict_storage[dict_sign[child]][9] = 0
                dict_storage[dict_sign[child]][-1] = 0
        if basic.have_gm(name):
            list_store_gm = basic.get_gm_store(name)
            for store_gm in list_store_gm:
                data_fba_fee_gm, data_manage_fba_gm = dict_fba_fee[store_gm], dict_manage_fba[store_gm]
                data_fba_storage_gm, data_storage_fee_gm = dict_fba_storage[store_gm], dict_storage_fee[store_gm]
                dict_gm = basic.get_sign_gm(name, store_gm)
                list_child = list(dict_gm.keys())
                for i in range(0, len(data_fba_fee_gm['sku'])):
                    sku = str(data_fba_fee_gm['sku'][i])
                    if sku in list_child:
                        if basic.have_cart(name, dict_gm[sku], store_gm):
                            try:
                                dict_storage[dict_gm[sku]][0][data_fba_fee_gm['currency'][i]] = float(
                                    data_fba_fee_gm['expected-fulfillment-fee-per-unit'][i])
                            except TypeError:
                                dict_storage[dict_gm[sku]][0] = {data_fba_fee_gm['currency'][i]: float(
                                    data_fba_fee_gm['expected-fulfillment-fee-per-unit'][i])}
                for i in range(0, len(data_storage_fee_gm['asin'])):
                    asin = str(data_storage_fee_gm['asin'][i])
                    sku = ''
                    for item in list(dict_asin.keys()):
                        if dict_asin[item] == asin:
                            sku = item
                            break
                    if sku:
                        dict_storage[dict_sign[sku]][-2] += float(data_storage_fee_gm[
                                                                      'estimated_monthly_storage_fee'][i])
                for i in range(0, len(data_manage_fba_gm['sku'])):
                    sku = str(data_manage_fba_gm['sku'][i])
                    if sku in list_child:
                        if basic.have_cart(name, dict_gm[sku], store_gm):
                            dict_storage[dict_gm[sku]][1] = float(data_manage_fba_gm['your-price'][i])
                        dict_storage[dict_gm[sku]][2] += int(data_manage_fba_gm['afn-fulfillable-quantity'][i])
                        dict_storage[dict_gm[sku]][3] += int(data_manage_fba_gm['afn-warehouse-quantity'][i])
                        dict_storage[dict_gm[sku]][4] += int(data_manage_fba_gm['afn-total-quantity'][i])
                for i in range(0, len(data_fba_storage_gm['sku'])):
                    sku = str(data_fba_storage_gm['sku'][i])
                    if sku in list_child:
                        dict_storage[dict_gm[sku]][5] += int(data_fba_storage_gm['inv-age-0-to-90-days'][i])
                        dict_storage[dict_gm[sku]][6] += int(data_fba_storage_gm['inv-age-91-to-180-days'][i])
                        dict_storage[dict_gm[sku]][7] += int(data_fba_storage_gm['inv-age-181-to-270-days'][i])
                        dict_storage[dict_gm[sku]][8] += int(data_fba_storage_gm['inv-age-271-to-365-days'][i])
                        dict_storage[dict_gm[sku]][9] += int(data_fba_storage_gm['inv-age-365-plus-days'][i])
                        dict_storage[dict_gm[sku]][-1] += int(data_fba_storage_gm['estimated-excess-quantity'][i])
        for sign in dict_sign.values():
            basic.update_storage(json.dumps(dict_storage[sign][0]), dict_storage[sign][1],
                                 dict_storage[sign][2], dict_storage[sign][3], dict_storage[sign][4],
                                 dict_storage[sign][5], dict_storage[sign][6], dict_storage[sign][7],
                                 dict_storage[sign][8], dict_storage[sign][9], dict_storage[sign][10],
                                 dict_storage[sign][11], name, sign)
    now = datetime.now(tz=utc).astimezone(timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')
    basic.update_update(json.dumps([now]))
    basic.commit()


def extract_storage(basic: Basic, printer: pyqtSignal):
    try:
        main(basic, printer)
        printer.emit('成功导入库存数据')
    except Exception as ex:
        printer.emit('导入库存数据失败：%s' % ex)

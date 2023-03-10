#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
import pandas
from object.basic import Basic
from function import function
from advertisement import assist
from PyQt5.QtCore import pyqtSignal


def main(basic: Basic, printer: pyqtSignal):
    list_asin = json.loads(basic.get_picture_asin()[0])
    list_store = basic.store_all
    for store in list_store:
        printer.emit('正在采集%s店数据' % store)
        list_name = basic.name_in_store(store)
        try:
            tar_sp = pandas.read_excel('%s/Advertisement/SP - targeting.xlsx' % basic.path[store], sheet_name=0)
            for i in range(0, len(tar_sp['日期'])):
                date = str(tar_sp['日期'][i])[0: 10].replace('-', '.')
                result = function.find_one(tar_sp['广告活动名称'][i], list_name)
                if result[0]:
                    targeting = tar_sp['投放'][i]
                    if 'asin=' in targeting:
                        targeting = targeting.replace('asin=', '').replace('"', '')
                    elif 'category=' in targeting:
                        targeting = targeting.replace('category=', '').replace('"', '*').strip()
                    if '"' in targeting:
                        targeting = targeting.replace('"', '\\"')
                    basic.update_targeting(date, tar_sp['广告活动名称'][i], tar_sp['广告组名称'][i], targeting,
                                           int(tar_sp['展示量'][i]), int(tar_sp['点击量'][i]), float(tar_sp['花费'][i]),
                                           int(tar_sp['7天总订单数(#)'][i]), float(tar_sp['7天总销售额'][i]))
        except FileNotFoundError:
            printer.emit('SP-targeting文件未找到')
        try:
            st_sp = pandas.read_excel('%s/Advertisement/SP - search_terms.xlsx' % basic.path[store], sheet_name=0)
            for i in range(0, len(st_sp['日期'])):
                date = str(st_sp['日期'][i])[0: 10].replace('-', '.')
                result = function.find_one(st_sp['广告活动名称'][i], list_name)
                if result[0]:
                    targeting = st_sp['投放'][i]
                    if 'asin=' in targeting:
                        targeting = targeting.replace('asin=', '').replace('"', '')
                    elif 'category=' in targeting:
                        targeting = targeting.replace('category=', '').replace('"', '*').strip()
                    if '"' in targeting:
                        targeting = targeting.replace('"', '\\"')
                    st = st_sp['客户搜索词'][i]
                    if st[0: 2] == 'b0':
                        if st not in list_asin:
                            list_asin.append(st)
                    if '"' in st:
                        st = st.replace('"', '\\"')
                    basic.update_search_terms(date, st_sp['广告活动名称'][i], st_sp['广告组名称'][i], targeting, st,
                                              int(st_sp['展示量'][i]), int(st_sp['点击量'][i]), float(st_sp['花费'][i]),
                                              int(st_sp['7天总订单数(#)'][i]), float(st_sp['7天总销售额'][i]))
        except FileNotFoundError:
            printer.emit('SP-search_terms文件未找到')
        try:
            tar_sb = pandas.read_excel('%s/Advertisement/SB - targeting.xlsx' % basic.path[store], sheet_name=0)
            for i in range(0, len(tar_sb['日期'])):
                date = str(tar_sb['日期'][i])[0: 10].replace('-', '.')
                result = function.find_one(tar_sb['广告活动名称'][i], list_name)
                if result[0]:
                    targeting = tar_sb['投放'][i]
                    if 'asin=' in targeting:
                        targeting = targeting.replace('asin=', '').replace('"', '')
                    elif 'category=' in targeting:
                        targeting = targeting.replace('category=', '').replace('"', '*').strip()
                    if '"' in targeting:
                        targeting = targeting.replace('"', '\\"')
                    basic.update_targeting(date, tar_sb['广告活动名称'][i], '', targeting, int(tar_sb['展示量'][i]),
                                           int(tar_sb['点击量'][i]), float(tar_sb['花费'][i]),
                                           int(tar_sb['14天总订单数(#)'][i]), float(tar_sb['14天总销售额'][i]))
        except FileNotFoundError:
            printer.emit('SB-targeting文件未找到')
        try:
            st_sb = pandas.read_excel('%s/Advertisement/SB - search_terms.xlsx' % basic.path[store], sheet_name=0)
            for i in range(0, len(st_sb['日期'])):
                date = str(st_sb['日期'][i])[0: 10].replace('-', '.')
                result = function.find_one(st_sb['广告活动名称'][i], list_name)
                if result[0]:
                    targeting = st_sb['投放'][i]
                    if 'asin=' in targeting:
                        targeting = targeting.replace('asin=', '').replace('"', '')
                    elif 'category=' in targeting:
                        targeting = targeting.replace('category=', '').replace('"', '*').strip()
                    if '"' in targeting:
                        targeting = targeting.replace('"', '\\"')
                    st = st_sb['客户搜索词'][i]
                    if st[0: 2] == 'b0':
                        if st not in list_asin:
                            list_asin.append(st)
                    if '"' in st:
                        st = st.replace('"', '\\"')
                    basic.update_search_terms(date, st_sb['广告活动名称'][i], '', targeting, st, int(st_sb['展示量'][i]),
                                              int(st_sb['点击量'][i]), float(st_sb['花费'][i]),
                                              int(st_sb['14天总订单数(#)'][i]), float(st_sb['14天总销售额'][i]))
        except FileNotFoundError:
            printer.emit('SB-search_terms文件未找到')
        try:
            tar_sd = pandas.read_excel('%s/Advertisement/SD - targeting.xlsx' % basic.path[store], sheet_name=0)
            for i in range(0, len(tar_sd['日期'])):
                date = str(tar_sd['日期'][i])[0: 10].replace('-', '.')
                result = function.find_one(tar_sd['广告活动名称'][i], list_name)
                if result[0]:
                    targeting = tar_sd['投放策略'][i]
                    if 'asin=' in targeting:
                        targeting = targeting.replace('asin=', '').replace('"', '')
                    elif 'category=' in targeting:
                        targeting = targeting.replace('category=', '').replace('"', '*').strip()
                    elif 'audience=' in targeting:
                        targeting = targeting.replace('audience=', '').replace('"', '*').strip()
                    if '"' in targeting:
                        targeting = targeting.replace('"', '\\"')
                    basic.update_targeting(date, tar_sd['广告活动名称'][i], tar_sd['广告组名称'][i], targeting,
                                           int(tar_sd['展示量'][i]), int(tar_sd['点击量'][i]), float(tar_sd['花费'][i]),
                                           int(tar_sd['14天总订单数(#)'][i]), float(tar_sd['14天总销售额'][i]))
        except FileNotFoundError:
            printer.emit('SD-targeting文件未找到')
        try:
            st_sd = pandas.read_excel('%s/Advertisement/SD - search_terms.xlsx' % basic.path[store], sheet_name=0)
            for i in range(0, len(st_sd['开始日期'])):
                date = str(st_sd['开始日期'][i])[0: 10].replace('-', '.')
                campaign = st_sd['广告活动名称'][i]
                result = function.find_one(campaign, list_name)
                if result[0]:
                    targeting = st_sd['投放策略'][i]
                    if 'asin=' in targeting:
                        targeting = targeting.replace('asin=', '').replace('"', '')
                    elif 'category=' in targeting:
                        targeting = targeting.replace('category=', '').replace('"', '*').strip()
                    elif 'audience=' in targeting:
                        targeting = targeting.replace('audience=', '').replace('"', '*').strip()
                    if '"' in targeting:
                        targeting = targeting.replace('"', '\\"')
                    group = assist.get_group(campaign, basic)[0]
                    st = st_sd['匹配的目标'][i]
                    if st[0: 2] == 'b0':
                        if st not in list_asin:
                            list_asin.append(st)
                    if '"' in st:
                        st = st.replace('"', '\\"')
                    basic.update_search_terms(date, campaign, group, targeting, st, int(st_sd['展示量'][i]),
                                              int(st_sd['点击量'][i]), float(st_sd['花费'][i]),
                                              int(st_sd['14天总订单数(#)'][i]), float(st_sd['14天总销售额'][i]))
        except FileNotFoundError:
            printer.emit('SD-search_terms文件未找到')
    text_temp = json.dumps(list_asin)
    basic.update_picture_asin(text_temp)
    basic.commit()


def extract_data(basic: Basic, printer: pyqtSignal):
    try:
        main(basic, printer)
        printer.emit('成功导入广告数据')
    except Exception as ex:
        printer.emit('导入广告数据失败：%s' % ex)

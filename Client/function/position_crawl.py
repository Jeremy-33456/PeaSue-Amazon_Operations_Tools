#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
from function import poster
from datetime import datetime
from pytz import utc, timezone
from object.basic import Basic
from PyQt5.QtCore import pyqtSignal
from selenium.common.exceptions import TimeoutException


def main(basic: Basic, printer: pyqtSignal):
    driver = poster.open_amazon('show', 60, printer)
    if driver is None:
        printer.emit('未找到浏览器驱动')
    else:
        list_name = basic.product_list
        dict_child_asin = {}
        for name in list_name:
            dict_child_asin[name] = list(basic.get_asin(name).values())
        dict_keyword = {}
        for name in list_name:
            dict_keyword[name] = basic.get_search(name)
        date = datetime.now(tz=utc).astimezone(timezone('US/Pacific')).strftime('%Y.%m.%d')
        for name in list_name:
            sku = basic.sku[name]
            asin = basic.asin[name]
            if len(basic.get_crawl(name, date)) == 0:
                list_child_asin = dict_child_asin[name]
                list_keyword = dict_keyword[name]
                dict_nature, dict_sponsored = {}, {}
                for keyword in list_keyword:
                    nature, sponsored = '', ''
                    for i in range(1, 8):
                        while True:
                            while True:
                                try:
                                    printer.emit('正在获取' + sku + ' - ' + keyword + ' - 第' + str(i) + '页的结果')
                                    driver.get('https://www.amazon.com/s?k=' + keyword.replace(
                                        ' ', '+') + '&page=' + str(i) + '&ref=nb_sb_noss')
                                    break
                                except TimeoutException:
                                    poster.delay(2, 5, printer)
                            html = driver.execute_script("return document.documentElement.outerHTML")
                            if "Type the characters you see in this image:" in str(html):
                                while True:
                                    poster.delay(2, 5, printer)
                                    try:
                                        driver.refresh()
                                        printer.emit('出现验证码，刷新')
                                    except TimeoutException:
                                        pass
                                    html = driver.execute_script("return document.documentElement.outerHTML")
                                    if "Type the characters you see in this image:" not in str(html):
                                        break
                            result = poster.analysis_position(html, str(i), list_child_asin, nature, sponsored, printer)
                            if result != 'error':
                                nature = result[0]
                                sponsored = result[1]
                                break
                            poster.delay(2, 5, printer)
                        if nature != '' and sponsored != '':
                            break
                        poster.delay(1, 2, printer)
                    if nature == '':
                        printer.emit(sku + ' - ' + keyword + ' - ' + 'nature - 没找到')
                    else:
                        printer.emit(sku + ' - ' + keyword + ' - ' + 'nature' + ' - ' + nature)
                    if sponsored == '':
                        printer.emit(sku + '  ' + keyword + '  ' + 'sponsored - 没找到')
                    else:
                        printer.emit(sku + ' - ' + keyword + ' - ' + 'sponsored' + ' - ' + sponsored)
                    dict_nature[keyword], dict_sponsored[keyword] = nature, sponsored
                    poster.delay(1, 2, printer)
                text_nature, text_sponsored = json.dumps(dict_nature), json.dumps(dict_sponsored)
                while True:
                    while True:
                        try:
                            printer.emit('正在获取' + sku + ' - ' + asin + '的结果')
                            driver.get('https://www.amazon.com/dp/' + asin)
                            break
                        except TimeoutException:
                            poster.delay(2, 5, printer)
                    html = driver.execute_script("return document.documentElement.outerHTML")
                    if "Type the characters you see in this image:" in str(html):
                        while True:
                            poster.delay(2, 5, printer)
                            try:
                                driver.refresh()
                                printer.emit('出现验证码，刷新')
                            except TimeoutException:
                                pass
                            html = driver.execute_script("return document.documentElement.outerHTML")
                            if "Type the characters you see in this image:" not in str(html):
                                break
                    if "Sorry! We couldn't find that page. Try searching or go to Amazon's home page." in str(html):
                        rank_a = ''
                        number = 0
                        rate = 0.0
                        break
                    else:
                        result = poster.analysis_info(html, printer)
                        if result != 'error':
                            rank_a = result[0]
                            number = result[1]
                            rate = result[2]
                            break
                        printer.emit('无内容，重新获取')
                    poster.delay(2, 5, printer)
                printer.emit(text_nature)
                printer.emit(text_sponsored)
                printer.emit('%s  %s  %s' % (rank_a, number, rate))
                basic.update_crawl(name, date, text_nature, text_sponsored, rank_a, number, rate)
                basic.commit()
                poster.delay(2, 5, printer)
            else:
                printer.emit('%s的记录已存在' % name)
    driver.close()


def crawl_position(basic: Basic, printer: pyqtSignal):
    try:
        main(basic, printer)
        printer.emit('成功进行坑位爬取')
    except Exception as ex:
        printer.emit('坑位爬取失败：%s' % ex)

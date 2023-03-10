#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
from bs4 import BeautifulSoup
from object.basic import Basic
from function import poster
from PyQt5.QtCore import pyqtSignal
from selenium.common.exceptions import TimeoutException


def main(basic: Basic, printer: pyqtSignal):
    list_asin = json.loads(basic.get_picture_asin()[0])
    list_need = list_asin.copy()
    if len(list_asin) == 0:
        for item in basic.get_non_rank_asin():
            if item[0] not in list_need:
                list_need.append(item[0])
    if len(list_need) > 0:
        driver = poster.open_amazon('show', 60, printer)
        if driver is None:
            printer.emit('未找到浏览器驱动')
            return
        for asin in list_need:
            not_found = False
            while True:
                while True:
                    try:
                        printer.emit('正在获取 ' + asin)
                        driver.get('https://www.amazon.com/dp/' + asin)
                        break
                    except TimeoutException:
                        poster.delay(2, 5, printer)
                html = driver.execute_script("return document.documentElement.outerHTML")
                if "Type the characters you see in this image:" in str(html):
                    count = 0
                    while True:
                        poster.delay(2, 5, printer)
                        count += 1
                        if count < 5:
                            try:
                                driver.refresh()
                                html = driver.execute_script("return document.documentElement.outerHTML")
                                printer.emit('出现验证码，刷新')
                            except TimeoutException:
                                pass
                        if "Type the characters you see in this image:" not in str(html):
                            break
                if "Sorry! We couldn't find that page. Try searching or go to Amazon's home page." in str(html):
                    brand, res, http = '', ['', 0, 0.0], ''
                    not_found = True
                    break
                else:
                    info = BeautifulSoup(html, "html.parser")
                    res = poster.analysis_info(html, printer)
                    if res != 'error':
                        list_temp = info.find_all('script', {'type': 'text/javascript'})
                        http = ''
                        for temp in list_temp:
                            if 'colorImages' in str(temp):
                                index1 = str(temp).find('"main":{"')
                                index2 = str(temp).find('"', index1 + 9)
                                http = str(temp)[index1 + 9: index2]
                                break
                        try:
                            brand = str(info.find('a', {'id': 'bylineInfo'}).string)
                            if brand.find('Visit the') != -1 and brand.find('Store') != -1:
                                brand = brand[10: -6]
                            brand = brand.replace('Brand:', '').replace('"', '').strip()
                        except AttributeError:
                            try:
                                brand = str(info.find('a', {'class': 'a-color-base a-link-normal a-text-bold'}).string)
                                brand = brand.strip()
                            except AttributeError:
                                brand = ''
                        break
                poster.delay(2, 5, printer)
            printer.emit(brand)
            printer.emit(http)
            if not_found:
                try:
                    list_asin.remove(asin)
                    text_upload = json.dumps(list_asin)
                    basic.update_picture_asin(text_upload)
                except ValueError:
                    pass
            elif brand != '' and res != ['', 0, 0.0] and http != '':
                basic.update_picture(asin, brand, res[0], res[1], res[2], http)
                try:
                    list_asin.remove(asin)
                    text_upload = json.dumps(list_asin)
                    basic.update_picture_asin(text_upload)
                except ValueError:
                    pass
                printer.emit('已更新信息：%s' % asin)
            basic.commit()
            poster.delay(2, 5, printer)
        driver.close()
    else:
        printer.emit('无asin需要爬取')


def crawl_picture(basic: Basic, printer: pyqtSignal):
    try:
        main(basic, printer)
        printer.emit('成功进行图片爬取')
    except Exception as ex:
        printer.emit('图片爬取失败：%s' % ex)

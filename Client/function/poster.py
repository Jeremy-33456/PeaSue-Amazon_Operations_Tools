#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from PyQt5.QtCore import pyqtSignal
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException


def delay(bottom: int or float, top: int or float, printer: pyqtSignal = None):
    time_delay = round(random.uniform(bottom, top), 2)
    if printer:
        printer.emit('请等待' + str(time_delay) + '秒')
    else:
        print('请等待' + str(time_delay) + '秒')
    time.sleep(time_delay)


def open_amazon(show: str, timeout: int, printer: pyqtSignal):
    option = webdriver.ChromeOptions()
    if show == 'hide':
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')
    printer.emit('正在启动浏览器')
    try:
        driver = webdriver.Chrome(options=option)
        driver.set_page_load_timeout(timeout)
        printer.emit('正在打开亚马逊')
        driver.get('https://www.amazon.com')
        printer.emit('正在修改地址')
        while True:
            try:
                driver.find_element(By.XPATH, "//div[@id='glow-ingress-block']").click()
                break
            except Exception as ex:
                printer.emit('未找到地址更改按钮：%s' % ex)
                delay(1, 2, printer)
        while True:
            try:
                driver.find_element(By.XPATH, "//input[@id='GLUXZipUpdateInput']").send_keys('90001')
                break
            except Exception as ex:
                printer.emit('未找到邮编输入框：%s' % ex)
                try:
                    driver.find_element(By.XPATH, "//div[@id='glow-ingress-block']").click()
                except Exception as ex:
                    printer.emit('未找到地址更改按钮：%s' % ex)
                delay(1, 2, printer)
        delay(0.5, 1, printer)
        while True:
            try:
                driver.find_element(By.XPATH, "//div[@class='a-column a-span4 a-span-last']").click()
                break
            except Exception as ex:
                printer.emit('未找到应用按钮：%s' % ex)
                try:
                    driver.find_element(By.XPATH, "//input[@id='GLUXZipUpdateInput']").send_keys('15301')
                except Exception as ex:
                    printer.emit('未找到邮编输入框：%s' % ex)
                delay(1, 2, printer)
        delay(1, 2, printer)
        while True:
            try:
                driver.find_element(By.XPATH, "//button[@name='glowDoneButton']").click()
                break
            except Exception as ex:
                try:
                    driver.find_element(By.XPATH, '//span[@class="a-button a-column a-button-primary a-button-span4"]')
                    delay(0.5, 1, printer)
                    driver.refresh()
                    break
                except NoSuchElementException:
                    pass
                printer.emit('未找到完成按钮：%s' % ex)
                delay(1, 2, printer)
        return driver
    except WebDriverException:
        pass


def analysis_position(result, page: str, list_child_asin: list, nature: str, sponsored: str, printer: pyqtSignal):
    info = BeautifulSoup(result, "html.parser")
    temp_s = info.find_all('div', {'data-asin': True, 'data-index': True})
    if len(temp_s) == 0:
        return 'error'
    else:
        for j in range(0, len(temp_s)):
            asin = temp_s[j].attrs['data-asin']
            index = temp_s[j].attrs['data-index']
            index = str(int(index) + 1)
            if str(temp_s[j]).find('Sponsored') == -1:
                status = 'nature'
            else:
                status = 'sponsored'
            if asin in list_child_asin:
                if nature == '' and status == 'nature':
                    printer.emit('发现自然坑位')
                    nature = page + ' # ' + index
                elif sponsored == '' and status == 'sponsored':
                    printer.emit('发现广告坑位')
                    sponsored = page + ' # ' + index
            if nature != '' and sponsored != '':
                break
        return [nature, sponsored]


def analysis_info(result, printer: pyqtSignal):
    info = BeautifulSoup(result, "html.parser")
    temp_s = info.find_all('span', {'class': 'a-text-bold'})
    if len(temp_s) == 0:
        return 'error'
    else:
        rank_a = ''
        try:
            temp = info.find('ul', {'class': 'a-unordered-list a-nostyle a-vertical zg_hrsr'})
            temp_all = temp.find_all('li')
            rank, rank_temp = [], []
            for i in range(0, len(temp_all)):
                temp = str(temp_all[i].find('span', {'class': 'a-list-item'}).text).replace(
                    '#', '').replace(',', '').strip()
                rank_temp.append(temp)
                rank.append(int(temp.split(' ')[0]))
            if len(temp_all) > 1:
                index_r = rank.index(min(rank))
            else:
                index_r = 0
            rank_a = rank_temp[index_r]
            printer.emit(rank_a)
        except AttributeError:
            th_all = info.find_all('th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
            for th in th_all:
                if 'Best Sellers Rank' == th.text.strip():
                    rank, rank_temp = [], []
                    span_all = th.findParent().find('td').find('span').find_all('span')
                    for span in span_all:
                        temp = str(span.text).replace('#', '').replace(',', '').strip()
                        rank_temp.append(temp)
                        rank.append(int(temp.split(' ')[0]))
                    index_r = rank.index(min(rank))
                    rank_a = rank_temp[index_r]
                    printer.emit(rank_a)
                    break
            if rank_a == '':
                printer.emit('暂无排名：未找到排名')
        temp = info.find('div', {'id': 'reviewsMedley'})
        try:
            rate = float(str(temp.find('span', {'class': 'a-icon-alt'}).string).replace('out of 5 stars', '').strip())
            printer.emit(str(rate))
        except Exception as ex:
            rate = 0.0
            printer.emit('暂无评论：%s' % ex)
        try:
            number = str(temp.find('span', {'class': 'a-size-base a-color-secondary'}))
            number = number.replace('<!--TODO: Replace this string with arp-x-ratings 5/22/19 (ShopperExp-5143)-->', '')
            number = number.replace('<span class="a-size-base a-color-secondary">', '').strip()
            number = number.replace('customer', '').replace('</span>', '').replace('global', '').strip()
            number = int(number.replace('ratings', '').replace('rating', '').replace(',', '').strip())
            printer.emit(str(number))
        except Exception as ex:
            number = 0
            printer.emit('暂无评论：%s' % ex)
        return rank_a, number, rate

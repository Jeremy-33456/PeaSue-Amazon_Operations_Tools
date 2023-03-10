#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
import time
import struct
import socket
import winreg
import threading
from function import function


class Basic:
    def __init__(self, session: str, conn_socket: socket.socket):
        self.history = False
        self.session = session
        self.socket = conn_socket
        self.list_month, self.rate, self.strategy, self.power, self.no_use, self.category_index = [], {}, {}, {}, {}, {}
        self.user_list, self.password, self.secret, self.product, self.belong, self.child = [], {}, {}, {}, {}, {}
        self.all_store, self.path, self.color, self.type, self.plural, self.index_category = [], {}, {}, [], {}, {}
        self.brand, self.size, self.type_synonym, self.deny, self.variation1, self.variation2 = {}, {}, {}, {}, {}, {}
        self.list_variation, self.selling_rate, self.audience, self.audisence, self.update = {}, {}, {}, {}, ''
        self.product_list, self.store_list, self.store, self.sku, self.asin, self.category = [], [], {}, {}, {}, {}
        self.gm, self.search, self.information, self.fit, self.child, self.cart, self.sign = {}, {}, {}, {}, {}, {}, {}
        self.child_asin, self.change, self.child_gm, self.price, self.coupon, self.date = {}, {}, {}, {}, {}, {}
        self.campaign, self.group, self.product_all, self.store_all, self.discount = {}, {}, [], [], {}
        self.shipment = []
        self.get_basic()
        self.thread = threading.Thread(target=self.keep_connect)
        self.thread.setDaemon(True)
        self.thread.start()

    def get_message(self, command: str, data=None):
        message = json.dumps([command, self.session, data])
        data_len = len(message)
        struct_bytes = struct.pack('i', data_len)
        self.socket.send(struct_bytes)
        self.socket.send(message.encode('utf-8'))
        struct_bytes = self.socket.recv(4)
        data_len = struct.unpack('i', struct_bytes)[0]
        gap_abs = data_len % 1024
        count = data_len // 1024
        recv_data = b''
        for i in range(count):
            recv_data += self.socket.recv(1024, socket.MSG_WAITALL)
        recv_data += self.socket.recv(gap_abs, socket.MSG_WAITALL)
        return json.loads(recv_data)

    def send_message(self, command: str, data=None):
        message = json.dumps([command, self.session, data])
        data_len = len(message)
        struct_bytes = struct.pack('i', data_len)
        self.socket.send(struct_bytes)
        self.socket.send(message.encode('utf-8'))

    def keep_connect(self):
        while True:
            time.sleep(60)
            self.send_message('keep_connect')

    def commit(self):
        self.send_message('commit')

    def get_basic(self):
        (self.list_month, self.rate, self.strategy, self.power, self.no_use, self.category_index, self.product_list,
         self.store_list, self.store, self.sku, self.asin, self.category, self.gm, self.search, self.information,
         self.fit, self.child, self.cart, self.sign, self.child_asin, self.change, self.child_gm, self.price,
         self.all_store, self.path, self.coupon, discount, self.shipment, self.color, self.type, self.plural,
         self.brand, self.size, self.type_synonym, self.deny, self.variation1, self.variation2, self.list_variation,
         self.selling_rate, self.audience, self.audisence, self.date, self.update, self.campaign,
         self.group) = self.get_message('get_basic', self.history)
        self.product_all = self.get_product_all()
        self.store_all = self.get_store_all()
        self.strategy.update(function.reverse_dict(self.strategy))
        self.index_category = function.reverse_dict(self.category_index)
        temp = r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        temp = winreg.OpenKey(winreg.HKEY_CURRENT_USER, temp)
        path = '%s/Super Browser' % winreg.QueryValueEx(temp, "Desktop")[0].replace('\\', '/')
        for key in self.path.keys():
            self.path[key] = '%s/%s' % (path, self.path[key])
        self.discount = {}
        for key in discount.keys():
            for key1 in discount[key].keys():
                for key2 in discount[key][key1].keys():
                    try:
                        sign = self.get_sign(key)[key1]
                    except KeyError:
                        sign = self.get_sign_gm(key, key2)[key1]
                    if self.have_cart(key, sign, key2):
                        self.discount[key, sign] = discount[key][key1][key2]
        self.plural['reverse'] = function.reverse_dict(self.plural)

    def get_product_all(self):
        temp = self.product_list.copy()
        for name in self.product_list:
            if name in self.gm.keys():
                temp += list(self.gm[name].values())
        return temp

    def get_store_all(self):
        temp = self.store_list.copy()
        for name in self.product_list:
            if name in self.gm.keys():
                for temp1 in list(self.gm[name].keys()):
                    if temp1 not in temp:
                        temp.append(temp1)
        return temp

    def is_gm(self, name: str):
        temp = False
        for key in self.gm.keys():
            if name in self.gm[key].values():
                temp = True
                break
        return temp

    def have_gm(self, name: str):
        if name in self.gm.keys():
            temp = True
        else:
            temp = False
        return temp

    def get_gm_name(self, name: str, store: str = ''):
        if store:
            try:
                temp = self.gm[name][store]
            except KeyError:
                temp = ''
        else:
            try:
                temp = list(self.gm[name].values())
            except KeyError:
                temp = []
        return temp

    def get_gm_store(self, name: str):
        try:
            temp = list(self.gm[name].keys())
        except KeyError:
            temp = []
        return temp

    def get_origin(self, name: str):
        temp = name
        for key in self.gm.keys():
            if name in self.gm[key].values():
                temp = key
                break
        return temp

    def get_store(self, name: str):
        try:
            temp = self.store[name]
        except KeyError:
            temp = ''
            for key in self.gm.keys():
                for key1 in self.gm[key].keys():
                    if self.gm[key][key1] == name:
                        temp = key1
                        break
                if temp:
                    break
        return temp

    def name_in_store(self, store: str):
        temp = []
        for key in self.store.keys():
            if self.store[key] == store and key in self.product_list:
                temp.append(key)
        for key in self.gm.keys():
            if store in self.gm[key].keys() and key in self.product_list:
                temp.append(self.gm[key][store])
        return temp

    def get_category(self, name: str):
        try:
            temp = self.category[name]
        except KeyError:
            temp = ''
        return temp

    def get_search(self, name: str):
        try:
            temp = self.search[name]
        except KeyError:
            temp = []
        return temp

    def get_information(self, name: str):
        try:
            temp = self.information[name]
        except KeyError:
            temp = {}
        return temp

    def get_fit(self, name: str):
        try:
            temp = self.fit[name]
        except KeyError:
            temp = []
        return temp

    def get_child(self, name: str):
        try:
            temp = self.child[name]
        except KeyError:
            temp = []
        return temp

    def get_sign(self, name: str):
        try:
            temp = self.sign[name]
        except KeyError:
            temp = {}
        return temp

    def get_sign_gm(self, name: str, store: str):
        try:
            temp = self.sign[name].copy()
        except KeyError:
            temp = {}
        for key in self.child_gm[name].keys():
            try:
                temp[self.child_gm[name][key][store]] = self.sign[name][key]
            except KeyError:
                pass
        return temp

    def get_asin(self, name: str):
        try:
            temp = self.child_asin[name].copy()
        except KeyError:
            temp = {}
        try:
            for key in self.child_gm[name].keys():
                for temp1 in self.child_gm[name][key]:
                    temp[self.child_gm[name][key][temp1]] = self.child_asin[name][key]
        except KeyError:
            pass
        return temp

    def have_cart(self, name: str, sign: str, store: str):
        try:
            return store == self.cart[name][sign]
        except KeyError:
            return store == self.get_store(name)

    def get_change(self, name: str):
        try:
            return self.change[name]
        except KeyError:
            return {}

    def get_price(self, name: str, sku: str):
        try:
            return self.price[name][sku]
        except KeyError:
            try:
                for key in self.child_gm[name].keys():
                    if sku in self.child_gm[name][key].values():
                        return self.price[name][key]
            except KeyError:
                pass

    def change_group(self, campaign: str, group: str):
        self.send_message('change_group', [campaign, group])

    def change_budget(self, campaign: str, budget: float):
        self.send_message('change_budget', [campaign, budget])

    def change_strategy(self, campaign: str, strategy: str):
        self.send_message('change_strategy', [campaign, strategy])

    def change_top(self, campaign: str, top: float):
        self.send_message('change_top', [campaign, top])

    def change_page(self, campaign: str, page: float):
        self.send_message('change_page', [campaign, page])

    def change_default(self, campaign: str, default: str):
        self.send_message('change_default', [campaign, default])

    def change_keyword(self, campaign: str, keyword: str):
        self.send_message('change_keyword', [campaign, keyword])

    def change_deny(self, name: str, category: str, deny: str):
        self.send_message('change_deny', [name, category, deny])

    def change_special_deny(self, campaign: str, sign: str, deny: str):
        self.send_message('change_special_deny', [campaign, sign, deny])

    def get_campaign(self, name: str):
        return self.get_message('get_campaign', name)

    def get_season(self, audience: str, category: str, season: str):
        return self.get_message('get_season', [audience, category, season])

    def get_history(self, keyword: str):
        return self.get_message('get_history', keyword)

    def get_storage_all(self, names: str):
        return self.get_message('get_storage_all', names)

    def get_storage_detail(self, name: str, signs: str):
        return self.get_message('get_storage_detail', [name, signs])

    def get_storage_sort(self, names: str):
        return self.get_message('get_storage_sort', names)

    def get_storage_sum(self, name: str, signs: str):
        return self.get_message('get_storage_sum', [name, signs])

    def get_orders_all(self, name: str):
        return self.get_message('get_orders_all', name)

    def get_refund_all(self, name: str):
        return self.get_message('get_refund_all', name)

    def get_performance_detail(self, name: str, dates: str):
        return self.get_message('get_performance_detail', [name, dates])

    def get_performance_sum(self, names: str, dates: str):
        return self.get_message('get_performance_sum', [names, dates])

    def get_crawl(self, name: str, dates: str):
        return self.get_message('get_crawl', [name, dates])

    def get_profit_detail(self, name: str, dates: str):
        return self.get_message('get_profit_detail', [name, dates])

    def get_profit_sum(self, names: str, dates: str):
        return self.get_message('get_profit_sum', [names, dates])

    def get_targeting_ignore(self, selects: str, dates: str):
        return self.get_message('get_targeting_ignore', [selects, dates])

    def get_targeting_all(self, selects: str, dates: str):
        return self.get_message('get_targeting_all', [selects, dates])

    def get_targeting_sum(self, selects: str, dates: str):
        return self.get_message('get_targeting_sum', [selects, dates])

    def get_targeting_detail(self, selects: str, dates: str):
        return self.get_message('get_targeting_detail', [selects, dates])

    def get_search_terms_ignore(self, selects: str, dates: str):
        return self.get_message('get_search_terms_ignore', [selects, dates])

    def get_search_terms_all(self, selects: str, dates: str):
        return self.get_message('get_search_terms_all', [selects, dates])

    def get_search_terms_sum(self, selects: str, dates: str):
        return self.get_message('get_search_terms_sum', [selects, dates])

    def get_brand_analytics(self, category: str):
        return self.get_message('get_brand_analytics', category)

    def get_deny(self, name: str):
        return self.get_message('get_deny', name)

    def get_picture_asin(self):
        return self.get_message('get_picture_asin')

    def get_storage_single(self, name: str):
        return self.get_message('get_storage_single', name)

    def get_child_data(self, name: str, date: str):
        return self.get_message('get_child_data', [name, date])

    def get_non_rank_asin(self):
        return self.get_message('get_non_rank_asin')

    def get_picture_info(self, asin: str):
        return self.get_message('get_picture_info', asin)

    def add_campaign(self, campaign: str, name: str, state: str, group: str, budget: float, page: float, top: float,
                     strategy: str, default: str, keyword: str):
        self.send_message('add_campaign', [campaign, name, state, group, budget, page, top, strategy, default, keyword])

    def update_brand_analytics(self, category: str, keyword: str, rank: int, date: str):
        self.send_message('update_brand_analytics', [category, keyword, rank, date])

    def update_picture_asin(self, asin: str):
        self.send_message('update_picture_asin', asin)

    def update_targeting(self, date: str, campaign: str, group: str, targeting: str, impressions: int, clicks: int,
                         spend: float, orders: int, sales: float):
        self.send_message('update_targeting', [date, campaign, group, targeting, impressions, clicks, spend, orders,
                                               sales])

    def update_search_terms(self, date: str, campaign: str, group: str, targeting: str, search_terms: str,
                            impressions: int, clicks: int, spend: float, orders: int, sales: float):
        self.send_message('update_search_terms', [date, campaign, group, targeting, search_terms, impressions, clicks,
                                                  spend, orders, sales])

    def update_child_data(self, name: str, date: str, orders: str, refund: str):
        self.send_message('update_child_data', [name, date, orders, refund])

    def update_performance(self, name: str, date: str, sales: float, discount: float, cost: float, all_flows: int,
                           nature_flows: int, discount_orders: int, all_orders: int, ad_impressions: int, ad_flows: int,
                           ad_orders: int, ad_spend: float, ad_sales: float):
        self.send_message('update_performance', [name, date, sales, discount, cost, all_flows, nature_flows,
                                                 discount_orders, all_orders, ad_impressions, ad_flows, ad_orders,
                                                 ad_spend, ad_sales])

    def update_profit(self, name: str, date: str, quantity: int, sales: float, selling: float, fba: float,
                      coupon: float, refund: float, adjust: float, advertisement: float, storage: float,
                      disposal: float, other: float, price: float, transport: float):
        self.send_message('update_profit', [name, date, quantity, sales, selling, fba, coupon, refund, adjust,
                                            advertisement, storage, disposal, other, price, transport])

    def update_storage(self, fba_fee: str, price: float, storage_usable: int, storage_warehouse: int, storage_all: int,
                       storage_0_90: int, storage_91_180: int, storage_181_270: int, storage_271_365: int,
                       storage_365_: int, storage_fee: float, redundancy: int, name: str, sign: str):
        self.send_message('update_storage', [fba_fee, price, storage_usable, storage_warehouse, storage_all,
                                             storage_0_90, storage_91_180, storage_181_270, storage_271_365,
                                             storage_365_, storage_fee, redundancy, name, sign])

    def update_update(self, update: str):
        self.send_message('update_update', update)

    def update_picture(self, asin: str, brand: str, rank: str, number: int, rate: float, picture: str):
        self.send_message('update_picture', [asin, brand, rank, number, rate, picture])

    def update_crawl(self, name: str, date: str, nature: str, sponsored: str, rank: str, number: int, rate: float):
        self.send_message('update_crawl', [name, date, nature, sponsored, rank, number, rate])
    
    def get_fit_keyword(self, name: str):
        category = self.get_category(name)
        dict_data = self.get_information(name)
        list_fit = self.get_fit(name)
        if 'audience' in list_fit:
            list_fit.remove('audience')
            list_temp = self.audience['synonym'][dict_data['audience']]
            for audience in list_temp:
                list_fit.append(audience)
                for audisence in self.audisence['synonym'][audience]:
                    list_fit.append(audisence)
        if 'brand' in list_fit:
            list_fit.remove('brand')
            list_fit += self.brand[category]['synonym'][dict_data['brand']]
        if 'color' in list_fit:
            list_fit.remove('color')
            for color in dict_data['color']:
                list_fit += self.color['synonym'][color]
        if 'size' in list_fit:
            list_fit.remove('size')
            for size in dict_data['size']:
                list_fit += self.size[category][dict_data['audience']]['synonym'][size]
        for fit in list_fit:
            if fit in self.plural.keys():
                list_fit.append(self.plural[fit])
        return list_fit

    def get_deny_work(self, name: str):
        category = self.get_category(name)
        dict_data = self.get_information(name)
        list_deny = self.get_deny(name)[0].splitlines()
        if 'audience' in list_deny:
            list_deny.remove('audience')
            temp = self.audience['synonym'][dict_data['audience']]
            list_temp = list(set(self.audience['all']) - set(temp))
            for audience in list_temp:
                list_deny.append(audience)
                for audisence in self.audisence['synonym'][audience]:
                    list_deny.append(audisence)
        if 'brand' in list_deny:
            list_deny.remove('brand')
            list_temp = self.brand[category]['synonym'][dict_data['brand']]
            list_deny += list(set(self.brand[category]['all']) - set(list_temp))
        if 'color' in list_deny:
            list_deny.remove('color')
            list_temp = []
            for temp in dict_data['color']:
                list_temp += self.color['synonym'][temp]
            list_deny += list(set(self.color['all']) - set(list_temp))
        if 'size' in list_deny:
            list_deny.remove('size')
            list_temp = []
            for temp in dict_data['size']:
                list_temp += self.size[category][dict_data['audience']]['synonym'][temp]
            list_deny += list(set(self.size[category][dict_data['audience']]['all']) - set(list_temp))
        for deny in list_deny:
            if deny in self.plural.keys():
                list_deny.append(self.plural[deny])
        return list_deny

    def simplify_split(self, keyword, category):
        list_word = keyword.split(' ')
        list_temp = []
        for word in list_word:
            if word in list(self.plural.keys()):
                list_temp.append(self.plural[word])
            elif word in self.brand[category]['extra']:
                list_temp.append(self.brand[category]['belong'][word])
            elif word in self.audisence['all']:
                temp = self.audisence['belong'][word]
                if temp in list(self.plural.keys()):
                    temp = self.plural[temp]
                list_temp.append(temp)
            elif word not in self.no_use:
                list_temp.append(word)
        return list_temp

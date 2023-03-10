#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import pandas
import time
import json
from advertisement import assist
from object.basic import Basic
from function import function


def generate_file(basic: Basic, inputted: str, pb=None):
    upload_add = False
    column_sp = ['Product', 'Entity', 'Operation', 'Campaign Id', 'Ad Group Id', 'Portfolio Id', 'Ad Id (Read only)',
                 'Keyword Id (Read only)', 'Product Targeting Id (Read only)', 'Campaign Name', 'Ad Group Name',
                 'Start Date', 'End Date', 'Targeting Type', 'State', 'Daily Budget', 'SKU', 'Ad Group Default Bid',
                 'Bid', 'Keyword Text', 'Match Type', 'Bidding Strategy', 'Placement', 'Percentage',
                 'Product Targeting Expression']
    column_sb = ['Product', 'Entity', 'Operation', 'Campaign Id', 'Draft Campaign Id', 'Portfolio Id',
                 'Ad Group Id (Read only)', 'Keyword Id (Read only)', 'Product Targeting Id (Read only)',
                 'Campaign Name', 'Start Date', 'End Date', 'State', 'Budget Type', 'Budget', 'Bid Optimization',
                 'Bid Multiplier', 'Bid', 'Keyword Text', 'Match Type', 'Product Targeting Expression', 'Ad Format',
                 'Landing Page URL', 'Landing Page Asins', 'Brand Entity Id', 'Brand Name', 'Brand Logo Asset Id',
                 'Brand Logo URL', 'Creative Headline', 'Creative ASINs', 'Video Media Ids', 'Creative Type']
    column_sd = ['Product', 'Entity', 'Operation', 'Campaign Id', 'Portfolio Id', 'Ad Group Id', 'Ad Id (Read only)',
                 'Targeting Id (Read only)', 'Campaign Name', 'Ad Group Name', 'Start Date', 'End Date', 'State',
                 'Tactic', 'Budget Type', 'Budget', 'SKU', 'Ad Group Default Bid', 'Bid', 'Bid Optimization',
                 'Cost Type', 'Targeting Expression']
    list_store = [basic.get_store(inputted)]
    dict_product = {list_store[0]: inputted}
    if basic.have_gm(inputted):
        temp = basic.get_gm_store(inputted)
        list_store += temp
        for store in temp:
            dict_product[store] = basic.get_gm_name(inputted, store)
    if pb:
        thread = function.start_pb_thread(pb, 100, 0.1 + 0.01)
    else:
        thread = None
    for store in list_store:
        to_do = False
        date = time.strftime("%Y.%m.%d", time.localtime())
        path = basic.path[store]
        list_sp, list_sb, list_sd = [], [], []
        product = dict_product[store]
        dict_budget_now, dict_strategy_now, dict_top_now, dict_page_now, dict_default_now = {}, {}, {}, {}, {}
        dict_bid_now, dict_phrase_now, dict_exact_now, dict_asin_now = {}, {}, {}, {}
        dict_campaign_id, dict_group_id = {}, {}
        dict_row_info = {'Campaign': {}, 'Bid': {}, 'Group': {}, 'Keyword': {}, 'Exact': {}, 'Phrase': {}, 'Asin': {}}
        data_sp = pandas.read_excel('%s/bulk file.xlsx' % path, sheet_name='Sponsored Products Campaigns')
        for i in range(0, len(data_sp['Entity'])):
            entity, campaign_id, group_id = data_sp['Entity'][i], data_sp['Campaign Id'][i], data_sp['Ad Group Id'][i]
            list_temp = []
            for column in column_sp:
                if pandas.isnull(data_sp[column][i]):
                    temp = ''
                else:
                    temp = data_sp[column][i]
                list_temp.append(temp)
            if entity == 'Campaign':
                campaign_name = data_sp['Campaign Name'][i]
                if product in campaign_name:
                    to_do = True
                    dict_budget_now[campaign_name] = float(data_sp['Daily Budget'][i])
                    if data_sp['Bidding Strategy'][i] == 'Fixed bid':
                        strategy = 'FB'
                    elif data_sp['Bidding Strategy'][i] == 'Dynamic bids - down only':
                        strategy = 'DB-DO'
                    else:
                        strategy = 'DB-UAD'
                    dict_strategy_now[campaign_name] = {'All': strategy}
                    dict_campaign_id[campaign_id] = campaign_name
                    dict_default_now[campaign_name], dict_bid_now[campaign_name] = {}, {}
                    dict_exact_now[campaign_name], dict_phrase_now[campaign_name] = {}, {}
                    dict_asin_now[campaign_name] = {}
                    dict_row_info['Campaign'][campaign_name] = list_temp.copy()
                    for item in ['Bid', 'Group', 'Keyword', 'Exact', 'Phrase', 'Asin']:
                        dict_row_info[item][campaign_name] = {}
            elif campaign_id in dict_campaign_id.keys():
                campaign_name = dict_campaign_id[campaign_id]
                if entity == 'Ad Group' and data_sp['State'][i] == 'enabled':
                    group_name = data_sp['Ad Group Name'][i]
                    dict_default_now[campaign_name][group_name] = float(data_sp['Ad Group Default Bid'][i])
                    dict_group_id[group_id] = (campaign_name, group_name)
                    dict_bid_now[campaign_name][group_name] = {}
                    dict_exact_now[campaign_name][group_name] = []
                    dict_phrase_now[campaign_name][group_name] = []
                    dict_asin_now[campaign_name][group_name] = []
                    dict_row_info['Group'][campaign_name][group_name] = list_temp.copy()
                    for item in ['Keyword', 'Exact', 'Phrase', 'Asin']:
                        dict_row_info[item][campaign_name][group_name] = {}
                else:
                    if entity == 'Bidding Adjustment':
                        if data_sp['Placement'][i] == 'placementTop':
                            dict_row_info['Bid'][campaign_name]['Top'] = list_temp.copy()
                            dict_top_now[dict_campaign_id[campaign_id]] = float(data_sp['Percentage'][i])
                        elif data_sp['Placement'][i] == 'placementProductPage':
                            dict_row_info['Bid'][campaign_name]['Page'] = list_temp.copy()
                            dict_page_now[dict_campaign_id[campaign_id]] = float(data_sp['Percentage'][i])
                    elif group_id in dict_group_id.keys():
                        group_name = dict_group_id[group_id][1]
                        if entity == 'Keyword':
                            keyword = data_sp['Keyword Text'][i]
                            dict_row_info['Keyword'][campaign_name][group_name][keyword] = list_temp.copy()
                            if data_sp['State'][i] == 'enabled':
                                if not pandas.isnull(data_sp['Bid'][i]):
                                    bid = float(data_sp['Bid'][i])
                                else:
                                    bid = 'default'
                                dict_bid_now[campaign_name][group_name][keyword] = bid
                        elif entity == 'Product Targeting':
                            keyword = data_sp['Product Targeting Expression'][i]
                            if 'category' in keyword:
                                keyword = keyword.replace('category=', '').replace('"', '*').strip()
                                for key in basic.index_category.keys():
                                    keyword = keyword.replace(key, basic.index_category[key])
                            elif 'asin' in keyword:
                                keyword = keyword.replace('asin=', '').replace('"', '')
                            dict_row_info['Keyword'][campaign_name][group_name][keyword] = list_temp.copy()
                            if data_sp['State'][i] == 'enabled':
                                if not pandas.isnull(data_sp['Bid'][i]):
                                    bid = float(data_sp['Bid'][i])
                                else:
                                    bid = 'default'
                                dict_bid_now[campaign_name][group_name][keyword] = bid
                        elif entity == 'Negative Keyword':
                            deny = data_sp['Keyword Text'][i]
                            if data_sp['Match Type'][i] == 'negativeExact':
                                dict_row_info['Exact'][campaign_name][group_name][deny] = list_temp.copy()
                                if data_sp['State'][i] == 'enabled':
                                    dict_exact_now[campaign_name][group_name].append(deny)
                            elif data_sp['Match Type'][i] == 'negativePhrase':
                                dict_row_info['Phrase'][campaign_name][group_name][deny] = list_temp.copy()
                                if data_sp['State'][i] == 'enabled':
                                    dict_phrase_now[campaign_name][group_name].append(deny)
                        elif entity == 'Negative Product Targeting':
                            deny = data_sp['Product Targeting Expression'][i].replace('asin=', '').replace('"', '')
                            dict_row_info['Asin'][campaign_name][group_name][deny] = list_temp.copy()
                            if data_sp['State'][i] == 'enabled':
                                dict_asin_now[campaign_name][group_name].append(deny)
        data_sb = pandas.read_excel('%s/bulk file.xlsx' % path, sheet_name='Sponsored Brands Campaigns')
        for i in range(0, len(data_sb['Entity'])):
            entity, campaign_id = data_sb['Entity'][i], data_sb['Campaign Id'][i]
            group_id = data_sb['Ad Group Id (Read only)'][i]
            list_temp = []
            for column in column_sb:
                if pandas.isnull(data_sb[column][i]):
                    temp = ''
                else:
                    temp = data_sb[column][i]
                list_temp.append(temp)
            if entity == 'Campaign':
                campaign_name = data_sb['Campaign Name'][i]
                if product in campaign_name:
                    to_do = True
                    dict_budget_now[campaign_name] = float(data_sb['Budget'][i])
                    if data_sb['Bid Optimization'][i] == 'Auto':
                        strategy = 'A'
                    else:
                        strategy = 'M'
                    dict_strategy_now[campaign_name] = {'All': strategy}
                    if not pandas.isnull(data_sb['Bid Multiplier'][i]):
                        num = float(data_sb['Bid Multiplier'][i].replace('%', ''))
                    else:
                        num = 0.0
                    dict_top_now[campaign_name] = num
                    dict_page_now[campaign_name] = 0.0
                    dict_default_now[campaign_name] = {}
                    dict_campaign_id[campaign_id] = campaign_name
                    dict_bid_now[campaign_name] = {'': {}}
                    dict_exact_now[campaign_name], dict_phrase_now[campaign_name] = {'': []}, {'': []}
                    dict_asin_now[campaign_name] = {'': []}
                    dict_row_info['Campaign'][campaign_name] = list_temp.copy()
                    for item in ['Keyword', 'Exact', 'Phrase', 'Asin']:
                        dict_row_info[item][campaign_name] = {'': {}}
            elif campaign_id in dict_campaign_id.keys():
                campaign_name = dict_campaign_id[campaign_id]
                dict_group_id[group_id] = (campaign_name, '')
                if entity == 'Keyword':
                    keyword = data_sb['Keyword Text'][i]
                    dict_row_info['Keyword'][campaign_name][''][keyword] = list_temp.copy()
                    if data_sb['State'][i] == 'enabled':
                        if not pandas.isnull(data_sb['Bid'][i]):
                            bid = float(data_sb['Bid'][i])
                        else:
                            bid = 'default'
                        dict_bid_now[campaign_name][''][keyword] = bid
                elif entity == 'Product Targeting':
                    keyword = data_sb['Product Targeting Expression'][i]
                    if 'category' in keyword:
                        keyword = keyword.replace('category=', '').replace('"', '*').strip()
                        for key in basic.index_category.keys():
                            keyword = keyword.replace(key, basic.index_category[key])
                    elif 'asin' in keyword:
                        keyword = keyword.replace('asin=', '').replace('"', '')
                    dict_row_info['Keyword'][campaign_name][''][keyword] = list_temp.copy()
                    if data_sb['State'][i] == 'enabled':
                        if not pandas.isnull(data_sb['Bid'][i]):
                            bid = float(data_sb['Bid'][i])
                        else:
                            bid = 'default'
                        dict_bid_now[campaign_name][''][keyword] = bid
                elif entity == 'Negative Keyword':
                    deny = data_sb['Keyword Text'][i]
                    if data_sb['Match Type'][i] == 'negativeExact':
                        dict_row_info['Exact'][campaign_name][''][deny] = list_temp.copy()
                        if data_sb['State'][i] == 'enabled':
                            dict_exact_now[campaign_name][''].append(deny)
                    elif data_sb['Match Type'][i] == 'negativePhrase':
                        dict_row_info['Phrase'][campaign_name][''][deny] = list_temp.copy()
                        if data_sb['State'][i] == 'enabled':
                            dict_phrase_now[campaign_name][''].append(deny)
                elif entity == 'Negative Product Targeting':
                    deny = data_sb['Product Targeting Expression'][i].replace('asin=', '').replace('"', '')
                    dict_row_info['Asin'][campaign_name][''][deny] = list_temp.copy()
                    if data_sb['State'][i] == 'enabled':
                        dict_asin_now[campaign_name][''].append(deny)
        data_sd = pandas.read_excel('%s/bulk file.xlsx' % path, sheet_name='Sponsored Display Campaigns')
        for i in range(0, len(data_sd['Entity'])):
            entity, campaign_id, group_id = data_sd['Entity'][i], data_sd['Campaign Id'][i], data_sd['Ad Group Id'][i]
            list_temp = []
            for column in column_sd:
                if pandas.isnull(data_sd[column][i]):
                    temp = ''
                else:
                    temp = data_sd[column][i]
                list_temp.append(temp)
            if entity == 'Campaign':
                campaign_name = data_sd['Campaign Name'][i]
                if product in campaign_name:
                    to_do = True
                    dict_budget_now[campaign_name] = float(data_sd['Budget'][i])
                    dict_top_now[campaign_name] = 0.0
                    dict_page_now[campaign_name] = 0.0
                    dict_campaign_id[campaign_id] = campaign_name
                    dict_strategy_now[campaign_name] = {}
                    dict_default_now[campaign_name], dict_bid_now[campaign_name] = {}, {}
                    dict_exact_now[campaign_name], dict_phrase_now[campaign_name] = {}, {}
                    dict_asin_now[campaign_name] = {}
                    dict_row_info['Campaign'][campaign_name] = list_temp.copy()
                    for item in ['Group', 'Keyword', 'Exact', 'Phrase', 'Asin']:
                        dict_row_info[item][campaign_name] = {}
            elif campaign_id in dict_campaign_id.keys():
                campaign_name = dict_campaign_id[campaign_id]
                if entity == 'Ad Group' and data_sd['State'][i] == 'enabled':
                    group_name = data_sd['Ad Group Name'][i]
                    dict_default_now[campaign_name][group_name] = float(data_sd['Ad Group Default Bid'][i])
                    if data_sd['Bid Optimization'][i] == 'Optimize for page visits':
                        strategy = 'OPV'
                    elif data_sd['Bid Optimization'][i] == 'Optimize for conversions':
                        strategy = 'OC'
                    else:
                        strategy = 'OVI'
                    dict_strategy_now[campaign_name][group_name] = strategy
                    dict_group_id[group_id] = (campaign_name, group_name)
                    dict_bid_now[campaign_name][group_name] = {}
                    dict_exact_now[campaign_name][group_name] = []
                    dict_phrase_now[campaign_name][group_name] = []
                    dict_asin_now[campaign_name][group_name] = []
                    dict_row_info['Group'][campaign_name][group_name] = list_temp.copy()
                    for item in ['Keyword', 'Exact', 'Phrase', 'Asin']:
                        dict_row_info[item][campaign_name][group_name] = {}
                else:
                    if group_id in dict_group_id.keys():
                        group_name = dict_group_id[group_id][1]
                        if entity == 'Product Targeting':
                            keyword = data_sd['Targeting Expression'][i]
                            if 'category' in keyword:
                                keyword = keyword.replace('category=', '').replace('"', '*').strip()
                                for key in basic.index_category.keys():
                                    keyword = keyword.replace(key, basic.index_category[key])
                            elif 'asin' in keyword:
                                keyword = keyword.replace('asin=', '').replace('"', '')
                            dict_row_info['Keyword'][campaign_name][group_name][keyword] = list_temp.copy()
                            if data_sd['State'][i] == 'enabled':
                                if not pandas.isnull(data_sd['Bid'][i]):
                                    bid = float(data_sd['Bid'][i])
                                else:
                                    bid = 'default'
                                dict_bid_now[campaign_name][group_name][keyword] = bid
                        elif entity == 'Audience Targeting':
                            keyword = data_sd['Targeting Expression'][i]
                            if 'audience' in keyword:
                                keyword = keyword.replace('audience=', '').replace('"', '*').strip()
                                for key in basic.index_category.keys():
                                    keyword = keyword.replace(key, basic.index_category[key])
                            dict_row_info['Keyword'][campaign_name][group_name][keyword] = list_temp.copy()
                            if data_sd['State'][i] == 'enabled':
                                if not pandas.isnull(data_sd['Bid'][i]):
                                    bid = float(data_sd['Bid'][i])
                                else:
                                    bid = 'default'
                                dict_bid_now[campaign_name][group_name][keyword] = bid
                        elif entity == 'Negative Product Targeting' and data_sd['State'][i] == 'enabled':
                            deny = data_sd['Targeting Expression'][i].replace('asin=', '').replace('"', '')
                            dict_row_info['Asin'][campaign_name][group_name][deny] = list_temp.copy()
                            dict_asin_now[campaign_name][group_name].append(deny)
        if to_do:
            writer = pandas.ExcelWriter('%s/Upload/upload-%s-%s.xlsx' % (basic.path[store], product, date))
            name = basic.get_origin(product)
            dict_default, dict_budget, dict_strategy, dict_top, dict_page = {}, {}, {}, {}, {}
            dict_bid, dict_add, dict_delete, list_campaign = {}, {}, {}, []
            for item in basic.get_campaign(name):
                if product in item[0]:
                    dict_budget[item[0]] = float(item[3])
                    dict_strategy[item[0]] = json.loads(item[6])
                    dict_top[item[0]] = float(item[5])
                    dict_page[item[0]] = float(item[4])
                    dict_default[item[0]] = json.loads(item[9])
                    dict_bid[item[0]] = json.loads(item[10])
                    dict_add[item[0]] = json.loads(item[7])
                    dict_delete[item[0]] = json.loads(item[8])
                    list_campaign.append(item[0])
            dict_deny, index = {}, 0
            temp = basic.get_deny(name)
            for item in ['phrase', 'exact', 'asin']:
                if temp[index] is not None:
                    dict_deny[item] = temp[index].splitlines()
                else:
                    dict_deny[item] = []
                index += 1
            dict_information = basic.get_information(name)
            category = basic.get_category(name)
            audience = dict_information['audience']
            if 'audience' in dict_deny['phrase']:
                dict_deny['phrase'].remove('audience')
                dict_deny['phrase'] += list(set(basic.audience['all']) - set(
                    basic.audience['synonym'][audience]))
            if 'brand' in dict_deny['phrase']:
                dict_deny['phrase'].remove('brand')
                dict_deny['phrase'] += list(set(basic.brand[category]['all']) - set(
                    basic.brand[category]['synonym'][dict_information['brand']]))
            if 'color' in dict_deny['phrase']:
                dict_deny['phrase'].remove('color')
                list_temp = []
                for color in dict_information['color']:
                    list_temp += basic.color['synonym'][color]
                dict_deny['phrase'] += list(set(basic.color['all']) - set(list_temp))
            if 'size' in dict_deny['phrase']:
                dict_deny['phrase'].remove('size')
                list_temp = []
                for size in dict_information['size']:
                    list_temp += basic.size[category][audience]['synonym'][size]
                dict_deny['phrase'] += list(set(basic.size[category][audience]['all']) - set(list_temp))
            dict_deny['phrase'] += basic.deny[category]
            for campaign in list_campaign:
                list_group = assist.get_group(campaign, basic)
                if len(list_group) == 0:
                    list_group.append('')
                result = function.find_one(campaign, ['Exact', 'PT'])
                if result[0]:
                    sign = {'Exact': 'exact', 'PT': 'asin'}[result[1]]
                    for group in list_group:
                        for keyword in list(dict_bid[campaign][group].keys()):
                            if keyword not in dict_deny[sign]:
                                dict_deny[sign].append(keyword)
            dict_phrase, dict_exact, dict_asin = {}, {}, {}
            for campaign in list_campaign:
                dict_phrase[campaign], dict_exact[campaign], dict_asin[campaign] = {}, {}, {}
                list_group = assist.get_group(campaign, basic)
                if len(list_group) == 0:
                    list_group = ['']
                for group in list_group:
                    match = assist.get_match(campaign, group)
                    if match not in ['Exact', 'PT', 'CT', 'AT']:
                        dict_phrase[campaign][group] = dict_deny['phrase'].copy()
                        if group in dict_add[campaign]['phrase'].keys():
                            for add in dict_add[campaign]['phrase'][group]:
                                dict_phrase[campaign][group].append(add)
                        if group in dict_delete[campaign]['phrase'].keys():
                            for delete in dict_delete[campaign]['phrase'][group]:
                                dict_phrase[campaign][group].remove(delete)
                        dict_exact[campaign][group] = dict_deny['exact'].copy()
                        if group in dict_add[campaign]['exact'].keys():
                            for add in dict_add[campaign]['exact'][group]:
                                dict_exact[campaign][group].append(add)
                        if group in dict_delete[campaign]['exact'].keys():
                            for delete in dict_delete[campaign]['exact'][group]:
                                dict_exact[campaign][group].remove(delete)
                    else:
                        dict_phrase[campaign][group], dict_exact[campaign][group] = [], []
                    if match in ['Auto', 'CT']:
                        dict_asin[campaign][group] = dict_deny['asin'].copy()
                        if group in dict_add[campaign]['asin'].keys():
                            for add in dict_add[campaign]['asin'][group]:
                                dict_asin[campaign][group].append(add)
                        if group in dict_delete[campaign]['asin'].keys():
                            for delete in dict_delete[campaign]['asin'][group]:
                                dict_asin[campaign][group].remove(delete)
                    else:
                        dict_asin[campaign][group] = []
            dict_campaign_name = function.reverse_dict(dict_campaign_id)
            dict_group_name = function.reverse_dict(dict_group_id)
            for campaign in list_campaign:
                list_group = assist.get_group(campaign, basic)
                strategy = dict_strategy[campaign]
                strategy_now = dict_strategy_now[campaign]
                if list_group[0] and 'All' in strategy.keys():
                    if dict_budget[campaign] != dict_budget_now[campaign] or strategy_now != strategy:
                        if dict_budget[campaign] != dict_budget_now[campaign]:
                            dict_row_info['Campaign'][campaign][15] = dict_budget[campaign]
                        elif strategy_now != strategy:
                            if strategy['All'] == 'FB':
                                temp = 'Fixed bid'
                            elif strategy['All'] == 'DB-DO':
                                temp = 'Dynamic bids - down only'
                            else:
                                temp = 'Dynamic bids - up and down'
                            dict_row_info['Campaign'][campaign][21] = temp
                        dict_row_info['Campaign'][campaign][2] = 'Update'
                        list_sp.append(dict_row_info['Campaign'][campaign])
                    if dict_top[campaign] != dict_top_now[campaign]:
                        dict_row_info['Bid'][campaign]['Top'][23] = dict_top[campaign]
                        dict_row_info['Bid'][campaign]['Top'][2] = 'Update'
                        list_sp.append(dict_row_info['Bid'][campaign]['Top'])
                    if dict_page[campaign] != dict_page_now[campaign]:
                        dict_row_info['Bid'][campaign]['Page'][23] = dict_page[campaign]
                        dict_row_info['Bid'][campaign]['Page'][2] = 'Update'
                        list_sp.append(dict_row_info['Bid'][campaign]['Page'])
                    for group in list_group:
                        campaign_id = dict_campaign_name[campaign]
                        group_id = dict_group_name[(campaign, group)]
                        if dict_default_now[campaign][group] != dict_default[campaign][group]:
                            dict_row_info['Group'][campaign][group][17] = dict_default[campaign][group]
                            dict_row_info['Group'][campaign][group][2] = 'Update'
                            list_sp.append(dict_row_info['Group'][campaign][group])
                        if dict_bid_now[campaign][group] != dict_bid[campaign][group]:
                            list_now = list(dict_bid_now[campaign][group].keys())
                            list_need = list(dict_bid[campaign][group].keys())
                            result = function.find_add_delete(list_now, list_need)
                            if result[0]:
                                match = assist.get_match(campaign, group)
                                for keyword in result[1]:
                                    if dict_bid[campaign][group][keyword] == 'default':
                                        bid = ''
                                    else:
                                        bid = dict_bid[campaign][group][keyword]
                                    if keyword not in dict_row_info['Keyword'][campaign][group].keys():
                                        if match in ['Broad', 'Phrase', 'Exact']:
                                            match.lower()
                                            list_sp.append([
                                                'Sponsored Products', 'Keyword', 'Create', campaign_id, group_id, '',
                                                '', '', '', '', '', '', '', '', 'enabled', '', '', '', bid, keyword,
                                                match, '', '', '', ''])
                                        else:
                                            if keyword[0: 2] == 'BO':
                                                keyword = 'asin="%s"' % keyword
                                            elif '*' in keyword:
                                                keyword = 'category=%s' % keyword.replace('*', '"')
                                                for key in basic.category_index.keys():
                                                    keyword = keyword.replace(key, basic.category_index[key])
                                            list_sp.append(
                                                ['Sponsored Products', 'Product Targeting', 'Create', campaign_id,
                                                 group_id, '', '', '', '', '', '', '', '', '', 'enabled', '', '', '',
                                                 bid, '', '', '', '', '', keyword])
                                    else:
                                        dict_row_info['Keyword'][campaign][group][keyword][14] = 'enabled'
                                        dict_row_info['Keyword'][campaign][group][keyword][18] = bid
                                        dict_row_info['Keyword'][campaign][group][keyword][2] = 'Update'
                                        list_sp.append(dict_row_info['Keyword'][campaign][group][keyword])
                                for keyword in result[2]:
                                    dict_row_info['Keyword'][campaign][group][keyword][14] = 'paused'
                                    dict_row_info['Keyword'][campaign][group][keyword][2] = 'Update'
                                    list_sp.append(dict_row_info['Keyword'][campaign][group][keyword])
                            else:
                                for keyword in dict_bid[campaign][group].keys():
                                    bid = dict_bid[campaign][group][keyword]
                                    if bid != dict_bid_now[campaign][group][keyword]:
                                        if bid == 'default':
                                            bid = ''
                                        dict_row_info['Keyword'][campaign][group][keyword][18] = bid
                                        dict_row_info['Keyword'][campaign][group][keyword][2] = 'Update'
                                        list_sp.append(dict_row_info['Keyword'][campaign][group][keyword])
                        result = function.find_add_delete(dict_exact_now[campaign][group], dict_exact[campaign][group])
                        if result[0]:
                            for deny in result[1]:
                                list_sp.append([
                                    'Sponsored Products', 'Negative Keyword', 'Create', campaign_id, group_id, '', '',
                                    '', '', '', '', '', '', '', 'enabled', '', '', '', '', deny, 'negativeExact', '',
                                    '', '', ''])
                            for deny in result[2]:
                                dict_row_info['Exact'][campaign][group][deny][2] = 'Archive'
                                list_sp.append(dict_row_info['Exact'][campaign][group][deny])
                        result = function.find_add_delete(dict_phrase_now[campaign][group],
                                                          dict_phrase[campaign][group])
                        if result[0]:
                            for deny in result[1]:
                                list_sp.append([
                                    'Sponsored Products', 'Negative Keyword', 'Create', campaign_id, group_id, '', '',
                                    '', '', '', '', '', '', '', 'enabled', '', '', '', '', deny, 'negativePhrase', '',
                                    '', '', ''])
                            for deny in result[2]:
                                dict_row_info['Phrase'][campaign][group][deny][2] = 'Archive'
                                list_sp.append(dict_row_info['Phrase'][campaign][group][deny])
                        result = function.find_add_delete(dict_asin_now[campaign][group], dict_asin[campaign][group])
                        if result[0]:
                            for deny in result[1]:
                                deny = 'asin="%s"' % deny
                                list_sp.append([
                                    'Sponsored Products', 'Negative Product Targeting', 'Create', campaign_id, group_id,
                                    '', '', '', '', '', '', '', '', '', 'enabled', '', '', '', '', '', '', '', '', '',
                                    deny])
                            for deny in result[2]:
                                dict_row_info['Asin'][campaign][group][deny][2] = 'Archive'
                                list_sp.append(dict_row_info['Asin'][campaign][group][deny])
                elif not list_group[0]:
                    if dict_budget[campaign] != dict_budget_now[campaign] or strategy_now != strategy or dict_top[
                            campaign] != dict_top_now[campaign]:
                        if dict_budget[campaign] != dict_budget_now[campaign]:
                            dict_row_info['Campaign'][campaign][14] = dict_budget[campaign]
                        elif strategy_now != strategy:
                            if strategy['All'] == 'A':
                                temp = 'Auto'
                            elif strategy['All'] == 'M':
                                temp = 'Manual'
                            else:
                                temp = 'Dynamic bids - down only'
                            dict_row_info['Campaign'][campaign][15] = temp
                        elif dict_top[campaign] != dict_top_now[campaign]:
                            dict_row_info['Campaign'][campaign][16] = '{:.1%}'.format(dict_top[campaign] / 100)
                        dict_row_info['Campaign'][campaign][2] = 'Update'
                        list_sb.append(dict_row_info['Campaign'][campaign])
                    campaign_id = dict_campaign_name[campaign]
                    group_id = dict_group_name[(campaign, '')]
                    if dict_bid_now[campaign][''] != dict_bid[campaign]['']:
                        list_now = list(dict_bid_now[campaign][''].keys())
                        list_need = list(dict_bid[campaign][''].keys())
                        result = function.find_add_delete(list_now, list_need)
                        if result[0]:
                            match = assist.get_match(campaign, '')
                            for keyword in result[1]:
                                if dict_bid[campaign][''][keyword] == 'default':
                                    bid = ''
                                else:
                                    bid = dict_bid[campaign][''][keyword]
                                if keyword not in dict_row_info['Keyword'][campaign][''].keys():
                                    if match in ['Broad', 'Phrase', 'Exact']:
                                        match.lower()
                                        list_sb.append([
                                            'Sponsored Brands', 'Keyword', 'Create', campaign_id, '', '', group_id, '',
                                            '', '', '', '', 'enabled', '', '', '', '', bid, keyword, match, '', '', '',
                                            '', '', '', '', '', '', '', '', ''])
                                    else:
                                        if keyword[0: 2] == 'BO':
                                            keyword = 'asin="%s"' % keyword
                                        elif '*' in keyword:
                                            keyword = 'category=%s' % keyword.replace('*', '"')
                                            for key in basic.category_index.keys():
                                                keyword = keyword.replace(key, basic.category_index[key])
                                        list_sb.append([
                                             'Sponsored Brands', 'Product Targeting', 'Create', campaign_id, '', '',
                                             group_id, '', '', '', '', '', 'enabled', '', '', '', '', bid, '', '',
                                             keyword, '', '', '', '', '', '', '', '', '', '', ''])
                                else:
                                    dict_row_info['Keyword'][campaign][''][keyword][12] = 'enabled'
                                    dict_row_info['Keyword'][campaign][''][keyword][17] = bid
                                    dict_row_info['Keyword'][campaign][''][keyword][2] = 'Update'
                                    list_sb.append(dict_row_info['Keyword'][campaign][''][keyword])
                            for keyword in result[2]:
                                dict_row_info['Keyword'][campaign][''][keyword][12] = 'paused'
                                dict_row_info['Keyword'][campaign][''][keyword][2] = 'Update'
                                list_sb.append(dict_row_info['Keyword'][campaign][''][keyword])
                        else:
                            for keyword in dict_bid[campaign][''].keys():
                                bid = dict_bid[campaign][''][keyword]
                                if bid != dict_bid_now[campaign][''][keyword]:
                                    if bid == 'default':
                                        bid = ''
                                    dict_row_info['Keyword'][campaign][''][keyword][17] = bid
                                    dict_row_info['Keyword'][campaign][''][keyword][2] = 'Update'
                                    list_sb.append(dict_row_info['Keyword'][campaign][''][keyword])
                    result = function.find_add_delete(dict_exact_now[campaign][''], dict_exact[campaign][''])
                    if result[0]:
                        for deny in result[1]:
                            list_sb.append([
                                'Sponsored Brands', 'Negative Keyword', 'Create', campaign_id, '', '', group_id, '', '',
                                '', '', '', 'enabled', '', '', '', '', '', deny, 'negativeExact', '', '', '', '', '',
                                '', '', '', '', '', '', ''])
                        for deny in result[2]:
                            dict_row_info['Exact'][campaign][''][deny][2] = 'Archive'
                            list_sb.append(dict_row_info['Exact'][campaign][''][deny])
                    result = function.find_add_delete(dict_phrase_now[campaign][''], dict_phrase[campaign][''])
                    if result[0]:
                        for deny in result[1]:
                            list_sb.append([
                                'Sponsored Brands', 'Negative Keyword', 'Create', campaign_id, '', '', group_id, '', '',
                                '', '', '', 'enabled', '', '', '', '', '', deny, 'negativePhrase', '', '', '', '', '',
                                '', '', '', '', '', '', ''])
                        for deny in result[2]:
                            dict_row_info['Phrase'][campaign][''][deny][2] = 'Archive'
                            list_sb.append(dict_row_info['Phrase'][campaign][''][deny])
                    result = function.find_add_delete(dict_asin_now[campaign][''], dict_asin[campaign][''])
                    if result[0]:
                        for deny in result[1]:
                            deny = 'asin="%s"' % deny
                            list_sb.append([
                                'Sponsored Brands', 'Negative Product Targeting', 'Create', campaign_id, '', '',
                                group_id, '', '', '', '', '', 'enabled', '', '', '', '', '', '', '', deny, '', '', '',
                                '', '', '', '', '', '', '', ''])
                        for deny in result[2]:
                            dict_row_info['Asin'][campaign][''][deny][2] = 'Archive'
                            list_sb.append(dict_row_info['Asin'][campaign][''][deny])
                elif 'All' not in strategy.keys():
                    if dict_budget[campaign] != dict_budget_now[campaign]:
                        dict_row_info['Campaign'][campaign][15] = dict_budget[campaign]
                        dict_row_info['Campaign'][campaign][2] = 'Update'
                        list_sd.append(dict_row_info['Campaign'][campaign])
                    for group in list_group:
                        campaign_id = dict_campaign_name[campaign]
                        group_id = dict_group_name[(campaign, group)]
                        if dict_default_now[campaign][group] != dict_default[campaign][group] or strategy[
                                group] != strategy_now[group]:
                            if dict_default_now[campaign][group] != dict_default[campaign][group]:
                                dict_row_info['Group'][campaign][group][17] = dict_default[campaign][group]
                            elif strategy[group] != strategy_now[group]:
                                if strategy[group] == 'OPV':
                                    strategy_temp = 'Optimize for page visits'
                                elif strategy[group] == 'OC':
                                    strategy_temp = 'Optimize for conversions'
                                else:
                                    strategy_temp = 'Optimize for viewable impressions'
                                dict_row_info['Group'][campaign][group][19] = strategy_temp
                            dict_row_info['Group'][campaign][group][2] = 'Update'
                            list_sd.append(dict_row_info['Group'][campaign][group])
                        if dict_bid_now[campaign][group] != dict_bid[campaign][group]:
                            list_now = list(dict_bid_now[campaign][group].keys())
                            list_need = list(dict_bid[campaign][group].keys())
                            result = function.find_add_delete(list_now, list_need)
                            if result[0]:
                                match = assist.get_match(campaign, group)
                                for keyword in result[1]:
                                    if dict_bid[campaign][group][keyword] == 'default':
                                        bid = ''
                                    else:
                                        bid = dict_bid[campaign][group][keyword]
                                    if keyword not in dict_row_info['Keyword'][campaign][group].keys():
                                        if match in ['CT', 'PT']:
                                            if keyword[0: 2] == 'BO':
                                                keyword = 'asin="%s"' % keyword
                                            elif '*' in keyword:
                                                keyword = 'category=%s' % keyword.replace('*', '"')
                                                for key in basic.category_index.keys():
                                                    keyword = keyword.replace(key, basic.category_index[key])
                                            temp = 'Product Targeting'
                                        else:
                                            if '*' in keyword:
                                                keyword = 'audience=%s' % keyword.replace('*', '"')
                                                for key in basic.category_index.keys():
                                                    keyword = keyword.replace(key, basic.category_index[key])
                                        list_sd.append([
                                            'Sponsored Display', temp, 'Create', campaign_id, '', group_id, '', '',
                                            '', '', '', '', 'enabled', '', '', '', '', '', bid, '', '', keyword])
                                    else:
                                        dict_row_info['Keyword'][campaign][group][keyword][12] = 'enabled'
                                        dict_row_info['Keyword'][campaign][group][keyword][18] = bid
                                        dict_row_info['Keyword'][campaign][group][keyword][2] = 'Update'
                                        list_sd.append(dict_row_info['Keyword'][campaign][group][keyword])
                                for keyword in result[2]:
                                    dict_row_info['Keyword'][campaign][group][keyword][12] = 'paused'
                                    dict_row_info['Keyword'][campaign][group][keyword][2] = 'Update'
                                    list_sd.append(dict_row_info['Keyword'][campaign][group][keyword])
                            else:
                                for keyword in dict_bid[campaign][group].keys():
                                    bid = dict_bid[campaign][group][keyword]
                                    if bid != dict_bid_now[campaign][group][keyword]:
                                        if bid == 'default':
                                            bid = ''
                                        dict_row_info['Keyword'][campaign][group][keyword][18] = bid
                                        dict_row_info['Keyword'][campaign][group][keyword][2] = 'Update'
                                        list_sd.append(dict_row_info['Keyword'][campaign][group][keyword])
                        result = function.find_add_delete(dict_asin_now[campaign][group], dict_asin[campaign][group])
                        if result[0]:
                            for deny in result[1]:
                                deny = 'asin="%s"' % deny
                                list_sd.append([
                                    'Sponsored Display', 'Negative Product Targeting', 'Create', campaign_id, '',
                                    group_id, '', '', '', '', '', '', 'enabled', '', '', '', '', '', '', '', '', deny])
                            for deny in result[2]:
                                dict_row_info['Asin'][campaign][group][deny][2] = 'Archive'
                                list_sd.append(dict_row_info['Asin'][campaign][group][deny])
            final_sp = pandas.DataFrame(columns=column_sp, data=list_sp)
            final_sp.to_excel(writer, index=False, sheet_name='Sponsored Products Campaigns')
            final_sb = pandas.DataFrame(columns=column_sb, data=list_sb)
            final_sb.to_excel(writer, index=False, sheet_name='Sponsored Brands Campaigns')
            final_sd = pandas.DataFrame(columns=column_sd, data=list_sd)
            final_sd.to_excel(writer, index=False, sheet_name='Sponsored Display Campaigns')
            writer.save()
    if pb:
        function.stop_thread(thread)
        pb.setValue(100)
    return upload_add

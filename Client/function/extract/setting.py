#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
import pandas
from object.basic import Basic
from function import function
from advertisement import assist


def extract_setting(need: str, basic: Basic):
    dict_budget, dict_top, dict_page, dict_default, dict_bid_on, dict_strategy = {}, {}, {}, {}, {}, {}
    dict_campaign, dict_group = {}, {}
    store = basic.get_store(need)
    list_path = [basic.path[store]]
    list_campaign = assist.get_campaign(need, basic, 'all')
    list_product = [need]
    if basic.have_gm(need):
        list_store = basic.get_gm_store(need)
        for store in list_store:
            list_path.append(basic.path[store])
            list_campaign += assist.get_campaign(basic.get_gm_name(need, store), basic, 'all')
            list_product += basic.get_gm_name(need)
    for path in list_path:
        data_sp = pandas.read_excel('%s/bulk file.xlsx' % path, sheet_name='Sponsored Products Campaigns')
        dict_campaign_id, dict_group_id = {}, {}
        for i in range(0, len(data_sp['Entity'])):
            entity, campaign_id, group_id = data_sp['Entity'][i], data_sp['Campaign Id'][i], data_sp['Ad Group Id'][i]
            if entity == 'Campaign':
                campaign_name = data_sp['Campaign Name'][i]
                result = function.find_one(campaign_name, list_product)
                if result[0]:
                    if campaign_name not in list_campaign:
                        if data_sp['State'][i] == 'enabled':
                            state = 'on'
                        else:
                            state = 'off'
                        dict_campaign[campaign_name] = (need, state)
                    dict_budget[campaign_name] = float(data_sp['Daily Budget'][i])
                    if data_sp['Bidding Strategy'][i] == 'Fixed bid':
                        strategy = 'FB'
                    elif data_sp['Bidding Strategy'][i] == 'Dynamic bids - down only':
                        strategy = 'DB-DO'
                    else:
                        strategy = 'DB-UAD'
                    dict_strategy[campaign_name] = {'All': strategy}
                    dict_campaign_id[campaign_id] = campaign_name
                    dict_group[campaign_name], dict_default[campaign_name], dict_bid_on[campaign_name] = [], {}, {}
            elif campaign_id in dict_campaign_id.keys():
                campaign_name = dict_campaign_id[campaign_id]
                if entity == 'Ad Group' and data_sp['State'][i] == 'enabled':
                    group_name = data_sp['Ad Group Name'][i]
                    dict_group[campaign_name].append(group_name)
                    dict_default[campaign_name][group_name] = float(data_sp['Ad Group Default Bid'][i])
                    dict_group_id[group_id] = group_name
                    dict_bid_on[campaign_name][group_name] = {}
                else:
                    if entity == 'Bidding Adjustment':
                        if data_sp['Placement'][i] == 'placementTop':
                            dict_top[dict_campaign_id[campaign_id]] = float(data_sp['Percentage'][i])
                        elif data_sp['Placement'][i] == 'placementProductPage':
                            dict_page[dict_campaign_id[campaign_id]] = float(data_sp['Percentage'][i])
                    elif group_id in dict_group_id.keys():
                        group_name = dict_group_id[group_id]
                        if entity == 'Keyword' and data_sp['State'][i] == 'enabled':
                            if not pandas.isnull(data_sp['Bid'][i]):
                                bid = float(data_sp['Bid'][i])
                            else:
                                bid = 'default'
                            dict_bid_on[campaign_name][group_name][data_sp['Keyword Text'][i]] = bid
                        elif entity == 'Product Targeting' and data_sp['State'][i] == 'enabled':
                            keyword = data_sp['Product Targeting Expression'][i]
                            if 'category' in keyword:
                                keyword = keyword.replace('category=', '').replace('"', '*').strip()
                                for key in basic.index_category.keys():
                                    keyword = keyword.replace(key, basic.index_category[key])
                            elif 'asin' in keyword:
                                keyword = keyword.replace('asin=', '').replace('"', '')
                            if not pandas.isnull(data_sp['Bid'][i]):
                                bid = float(data_sp['Bid'][i])
                            else:
                                bid = 'default'
                            dict_bid_on[campaign_name][group_name][keyword] = bid
        data_sb = pandas.read_excel('%s/bulk file.xlsx' % path, sheet_name='Sponsored Brands Campaigns')
        dict_campaign_id = {}
        for i in range(0, len(data_sb['Entity'])):
            entity, campaign_id = data_sb['Entity'][i], data_sb['Campaign Id'][i]
            if entity == 'Campaign':
                campaign_name = data_sb['Campaign Name'][i]
                result = function.find_one(campaign_name, list_product)
                if result[0]:
                    if campaign_name not in list_campaign:
                        if data_sb['State'][i] == 'enabled':
                            state = 'on'
                        else:
                            state = 'off'
                        dict_campaign[campaign_name] = (need, state)
                    dict_group[campaign_name] = []
                    dict_budget[campaign_name] = float(data_sb['Budget'][i])
                    if data_sb['Bid Optimization'][i] == 'Auto':
                        strategy = 'A'
                    else:
                        strategy = 'M'
                    dict_strategy[campaign_name] = {'All': strategy}
                    if not pandas.isnull(data_sb['Bid Multiplier'][i]):
                        num = float(data_sb['Bid Multiplier'][i].replace('%', ''))
                    else:
                        num = 0.0
                    dict_top[campaign_name] = num
                    dict_page[campaign_name] = 0.0
                    dict_default[campaign_name] = {}
                    dict_campaign_id[campaign_id] = campaign_name
                    dict_bid_on[campaign_name] = {'': {}}
            elif campaign_id in dict_campaign_id.keys():
                campaign_name = dict_campaign_id[campaign_id]
                if entity == 'Keyword' and data_sb['State'][i] == 'enabled':
                    if not pandas.isnull(data_sb['Bid'][i]):
                        bid = float(data_sb['Bid'][i])
                    else:
                        bid = 'default'
                    dict_bid_on[campaign_name][''][data_sb['Keyword Text'][i]] = bid
                elif entity == 'Product Targeting' and data_sb['State'][i] == 'enabled':
                    keyword = data_sb['Product Targeting Expression'][i]
                    if 'category' in keyword:
                        keyword = keyword.replace('category=', '').replace('"', '*').strip()
                        for key in basic.index_category.keys():
                            keyword = keyword.replace(key, basic.index_category[key])
                    elif 'asin' in keyword:
                        keyword = keyword.replace('asin=', '').replace('"', '')
                    if not pandas.isnull(data_sb['Bid'][i]):
                        bid = float(data_sb['Bid'][i])
                    else:
                        bid = 'default'
                    dict_bid_on[campaign_name][''][keyword] = bid
        data_sd = pandas.read_excel('%s/bulk file.xlsx' % path, sheet_name='Sponsored Display Campaigns')
        dict_campaign_id, dict_group_id = {}, {}
        for i in range(0, len(data_sd['Entity'])):
            entity, campaign_id, group_id = data_sd['Entity'][i], data_sd['Campaign Id'][i], data_sd['Ad Group Id'][i]
            if entity == 'Campaign':
                campaign_name = data_sd['Campaign Name'][i]
                result = function.find_one(campaign_name, list_product)
                if result[0]:
                    if campaign_name not in list_campaign:
                        if data_sd['State'][i] == 'enabled':
                            state = 'on'
                        else:
                            state = 'off'
                        dict_campaign[campaign_name] = (need, state)
                    dict_budget[campaign_name] = float(data_sd['Budget'][i])
                    dict_top[campaign_name] = 0.0
                    dict_page[campaign_name] = 0.0
                    dict_campaign_id[campaign_id] = campaign_name
                    dict_strategy[campaign_name] = {}
                    dict_group[campaign_name], dict_default[campaign_name], dict_bid_on[campaign_name] = [], {}, {}
            elif campaign_id in dict_campaign_id.keys():
                campaign_name = dict_campaign_id[campaign_id]
                if entity == 'Ad Group' and data_sd['State'][i] == 'enabled':
                    group_name = data_sd['Ad Group Name'][i]
                    dict_group[campaign_name].append(group_name)
                    dict_default[campaign_name][group_name] = float(data_sd['Ad Group Default Bid'][i])
                    if data_sd['Bid Optimization'][i] == 'Optimize for page visits':
                        strategy = 'OPV'
                    elif data_sd['Bid Optimization'][i] == 'Optimize for conversions':
                        strategy = 'OC'
                    else:
                        strategy = 'OVI'
                    dict_strategy[campaign_name][group_name] = strategy
                    dict_group_id[group_id] = group_name
                    dict_bid_on[campaign_name][group_name] = {}
                else:
                    if group_id in dict_group_id.keys():
                        group_name = dict_group_id[group_id]
                        if entity == 'Contextual Targeting' and data_sd['State'][i] == 'enabled':
                            keyword = data_sd['Targeting Expression'][i]
                            if 'category' in keyword:
                                keyword = keyword.replace('category=', '').replace('"', '*').strip()
                                for key in basic.index_category.keys():
                                    keyword = keyword.replace(key, basic.index_category[key])
                            elif 'asin' in keyword:
                                keyword = keyword.replace('asin=', '').replace('"', '')
                            if not pandas.isnull(data_sd['Bid'][i]):
                                bid = float(data_sd['Bid'][i])
                            else:
                                bid = 'default'
                            dict_bid_on[campaign_name][group_name][keyword] = bid
                        elif entity == 'Audience Targeting' and data_sd['State'][i] == 'enabled':
                            keyword = data_sd['Targeting Expression'][i]
                            if 'audience' in keyword:
                                keyword = keyword.replace('audience=', '').replace('"', '*').strip()
                                for key in basic.index_category.keys():
                                    keyword = keyword.replace(key, basic.index_category[key])
                            if not pandas.isnull(data_sd['Bid'][i]):
                                bid = float(data_sd['Bid'][i])
                            else:
                                bid = 'default'
                            dict_bid_on[campaign_name][group_name][keyword] = bid
    for campaign in list_campaign:
        temp = function.connect(dict_group[campaign], '\n')
        basic.change_group(campaign, temp)
        basic.change_budget(campaign, dict_budget[campaign])
        basic.change_top(campaign, dict_top[campaign])
        basic.change_page(campaign, dict_page[campaign])
        temp = json.dumps(dict_strategy[campaign])
        basic.change_strategy(campaign, temp)
        temp = json.dumps(dict_default[campaign])
        basic.change_default(campaign, temp)
        temp = json.dumps(dict_bid_on[campaign])
        basic.change_keyword(campaign, temp)
    for campaign in dict_campaign.keys():
        basic.add_campaign(campaign, dict_campaign[campaign][0], dict_campaign[campaign][1],
                           function.connect(dict_group[campaign], '\n'), dict_budget[campaign], dict_top[campaign],
                           dict_page[campaign], json.dumps(dict_strategy[campaign]), json.dumps(dict_default[campaign]),
                           json.dumps(dict_bid_on[campaign]))
    basic.commit()

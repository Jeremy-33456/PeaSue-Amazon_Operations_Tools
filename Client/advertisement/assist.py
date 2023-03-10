#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

from function import function
from object.basic import Basic


def get_campaign(name: str, basic: Basic, state: str = 'on'):
    try:
        temp = basic.campaign[name][state]
    except KeyError:
        temp = []
    return temp


def get_group(campaign: str, basic: Basic):
    if campaign:
        try:
            return basic.group[campaign]
        except KeyError:
            return []
    else:
        return []


def get_match(campaign: str, group: str):
    temp = '%s-%s' % (campaign, group)
    if '-Auto' in temp:
        match = 'Auto'
    elif '-Broad' in temp:
        match = 'Broad'
    elif '-Phrase' in temp:
        match = 'Phrase'
    elif '-Exact' in temp:
        match = 'Exact'
    elif '-PT' in temp:
        match = 'PT'
    elif '-CT' in temp:
        match = 'CT'
    else:
        match = 'AT'
    return match


def get_traffic(campaign: str, group: str):
    temp = '%s-%s' % (campaign, group)
    if 'LT' in temp:
        traffic = 'Low'
    elif 'MT' in temp:
        traffic = 'Medium'
    elif 'HT' in temp:
        traffic = 'High'
    else:
        traffic = 'Undefined'
    return traffic


def get_bid(campaign: str, group: str):
    temp = '%s-%s' % (campaign, group)
    if 'LB' in temp:
        bid = 'Low'
    elif 'MB' in temp:
        bid = 'Medium'
    elif 'HB' in temp:
        bid = 'High'
    else:
        bid = 'Undefined'
    return bid


def get_variation(campaign: str, group: str, all_variation: list):
    temp = '%s-%s' % (campaign, group)
    result = function.find_one(temp, all_variation)
    if result[0]:
        variation = result[1]
    else:
        variation = 'Undefined'
    return variation


def get_special(name: str, campaign: str, group: str, all_variation: list):
    temp = '%s-%s' % (campaign, group)
    list_temp = temp.split('-')
    for i in range(len(list_temp) - 1, -1, -1):
        if list_temp[i] in [name, 'Auto', 'Manual', 'Broad', 'Phrase', 'Exact', 'PT', 'CT', 'AT', 'LT', 'MT', 'HT',
                            'LB', 'MB', 'HB'] + all_variation:
            del list_temp[i]
    if len(list_temp) == 0:
        special = ['Normal']
    else:
        special = list_temp
    return special


def match_sort(group: list):
    new = []
    old = []
    list_all = ['Unexact', 'Auto', 'Sketchy', 'Broad', 'Phrase', 'Exact', 'PT', 'CT', 'AT']
    for item1 in list_all:
        for item2 in group:
            if item2.find(item1) != -1:
                new.append(item2)
            else:
                old.append(item2)
    old.sort()
    for item in old:
        if item not in new:
            new.append(item)
    return new

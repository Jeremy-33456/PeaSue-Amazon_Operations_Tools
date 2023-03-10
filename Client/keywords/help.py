#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

def prepare(text: str, category: str):
    import re
    text = text.lower()
    if text.find(',') != -1:
        text = text.replace(',', '')
    if text.find('#') != -1:
        text = text.replace('#', '')
    if text.find('+') != -1:
        text = text.replace('+', ' ')
    if text.find('/') != -1:
        text = text.replace('/', ' ')
    if category == 'slipper':
        if text.find('-') != -1:
            text = text.replace(' - ', '-')
            text = text.replace('- ', '-')
            text = text.replace(' -', '-')
        if text.find(' to ') != -1:
            text = text.replace(' to ', '-')
        if text.find('size') != -1 or text.find('sz') != -1:
            text = text.replace('sz', 'size')
            text = text.replace('size ', 'size')
            result = re.search('size\\d+(\\.\\d+)?-\\d+(\\.\\d+)?', text)
            try:
                text = text.replace(result.group(), '%size')
            except AttributeError:
                result = re.search('size\\d+(\\.\\d+)? \\d+(\\.\\d+)?', text)
                try:
                    text = text.replace(result.group(), '%size')
                except AttributeError:
                    result = re.search('size\\d+(\\.\\d+)?[ctwm]', text)
                    try:
                        text = text.replace(result.group(), '%size')
                    except AttributeError:
                        result = re.search('size\\d+(\\.\\d+)?', text)
                        try:
                            text = text.replace(result.group(), '%size')
                        except AttributeError:
                            pass
        if text.find('year') != -1 or text.find('yr') != -1:
            text = text.replace('yr', 'year')
            text = text.replace('years', 'year')
            text = text.replace('year old', 'year')
            text = text.replace(' year', 'year')
            result = re.search('\\d+(\\.\\d+)?-\\d+(\\.\\d+)?year', text)
            try:
                text = text.replace(result.group(), '%year')
            except AttributeError:
                result = re.search('\\d+(\\.\\d+)? \\d+(\\.\\d+)?year', text)
                try:
                    text = text.replace(result.group(), '%year')
                except AttributeError:
                    result = re.search('\\d+(\\.\\d+)?year', text)
                    try:
                        text = text.replace(result.group(), '%year')
                    except AttributeError:
                        pass
        elif text.find('age') != -1:
            text = text.replace('age ', 'age')
            result = re.search('age\\d+(\\.\\d+)?-\\d+(\\.\\d+)?', text)
            try:
                text = text.replace(result.group(), '%year')
            except AttributeError:
                result = re.search('age\\d+(\\.\\d+)? \\d+(\\.\\d+)?', text)
                try:
                    text = text.replace(result.group(), '%year')
                except AttributeError:
                    result = re.search('age\\d+(\\.\\d+)?', text)
                    try:
                        text = text.replace(result.group(), '%year')
                    except AttributeError:
                        pass
        result = re.search('\\d+(\\.\\d+)?-\\d+(\\.\\d+)?', text)
        try:
            text = text.replace(result.group(), '%size')
        except AttributeError:
            result = re.search('\\d+(\\.\\d+)? \\d+(\\.\\d+)?', text)
            try:
                text = text.replace(result.group(), '%size')
            except AttributeError:
                result = re.search('\\d+(\\.\\d+)?[ctwm]', text)
                try:
                    if result.group()[-1:] == 'y':
                        text = text.replace(result.group(), '%year')
                    elif result.group()[-1:] == 't':
                        if float(result.group()[0: -1]) > 4:
                            text = text.replace(result.group(), '%size')
                        else:
                            text = text.replace(result.group(), '%year')
                    else:
                        text = text.replace(result.group(), '%size')
                except AttributeError:
                    result = re.search('\\d+(\\.\\d+)?', text)
                    try:
                        text = text.replace(result.group(), '%size')
                    except AttributeError:
                        pass
    if text.find('    ') != -1:
        text = text.replace('    ', ' ')
    if text.find('   ') != -1:
        text = text.replace('   ', ' ')
    if text.find('  ') != -1:
        text = text.replace('  ', ' ')
    return text.strip()

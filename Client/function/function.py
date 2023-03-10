#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import json
import pandas
import ctypes
import chardet
import datetime
import threading
from function.poster import delay
from PyQt5.QtWidgets import QApplication


def choice(a: str, b: int, c: int):
    result = b
    while True:
        try:
            result = int(input(a))
        except ValueError:
            print('输入有误，请重新输入！')
        if b < result < c:
            return result


def read_clipboard():
    clipboard = QApplication.clipboard()
    return clipboard.text()


def to_clipboard(text: str or list):
    clipboard = QApplication.clipboard()
    if isinstance(text, str):
        clipboard.setText(text)
    else:
        list_text = []
        for item in text:
            if isinstance(item, list):
                list_text.append(connect(item, '\t'))
            else:
                list_text.append(item)
        clipboard.setText(connect(list_text, '\n'))


def get_day(start: str, end: str or int):
    date_list = [start]
    if isinstance(end, str):
        start = datetime.datetime.strptime(start, "%Y.%m.%d")
        end = datetime.datetime.strptime(end, "%Y.%m.%d")
        while start < end:
            start += datetime.timedelta(days=1)
            date_list.append(start.strftime("%Y.%m.%d"))
        return date_list
    else:
        start = datetime.datetime.strptime(start, "%Y.%m.%d")
        for i in range(0, end):
            start += datetime.timedelta(days=1)
            date_list.append(start.strftime("%Y.%m.%d"))
        return date_list


def find_one(string: str, group: list):
    for item in group:
        if ' ' not in string or ' ' in item:
            if string.find(item) != -1:
                return True, item
        else:
            for temp in string.split(' '):
                if item == temp:
                    return True, item
    return False, ''


def find_all(group: list, string: str):
    list_item = []
    for item in group:
        if item.find(string) != -1:
            list_item.append(item)
    if len(list_item) > 0:
        return True, list_item
    else:
        return False, []


def find_add_delete(old: list, new: list):
    list_add = []
    for item in new:
        if item not in old:
            list_add.append(item)
    list_delete = []
    for item in old:
        if item not in new:
            list_delete.append(item)
    if len(list_add) == 0 and len(list_delete) == 0:
        return False, [], []
    else:
        return True, list_add, list_delete


def find_cross_element(list_old: list, list_new: list):
    if len(list_old) == 0:
        list_result = list_new.copy()
    elif len(list_new) == 0:
        list_result = list_old.copy()
    else:
        list_temp = []
        for item in list_old:
            if item in list_new:
                list_temp.append(item)
        list_result = list_temp.copy()
    return list_result


def sum_value(dict_data: dict):
    count = 0
    for item in dict_data.keys():
        count += dict_data[item]
    return count


def operate_add_delete(list_all: list, list_add: list, list_delete: list):
    list_result = list_all.copy()
    for item in list_add:
        if item not in list_result:
            list_result.append(item)
    for item in list_delete:
        try:
            list_result.remove(item)
        except ValueError:
            pass
    return list_result


def connect(list_all: list, sign: str):
    result = ''
    if len(list_all) == 1:
        result += list_all[0]
    elif len(list_all) > 1:
        for i in range(0, len(list_all) - 1):
            if list_all[i].strip():
                result += list_all[i].strip() + sign
        if list_all[-1].strip():
            result += list_all[-1].strip()
        else:
            if result[-1 * len(sign):] == sign:
                result = result[0: -1 * len(sign)]
    return result


def progress_move(pb, max_value: int, step: float = 0.1):
    start = pb.value()
    while True:
        start += 1
        pb.setValue(start)
        delay(step, step)
        if start == max_value - 1:
            return


def start_pb_thread(pb, number: int, step: float = 0):
    if step:
        thread = threading.Thread(target=progress_move, args=(pb, number, step))
    else:
        thread = threading.Thread(target=progress_move, args=(pb, number,))
    thread.setDaemon(True)
    thread.start()
    return thread


def stop_thread(thread):
    tid = ctypes.c_long(thread.ident)
    ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(SystemExit))


def read_file(file_name: str):
    suffix = file_name[-4:]
    if suffix in ['.txt']:
        return open(file_name, 'r').read().splitlines()
    elif suffix == 'json':
        return json.load(open(file_name, 'r'))


def write_file(content: str or dict, path: str):
    if isinstance(content, dict):
        with open(path, 'wt') as f:
            f.write(json.dumps(content, indent=4))
    elif isinstance(content, str):
        with open(path, 'wt') as f:
            f.write(content)


def open_txt_as_chart(path: str, sep: str = None):
    dector = chardet.universaldetector.UniversalDetector()
    dector.feed(open(path, 'rb+').read())
    dector.close()
    encode_type = dector.result['encoding']
    if sep is not None:
        result = pandas.read_csv(path, sep='\t', encoding=encode_type)
    else:
        result = pandas.read_csv(path, encoding=encode_type)
    return result


def reverse_dict(dict_input: dict):
    dict_output = {}
    list_value = list(dict_input.values())
    for i in range(0, len(list_value)):
        temp = list(dict_input.keys())[i]
        dict_output[list_value[i]] = temp
    return dict_output


def sort_dict_key(dict_power: dict, reverse: bool = False):
    list_word = sorted(dict_power.items(), key=lambda item: item[1], reverse=reverse)
    return list_word

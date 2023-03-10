#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author : JLM

import wmi
import json
import base64
import socket
import configparser
from object import interface
from function import function
from object import basic, tableview, combobox, date
from product import calculate
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog


class Information(QMainWindow, interface.Ui_PeaSue):
    def __init__(self):
        super(Information, self).__init__()
        try:
            conf = configparser.ConfigParser()
            conf.read('setting.ini')
            ip = conf.get('basic', 'ip')
            port = conf.get('basic', 'port')
            user = conf.get('basic', 'user')
        except (configparser.NoSectionError, configparser.NoOptionError):
            QMessageBox.information(self, '提示', '无法找到配置文件或格式有误', QMessageBox.Yes)
            ip, port, user = '', '', ''
            exit()
        device_id = wmi.WMI().Win32_BaseBoard()[0].SerialNumber
        secret = base64.b64encode(device_id.encode('ansi')).decode('ansi')
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.connect((ip, int(port)))
        conn_socket.send(json.dumps(['verify_secret', user, secret]).encode('utf-8'))
        recv_data = conn_socket.recv(1024).decode('utf-8')
        if recv_data == 'ERROR':
            password, judge = QInputDialog.getText(self, '提示', '请输入密码：')
            if not judge:
                exit()
            conn_socket.send(json.dumps(['verify_password', user, password]).encode('utf-8'))
            recv_data = conn_socket.recv(1024).decode('utf-8')
            if recv_data != 'ERROR':
                session = recv_data
            else:
                session = ''
                exit()
        elif recv_data == 'REPEAT':
            QMessageBox.information(self, '提示', '重复登录', QMessageBox.Yes)
            session = ''
            exit()
        else:
            session = recv_data
        self.basic = basic.Basic(session, conn_socket)
        self.setupUi(self)
        self.storage_information = tableview.TableView(self.table1_information, 'storage', 'information',
                                                       self.basic.power, output=self.output_storage)
        self.chart_information = tableview.TableView(self.table2_information, 'chart', 'information', self.basic.power)
        self.ship_information = tableview.TableView(self.table3_information, 'ship', 'information', self.basic.power)
        self.date_information = date.Date(self.date1_information, self.date2_information, self.range_information,
                                          self.choice_information, 'information', self.basic)
        self.product_information.currentIndexChanged.connect(self.variation_change_information)
        self.product_information.currentIndexChanged.connect(
            lambda: self.date_information.refresh(self.product_information.currentText()))
        self.variation_information.currentIndexChanged.connect(self.show_data_information)
        self.analyse_information.clicked.connect(self.show_chart_information)
        self.product_information.addItems(['All'] + self.basic.product_list)
        self.choice_information.addItems(['补货', '退货率', '库销比'])
        from PyQt5.QtGui import QPalette
        self.palette_red = QPalette()
        from PyQt5.QtCore import Qt
        self.palette_red.setColor(QPalette.WindowText, Qt.red)
        self.label_update_information.setPalette(self.palette_red)
        self.update_information.setPalette(self.palette_red)

    def variation_change_information(self):
        name = self.product_information.currentText()
        if name == 'All':
            self.label_42.hide()
            self.variation_information.hide()
            combobox.clear(self.variation_information)
        else:
            self.label_42.show()
            self.variation_information.show()
            self.label_42.setText(self.basic.variation1[self.basic.get_category(name)])
            dict_child = self.basic.get_sign(name)
            list_variation = []
            for child in list(dict_child.keys()):
                variation = dict_child[child].split('|')[0].title()
                if variation not in list_variation:
                    list_variation.append(variation)
            if len(list_variation) > 1:
                list_variation.insert(0, 'All')
            combobox.reset_value(self.variation_information, list_variation)

    def show_data_information(self):
        name = self.product_information.currentText()
        header = ['SKU', '售价', '折扣类型', '折扣', '成交价', '尾程费', '仓储费', '可售库存', '在库库存', '在途库存',
                  '总库存', '0-90', '91-180', '181-270', '271-365', '365+', '冗余']
        if name == 'All':
            name = function.connect(self.basic.product_list, ',')
            variation, variation1, variation2 = '', '', ''
            header[0] = '产品'
        else:
            variation1 = self.basic.variation1[self.basic.get_category(name)]
            try:
                variation2 = self.basic.variation2[self.basic.get_category(name)]
            except KeyError:
                variation2 = ''
            if variation2:
                header.insert(1, variation2)
            variation = self.variation_information.currentText()
            if variation == 'All':
                header.insert(1, variation1)
        list_all = calculate.count_storage(name, header, variation, self.basic, variation1, variation2)
        self.storage_information.set_content(list_all, header, ['sum'])
        self.update_information.setText(self.basic.update)

    def show_chart_information(self):
        list_date = self.date_information.list_date
        if len(list_date) > 0:
            name = self.product_information.currentText()
            dict_sign = self.basic.get_sign(name)
            list_child = self.storage_information.get_content_column(0)[0: -1]
            choice = self.choice_information.currentText()
            if choice == '补货':
                header = ['SKU', '订单', '季节因子', '补货数']
            elif choice == '退货率':
                header = ['SKU', '订单', '退货', '退货率']
            else:
                header = ['SKU', '订单', '在库库销比', '总库销比']
            dict_data = {'orders': {}, 'refund': {}}
            for child in list_child:
                dict_data['orders'][child] = 0
            for item in self.basic.get_orders_all(name):
                if item[0] in list_date and len(json.loads(item[1])) > 0:
                    for child in list_child:
                        try:
                            dict_data['orders'][child] += json.loads(item[1])[dict_sign[child]]
                        except KeyError:
                            pass
            if choice == '退货率':
                for child in list_child:
                    dict_data['refund'][child] = 0
                for item in self.basic.get_refund_all(name):
                    if item[0] in list_date and len(json.loads(item[1])) > 0:
                        for child in list_child:
                            try:
                                dict_data['refund'][child] += json.loads(item[1])[dict_sign[child]]
                            except KeyError:
                                pass
            storage = self.storage_information.get_content_by_header(['在库库存', '总库存'], 'int')
            temp1, temp2 = [], []
            for item in storage:
                temp1.append(item[0])
                temp2.append(item[1])
            list_all = calculate.count_data(choice, list_date, list_child, dict_data, [temp1, temp2])
            self.chart_information.set_content(list_all, header, ['sum'])
        else:
            QMessageBox.information(self, '失败', '无数据可用', QMessageBox.Yes)

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author : JLM

import wmi
import json
import base64
import socket
import threading
import configparser
from PyQt5.QtCore import Qt, pyqtSignal
from object.basic import Basic
from PyQt5.QtWidgets import QApplication
from object.interface2 import Ui_Importer
from PyQt5.QtWidgets import QMainWindow, QInputDialog, QDesktopWidget, QMessageBox


class MyWindow(QMainWindow, Ui_Importer):
    print_text = pyqtSignal(str)

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height() - 40) / 2))
        self.command0.clicked.connect(self.stop_session)
        self.command1.clicked.connect(self.reload)
        self.command2.clicked.connect(self.refresh)
        self.command3.clicked.connect(self.position_crawl)
        self.command4.clicked.connect(self.picture_crawl)
        self.command5.clicked.connect(self.extract_storage)
        self.command6.clicked.connect(self.extract_performance)
        self.command7.clicked.connect(self.extract_data)
        self.command8.clicked.connect(self.extract_profit)
        self.command9.clicked.connect(self.extract_brand)
        self.printer.textChanged.connect(self.auto_roll)
        self.print_text.connect(self.update_printer)
        self.scroll = 0
        try:
            conf = configparser.ConfigParser()
            conf.read('setting.ini')
            ip = conf.get('basic', 'ip')
            port = conf.get('basic', 'port')
        except (configparser.NoSectionError, configparser.NoOptionError):
            QMessageBox.information(self, '提示', '无法找到配置文件或格式有误', QMessageBox.Yes)
            ip, port = '', ''
            exit()
        device_id = wmi.WMI().Win32_BaseBoard()[0].SerialNumber
        secret = base64.b64encode(device_id.encode('ansi')).decode('ansi')
        conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_socket.connect((ip, int(port)))
        conn_socket.send(json.dumps(['verify_secret', 'manager', secret]).encode('utf-8'))
        recv_data = conn_socket.recv(1024).decode('utf-8')
        if recv_data == 'ERROR':
            password, judge = QInputDialog.getText(self, '提示', '请输入密码：')
            if not judge:
                exit()
            conn_socket.send(json.dumps(['verify_password', 'manager', password]).encode('utf-8'))
            recv_data = conn_socket.recv(1024).decode('utf-8')
            if recv_data != 'ERROR':
                session = recv_data
            else:
                session = ''
                exit()
        else:
            session = recv_data
        self.basic = Basic(session, conn_socket)

    def auto_roll(self):
        if self.printer.verticalScrollBar().value() >= self.scroll:
            self.printer.moveCursor(self.printer.textCursor().End)
        self.scroll = self.printer.verticalScrollBar().maximum() - 4

    def update_printer(self, text: str):
        self.printer.append(text)

    def stop_session(self):
        sessions = self.basic.get_message('get_all_session')
        user, judge = QInputDialog.getItem(self, '提示', '请选择会话：', sessions)
        if judge:
            self.print_text.emit('结束会话：%s' % user)
            self.basic.send_message('stop_session', user.split('-')[0])

    def reload(self):
        try:
            self.basic.send_message('reload')
            self.print_text.emit('成功进行云端刷新')
        except Exception as ex:
            self.print_text.emit('云端刷新失败：%s' % ex)
    
    def refresh(self):
        try:
            self.basic.send_message('update_connection')
            self.basic.get_basic()
            self.print_text.emit('成功进行本地刷新')
        except Exception as ex:
            self.print_text.emit('本地刷新失败：%s' % ex)

    def position_crawl(self):
        from function.position_crawl import crawl_position
        t1 = threading.Thread(target=crawl_position, args=(self.basic, self.print_text))
        t1.setDaemon(True)
        t1.start()

    def picture_crawl(self):
        from function.picture_crawl import crawl_picture
        t2 = threading.Thread(target=crawl_picture, args=(self.basic, self.print_text))
        t2.setDaemon(True)
        t2.start()

    def extract_storage(self):
        from function.extract.storage import extract_storage
        t3 = threading.Thread(target=extract_storage, args=(self.basic, self.print_text))
        t3.setDaemon(True)
        t3.start()

    def extract_performance(self):
        from function.extract.performance import extract_performance
        t4 = threading.Thread(target=extract_performance, args=(self.basic, self.print_text))
        t4.setDaemon(True)
        t4.start()

    def extract_data(self):
        from function.extract.data import extract_data
        t5 = threading.Thread(target=extract_data, args=(self.basic, self.print_text))
        t5.setDaemon(True)
        t5.start()

    def extract_profit(self):
        from function.extract.profit import extract_profit
        t6 = threading.Thread(target=extract_profit, args=(self.basic, self.print_text))
        t6.setDaemon(True)
        t6.start()

    def extract_brand(self):
        result = QInputDialog.getItem(self, '提示', '请选择类目：', self.basic.type)
        if result[1]:
            category = result[0]
            result = QInputDialog.getItem(self, '提示', '请选择店铺：', self.basic.store_all)
            if result[1]:
                store = result[0]
                from function.extract.brand_analytics import extract_brand
                t7 = threading.Thread(target=extract_brand, args=(self.basic, self.print_text, category, store))
                t7.setDaemon(True)
                t7.start()


if __name__ == '__main__':
    try:
        import sys
        app = QApplication(sys.argv)
        my_window = MyWindow()
        my_window.show()
        sys.exit(app.exec_())
    except Exception as expt:
        print(expt)

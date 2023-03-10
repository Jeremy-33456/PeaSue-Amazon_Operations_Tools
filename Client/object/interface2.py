# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface2.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Importer(object):
    def setupUi(self, Importer):
        Importer.setObjectName("Importer")
        Importer.resize(540, 720)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Importer.sizePolicy().hasHeightForWidth())
        Importer.setSizePolicy(sizePolicy)
        Importer.setMinimumSize(QtCore.QSize(540, 720))
        Importer.setMaximumSize(QtCore.QSize(540, 720))
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(10)
        Importer.setFont(font)
        self.centralwidget = QtWidgets.QWidget(Importer)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(0, 913, 1444, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.command1 = QtWidgets.QPushButton(self.centralwidget)
        self.command1.setGeometry(QtCore.QRect(130, 10, 81, 41))
        self.command1.setObjectName("command1")
        self.command3 = QtWidgets.QPushButton(self.centralwidget)
        self.command3.setGeometry(QtCore.QRect(335, 10, 81, 41))
        self.command3.setObjectName("command3")
        self.command4 = QtWidgets.QPushButton(self.centralwidget)
        self.command4.setGeometry(QtCore.QRect(430, 10, 81, 41))
        self.command4.setObjectName("command4")
        self.command5 = QtWidgets.QPushButton(self.centralwidget)
        self.command5.setGeometry(QtCore.QRect(10, 60, 71, 41))
        self.command5.setObjectName("command5")
        self.command6 = QtWidgets.QPushButton(self.centralwidget)
        self.command6.setGeometry(QtCore.QRect(100, 60, 101, 41))
        self.command6.setObjectName("command6")
        self.command7 = QtWidgets.QPushButton(self.centralwidget)
        self.command7.setGeometry(QtCore.QRect(220, 60, 101, 41))
        self.command7.setObjectName("command7")
        self.command8 = QtWidgets.QPushButton(self.centralwidget)
        self.command8.setGeometry(QtCore.QRect(340, 60, 71, 41))
        self.command8.setObjectName("command8")
        self.command9 = QtWidgets.QPushButton(self.centralwidget)
        self.command9.setGeometry(QtCore.QRect(430, 60, 101, 41))
        self.command9.setObjectName("command9")
        self.command2 = QtWidgets.QPushButton(self.centralwidget)
        self.command2.setGeometry(QtCore.QRect(230, 10, 81, 41))
        self.command2.setObjectName("command2")
        self.printer = QtWidgets.QTextBrowser(self.centralwidget)
        self.printer.setGeometry(QtCore.QRect(10, 110, 521, 601))
        self.printer.setObjectName("printer")
        self.command0 = QtWidgets.QPushButton(self.centralwidget)
        self.command0.setGeometry(QtCore.QRect(30, 10, 71, 41))
        self.command0.setObjectName("command0")
        Importer.setCentralWidget(self.centralwidget)
        self.action_add = QtWidgets.QAction(Importer)
        self.action_add.setObjectName("action_add")
        self.action_refresh = QtWidgets.QAction(Importer)
        self.action_refresh.setObjectName("action_refresh")
        self.action = QtWidgets.QAction(Importer)
        self.action.setObjectName("action")
        self.action_storage = QtWidgets.QAction(Importer)
        self.action_storage.setObjectName("action_storage")
        self.action_performance = QtWidgets.QAction(Importer)
        self.action_performance.setObjectName("action_performance")
        self.action_setting = QtWidgets.QAction(Importer)
        self.action_setting.setObjectName("action_setting")
        self.action_data = QtWidgets.QAction(Importer)
        self.action_data.setObjectName("action_data")
        self.action_profit = QtWidgets.QAction(Importer)
        self.action_profit.setObjectName("action_profit")
        self.action_exit = QtWidgets.QAction(Importer)
        self.action_exit.setObjectName("action_exit")
        self.action_switch = QtWidgets.QAction(Importer)
        self.action_switch.setObjectName("action_switch")
        self.action_import = QtWidgets.QAction(Importer)
        self.action_import.setObjectName("action_import")

        self.retranslateUi(Importer)
        QtCore.QMetaObject.connectSlotsByName(Importer)

    def retranslateUi(self, Importer):
        _translate = QtCore.QCoreApplication.translate
        Importer.setWindowTitle(_translate("Importer", "Importer"))
        self.command1.setText(_translate("Importer", "云端刷新"))
        self.command3.setText(_translate("Importer", "爬取坑位"))
        self.command4.setText(_translate("Importer", "爬取图片"))
        self.command5.setText(_translate("Importer", "导入库存"))
        self.command6.setText(_translate("Importer", "导入产品数据"))
        self.command7.setText(_translate("Importer", "导入广告数据"))
        self.command8.setText(_translate("Importer", "导入利润"))
        self.command9.setText(_translate("Importer", "导入品牌分析"))
        self.command2.setText(_translate("Importer", "本地刷新"))
        self.command0.setText(_translate("Importer", "结束会话"))
        self.action_add.setText(_translate("Importer", "添加产品"))
        self.action_refresh.setText(_translate("Importer", "刷新"))
        self.action.setText(_translate("Importer", "导入库存"))
        self.action_storage.setText(_translate("Importer", "库存数据"))
        self.action_performance.setText(_translate("Importer", "产品数据"))
        self.action_setting.setText(_translate("Importer", "广告设置"))
        self.action_data.setText(_translate("Importer", "广告数据"))
        self.action_profit.setText(_translate("Importer", "利润数据"))
        self.action_exit.setText(_translate("Importer", "退出"))
        self.action_switch.setText(_translate("Importer", "切换"))
        self.action_import.setText(_translate("Importer", "导入"))
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/11/17 0:33
# @Author  : Gahon
# @Email   : Gahon1995@gmail.com

import sys
from PyQt5.QtCore import QFileInfo, QTimer
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication
from UI.ui_trans import Ui_Trans
from src.translate import Trans


class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent=parent)
        self.ui = Ui_Trans()
        self.ui.setupUi(self)
        self.in_file_path = ""
        self.out_file_path = ""
        self.ui.input.hide()
        self.ui.output.hide()
        self.ui.bt_trans.setEnabled(False)
        self.ui.t_trans.setEnabled(False)
        # 连接槽函数选择输入文件按钮
        self.ui.bt_input.clicked.connect(self.c_input)
        # 连接槽函数选择输出文件按钮
        self.ui.bt_output.clicked.connect(self.c_output)
        # 绑定转换按钮
        self.ui.bt_trans.clicked.connect(self.trans)
        # 绑定转换按钮
        self.ui.t_trans.textChanged.connect(self.trans_f)
        self.tr = ""
        self.model = False

    def c_input(self):
        self.in_file_path, file_type = QFileDialog.getOpenFileName(self, "选取输入文件", ".", "Text Files (*.txt)")
        self.ui.input.show()
        self.ui.input.setText(self.in_file_path)

    def c_output(self):
        self.out_file_path, file_type = QFileDialog.getOpenFileName(self, "选取输出文件", ".", "Text Files (*.txt)")
        self.ui.output.show()
        self.ui.output.setText(self.out_file_path)

    def trans(self):
        self.ui.info.setText("正在转换中...")
        in_file = QFileInfo(self.in_file_path)
        out_file = QFileInfo(self.out_file_path)
        encode = self.ui.encode.text()
        if in_file.isFile() and out_file.isFile():
            if self.tr.read_from_file(self.in_file_path, self.out_file_path, encode=encode):
                self.ui.info.setText("转换完成")
        else:
            self.ui.info.setText("输入文件路径有误")
            self.ui.info

    def trans_f(self):
        self.ui.info.clear()
        text = self.ui.t_trans.toPlainText()
        result = self.tr.translate(text, 1)
        self.ui.info.setText("转换结果：" + result[0][1])

    def resizeEvent(self, a0: QResizeEvent):
        self.ui.info.setText("加载model中...")
        QTimer.singleShot(1000, self.load_data)

    def load_data(self):
        try:
            self.tr = Trans()
            self.model = True
        except FileNotFoundError:
            self.ui.info.setText("加载失败，请检查model文件路径是否正确")
        if self.model:
            self.ui.bt_trans.setEnabled(True)
            self.ui.t_trans.setEnabled(True)
            self.ui.info.setText("model加载完成")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())

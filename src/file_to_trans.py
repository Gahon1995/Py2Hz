#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:39
# @Author  : Gahon
# @Email   : Gahon1995@gmail.com

from src import translate
import os

"""
    使用测试集进行测试，输出正确率
    测试文件的格式为奇数行为拼音，偶数行为其对应的正确翻译
"""

PROJECT_PATH = os.path.abspath(os.path.dirname(os.getcwd()))
TEST_DATA_PATH = os.path.join(PROJECT_PATH, "train", "data", "pinyindata.txt")

tr = translate.Trans()

print("正在转换。。。。")

count = 0
right = 0
with open(TEST_DATA_PATH, 'r', encoding='utf-8') as fout:
    # yin = list(input("请输入拼音： ").split(" "))
    while fout:
        data = fout.readline().rstrip(" ").strip("\ufeff").strip("\n")
        # print(data)
        target = fout.readline().strip("\n")
        if data == "" or target == "":
            break

        t = tr.translate(data, 1)

        count += len(target)
        for i in range(0, len(t[0][1])):

            if t[0][1][i] == target[i]:
                right += 1
        # if t[0][1] != target:
        print(t[0][1], target)
    print(right/count)

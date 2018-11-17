#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:39
# @Author  : Gahon
# @Email   : Gahon1995@gmail.com

import json
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(os.getcwd()))


PROB_MODEL = os.path.join(PROJECT_PATH, "data", "model", "prob_model.json")


def read_json_file(path, encode="utf-8"):
    """
        读取JSON文件
    :param path: 文件路径
    :param encode: 编码方式，默认为utf-8
    :return:
    """
    with open(path, 'r', encoding=encode) as file:
        return json.load(file)


class Trans:
    pys = dict()
    model = dict()
    first = dict()
    obs = dict()

    # 加载数据
    def __init__(self):
        """
            从概率模型中加载数据，保存到全局变量中
        :return:
        """
        print("加载model...")
        data = read_json_file(PROB_MODEL)
        # 两个字之间的的概率  '你': {'cnt': 0.8, 'words': {'好': 0.7, '门': 0.5},,,}
        self.model = data["model"]
        # 每个汉字开头的概率 {"你": 0.3, "还"： 0.2,,,}
        self.first = data["words"]
        # 多音字选这个的概率 {'塞': {'sai': 0.8, 'se': 0.2},,}
        self.obs = data["hz2py"]

        self.pys = data["pinyin"]
        print("加载完成")

    def translate(self, words, path_deep=1):
        """
            转换函数，将一行拼音转换为一行文字
        :param words:   一行以空格隔开的拼音
        :param path_deep:   显示匹配结果的句子数量，默认只显示一个句子
        :return:
        """
        if len(words) == 0:
            return list([["", ""]])
        words = list(words.strip().split(" "))
        # min_pro = 1e-20
        pre_node = dict()
        if words[0] not in self.pys.keys():
            words[0] = words[0].replace("v", "u")
            if words[0] not in self.pys.keys():
                # print("输入的拼音没有对应的拼音: ", words[0], words)
                return [[" ", "拼音错误： " + words[0]]]

        for _w in self.pys[words[0]]:
            # _w : words[0] 这个拼音对应的每个字

            pro_word = self.obs[_w][words[0]]

            if _w not in self.first.keys() or _w not in self.model.keys():
                continue
            pre_node[_w] = dict()
            pre_node[_w]["score"] = self.first[_w] * pro_word
            pre_node[_w]["path"] = list(_w)

        for deep in range(1, len(words)):
            new_node = dict()
            _pinyin = words[deep]
            if _pinyin not in self.pys.keys():
                _pinyin = _pinyin.replace("v", "u")
                if _pinyin not in self.pys.keys():
                    # print("输入的拼音没有对应的拼音1: ", _pinyin)
                    return [["", "拼音错误：  " + _pinyin]]
            for _word in self.pys[_pinyin]:

                _pro_word = self.obs[_word][_pinyin]  # _pro_word:  当前这个字_word对应的拼音是_pinyin的概率，多音字处理

                if _word not in self.model.keys():
                    continue
                # 创建新节点，用于计算保存这一层的最大路径
                new_node.setdefault(_word, dict())
                new_node[_word]["score"] = -1
                new_node[_word]["path"] = list()

                # 计算前边节点的所有字到当前字的距离
                for pre_word in pre_node:  # pre_word: 上一个节点的某一个字

                    if _word not in self.model[pre_word]["words"].keys():
                        # 如果两个字没有联系，默认最小值
                        this_pro = 1e-20
                    else:
                        _cnt = self.model[pre_word]["words"][_word] / self.model[pre_word]["cnt"]
                        this_pro = _pro_word * self.model[pre_word]["words"][_word]
                    _score = pre_node[pre_word]["score"] * this_pro

                    if _score > new_node[_word]["score"]:
                        new_node[_word]["score"] = _score
                        new_node[_word]["path"] = list(pre_node[pre_word]["path"])
                        new_node[_word]["path"].append(_word)

            pre_node = new_node

        path = sorted(pre_node.items(), key=lambda x: x[1]["score"], reverse=True)

        if len(path) == 0:
            return [["", "没有找到匹配的翻译"]]
        result = list()
        for i in range(0, min(path_deep, len(path))):
            result.append([path[i][1]["score"], "".join(path[i][1]["path"])])
        return result

    def get_input(self):
        """
            从命令行输入拼音进行转换
        :return:
        """
        deep = 1
        while True:
            inp = input("\n请输入要转换的拼音： ").strip()
            if len(inp) == 0:
                print("无输入，退出中")
                break
            result = self.translate(inp, deep)
            for path in result:
                print(path[1])

    def read_from_file(self, in_path, out_path, encode="utf-8"):
        """
            从文件中读取文件进行转换，并将转换结果保存到文件中
        :param in_path:     拼音文件路径，要求里边只有拼音，并且每行的各个拼音用空格隔开
        :param out_path:    输出结果文件路径
        :param encode:      输入文件的编码方式设置，输出文件编码默认为gbk
        :return:
        """
        print("输入文件路径：", in_path)
        print("输出文件路径：", out_path)
        print("encode: ", encode)
        print("正在转换....")
        with open(in_path, "r", encoding=encode) as fin, open(out_path, "w", encoding="gbk") as fout:
            while fout:
                data = fin.readline()
                if data == "":
                    break
                result = self.translate(data)
                fout.write(result[0][1])
                fout.write("\n")

        print("转换完成。")
        return True


if __name__ == "__main__":
    num = len(sys.argv)
    tr = Trans()
    if num == 1:
        print("输入格式为: translate.exe \"pinyin\"")
        print("      or: translate.exe input_path output_path")
        print("      or: python3 translate.py \"pinyin\"")
        print("      or: python3 translate.exe input_path output_path")
        tr.get_input()
    elif num == 2:
        print(tr.translate(sys.argv[1], 3)[0][1])
    elif num == 3:
        tr.read_from_file(sys.argv[1], sys.argv[2])
    else:
        print("输入有误")
        print("输入格式为: chengxu \"pinyin\"")
        print("      or: chengxu input_path output_path")
        print("      or: python3 translate.py \"pinyin\"")
        print("      or: python3 translate.exe input_path output_path")





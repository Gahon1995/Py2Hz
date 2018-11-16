#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/11/16 17:39
# @Author  : Gahon
# @Email   : Gahon1995@gmail.com

import json
import os
from src import utils
import time
import multiprocessing
import copy

PROJECT_PATH = utils.PROJECT_PATH

# 文件路径定义
NEWS_PATH = utils.NEWS_PATH
ARTICLE_PATH = utils.ARTICLE_PATH
BASE_MODEL = utils.BASE_MODEL

# 所有汉字列表  {"你"：cnt,,,}
cnt_words = utils.get_chinese()
# 所有的汉字对应的拼音列表 {"和": {"he": cnt, "huo": cnt}}
cnt_hz2py = utils.get_hz2py()
# 词组关系 {"你": {"cnt": cnt, "words": {"好":cnt, "们": cnt } } }
cnt_model = dict()

base_words, base_hz2py, base_model = dict(), dict(), dict()


def get_cnt():
    """
        返回各个词频数据，供外部调用
    """
    return base_words, base_hz2py, base_model


def train_from_sentences(content: str, train_words, train_hz2py, train_model):
    """
        使用一行文本中进行训练
    :param content: 待训练的文本
    :param train_words: 保存字频
    :param train_hz2py: 保存每个字对应其中一个拼音的次数
    :param train_model: 保存两个字同时出现的频率
    :return:    训练出来的字频数据（上边三个）
    """
    _sentences = utils.cut_article(content)
    for _sentence in _sentences:
        # 前一个字
        _pre = ""
        for pos in range(0, len(_sentence)):
            _word = _sentence[pos]
            if _word not in train_words.keys():
                # _pre = ""
                continue
            train_words[_word] += 1
            # 判断是否为多音字
            if utils.is_multi(_word):
                # pass
                # # 多音字，通过pypinyin包得到正确发音，然后对应拼音+1
                start = max(0, pos - 2)
                end = min(pos + 2, len(_sentence))
                pinyin = utils.multi2py(_sentence[start:end], _word)
                if pinyin == "":
                        continue
                train_hz2py[_word][pinyin] += 1
            else:
                # 对应拼音 + 1
                (key, value), = train_hz2py[_word].items()
                train_hz2py[_word][key] = value + 1

            # 判断上一个字是否已经在第一个字的列表中
            if _pre == "":
                _pre = _word
                continue
            if _pre not in train_model.keys():
                # 不在第一个字列表中，则加入
                train_model.setdefault(_pre, dict())
                train_model[_pre].setdefault("cnt", 0)
                train_model[_pre].setdefault("words", dict())
            # 判断当前字是否在 model[_pre].keys() 中
            if _word not in train_model[_pre]["words"].keys():
                # 不在，则将其加入
                train_model[_pre]["words"].setdefault(_word, 0)
            train_model[_pre]["cnt"] += 1
            train_model[_pre]["words"][_word] += 1
            _pre = _word
    return train_words, train_hz2py, train_model


def merge_data(train_words, train_hz2py, train_model):
    """
        将单个文本训练出来的字频数据合并到全局字频数据中
    :param train_words: 单个字出现的字频
    :param train_hz2py: 每个字对应其中一个拼音的次数
    :param train_model: 两个字同时出现的频率
    :return:
    """
    for _word in train_words:
        if _word not in base_words.keys():
            base_words[_word] = train_words[_word]
        else:
            base_words[_word] += train_words[_word]

    for _hz2py in train_hz2py:
        if _hz2py not in base_hz2py.keys():
            base_hz2py[_hz2py] = train_hz2py[_hz2py]
        else:
            for pin in base_hz2py[_hz2py]:
                base_hz2py[_hz2py][pin] += base_hz2py[_hz2py][pin]

    for _model in train_model:
        if _model not in base_model.keys():
            base_model[_model] = train_model[_model]
        else:
            base_model[_model]["cnt"] += train_model[_model]["cnt"]
            for _mo in train_model[_model]["words"].keys():
                if _mo not in base_model[_model]["words"].keys():
                    base_model[_model]["words"][_mo] = train_model[_model]["words"][_mo]
                else:
                    base_model[_model]["words"][_mo] += train_model[_model]["words"][_mo]


def multi_read_news(encode="gbk"):
    """
        使用多线程的方式去对每个文件进行分析
    :param encode:
    :return:
    """
    results = []
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    files = os.listdir(NEWS_PATH)
    for file in files:
        if not os.path.isdir(file):
            result = pool.apply_async(open_news, args=(os.path.join(NEWS_PATH, file), encode))
            results.append(result)
    pool.close()
    pool.join()
    print("\nfinish")
    for result in results:
        (tmp_words, tmp_hz2py, tmp_model) = result.get()
        merge_data(tmp_words, tmp_hz2py, tmp_model)


def multi_read_article(encode="utf-8"):
    results = []
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    files = os.listdir(ARTICLE_PATH)
    for file in files:
        if not os.path.isdir(file):
            result = pool.apply_async(open_article, args=(os.path.join(ARTICLE_PATH, file), encode))

            results.append(result)
    pool.close()
    pool.join()
    print("\nfinish")
    for result in results:
        (tmp_words, tmp_hz2py, tmp_model) = result.get()
        merge_data(tmp_words, tmp_hz2py, tmp_model)


def open_news(path, encode):
    print("loading file \"", path, "\"")
    tmp_words = copy.deepcopy(cnt_words)
    tmp_hz2py = copy.deepcopy(cnt_hz2py)
    tmp_model = copy.deepcopy(cnt_model)
    with open(path, 'r', encoding=encode) as f:
        count = 0
        for line in f:
            if count == 1000:
                print(".", end="")
                count = 0
            count += 1

            if line.strip() == "":
                continue
            message = json.loads(line)
            train_from_sentences(message["title"], tmp_words, tmp_hz2py, tmp_model)
            train_from_sentences(message["html"], tmp_words, tmp_hz2py, tmp_model)
    return tmp_words, tmp_hz2py, tmp_model


def open_article(path, encode):
    print("loading file \"", path, "\"")
    tmp_words = copy.deepcopy(cnt_words)
    tmp_hz2py = copy.deepcopy(cnt_hz2py)
    tmp_model = copy.deepcopy(cnt_model)
    with open(path, 'r', encoding=encode) as f:
        count = 0
        for line in f:
            # print(count)
            if count == 1000:
                print(".", end="")
                count = 0
            count += 1

            if line.strip() == "":
                continue
            train_from_sentences(line, tmp_words, tmp_hz2py, tmp_model)
    return tmp_words, tmp_hz2py, tmp_model


# 统一文件读取，方便增加训练材料
def read():
    multi_read_article()
    multi_read_news()


def save():
    print("保存数据...")
    model = dict()
    model["words"] = base_words
    model["hz2py"] = base_hz2py
    model["model"] = base_model
    utils.save_json_file(BASE_MODEL, model)
    print("保存完成...")


def train():
    read()
    save()


if __name__ == "__main__":
    _start = time.time()

    train()

    _end = time.time()

    print("\n总共耗时： ", (_end - _start)/60, "分钟")


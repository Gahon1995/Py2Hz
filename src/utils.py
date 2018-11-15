import json
import re
import os
import pypinyin
from src import load_pinyin
import pickle

PROJECT_PATH = os.path.abspath(os.path.dirname(os.getcwd()))

PINYIN_PATH = os.path.join(PROJECT_PATH, "data", "pinyin", "拼音汉字表.txt")
WORDS_PATH = os.path.join(PROJECT_PATH, "data", "pinyin", "一二级汉字表.txt")
NEWS_PATH = os.path.join(PROJECT_PATH, "train", "sina_news_gbk")
ARTICLE_PATH = os.path.join(PROJECT_PATH, "train", "article")

PRO_DATA_WORDS = os.path.join(PROJECT_PATH, "data", "words.txt")

BASE_MODEL = os.path.join(PROJECT_PATH, "data", "model", "base_model.json")
PROB_MODEL = os.path.join(PROJECT_PATH, "data", "model", "prob_model.json")
PICKLE_MODEL = os.path.join(PROJECT_PATH, "data", "model", "pickle_model.data")


load_pinyin._init(PINYIN_PATH)

hz2py = load_pinyin.get_hz2py()
multi = load_pinyin.get_multi()
pys = load_pinyin.get_pys()



sp = re.compile(r"\s|[0-9a-zA-Z]|\.|\(|\)|" + "|".join(["，", "。", "、", "：", "；", "？", "！", "（", "）", "《", "》",
                                                      "-", "——", "·", "……", "‘", "’", "“", "”", "/", r"\\", "\\[", "\\]",
                                                     " 【", "】", "\\|", "℃", ">>", "<<"]))

words = dict()


# 句子分割
def cut_article(para):

    return list(sp.split(para))


# 多音字转换为拼音，传入多音字所在句子和这个汉字
def multi2py(sentence: str, word):
    pinyin = pypinyin.lazy_pinyin(sentence)

    for py in pinyin:
        # 特殊修正
        if py == "nei" and word == "哪":
            py = "na"
        elif py == "ji" and word == "家":
            py = "jia"
        elif py == "nve" and word == "疟":
            py = "nue"
        elif py == "hua" and word == "还":
            py = "huan"
        if py in hz2py[word].keys():
            return py
    # print(sentence, word)
    # print(pinyin)
    return ""


def is_multi(word):
    if word in multi:
        return True
    return False


def print_json(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def get_chinese():
    with open(WORDS_PATH, "r", encoding="gbk") as fin:
        count = 0
        charList = list(fin.readline().strip())
        for c in charList:
            words[c] = count
    return words


def get_hz2py():
    return hz2py


def save_json_file(path, data):
    with open(path, 'w', encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False)


def save_pickle_file(path,data):
    print("保存model到文件中")
    with open(path, "wb") as out:
        pickle.dump(data, out)


def read_json_file(path):
    with open(path, 'r') as file:
        return json.load(file)


if __name__ == "__main__":
    # print(is_multi("和"))
    # print_json(hz2py)
    # print(len(hz2py))

    # print(get_chinese())

    print(hz2py["疟"])

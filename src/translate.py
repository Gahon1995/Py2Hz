import json
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.dirname(os.getcwd()))

# TODO - 将路径转换为多平台通用的格式
PINYIN_PATH = os.path.join(PROJECT_PATH, "data", "pinyin", "拼音汉字表.txt")

PROB_MODEL = os.path.join(PROJECT_PATH, "data", "model", "prob_model.json")
PICKLE_MODEL = os.path.join(PROJECT_PATH, "data", "model", "pickle_model.data")

pys = dict()
model = dict()
first = dict()
obs = dict()


def read_json_file(path):
    with open(path, 'r') as file:
        return json.load(file)


# 加载数据
def _init():
    global obs, model, first, pys
    print("加载model...")
    data = read_json_file(PROB_MODEL)
    # 两个字之间的的概率  '你': {'cnt': 0.8, 'words': {'好': 0.7, '门': 0.5},,,}
    model = data["model"]
    # 每个汉字开头的概率 {"你": 0.3, "还"： 0.2,,,}
    first = data["words"]
    # 多音字选这个的概率 {'塞': {'sai': 0.8, 'se': 0.2},,}
    obs = data["hz2py"]

    pys = read_from_pinyin_file()
    print("加载完成")


def read_from_pinyin_file():
    all_py = dict()
    with open(PINYIN_PATH, 'r', encoding='gbk') as fout:

        for pinyin in fout:
            pinyin = pinyin.strip("\n").split(" ")
            key = pinyin[0]
            pinyin.remove(pinyin[0])
            all_py[key] = pinyin
    return all_py


def translate(words: str, path_deep=1):
    if len(words) == 0:
        return list(["", ""])
    words = list(words.strip().split(" "))
    # min_pro = 1e-20
    pre_node = dict()
    if words[0] not in pys.keys():
        words[0] = words[0].replace("v", "u")
        if words[0] not in pys.keys():
            # print("输入的拼音没有对应的拼音: ", words[0], words)
            return [[" ", "拼音错误： " + words[0]]]

    for _w in pys[words[0]]:
        # _w : words[0] 这个拼音对应的每个字

        pro_word = obs[_w][words[0]]

        if _w not in first.keys() or _w not in model.keys():
            continue
        pre_node[_w] = dict()
        pre_node[_w]["score"] = first[_w] * pro_word
        pre_node[_w]["path"] = list(_w)

    for deep in range(1, len(words)):
        new_node = dict()
        _pinyin = words[deep]
        if _pinyin not in pys.keys():
            _pinyin = _pinyin.replace("v", "u")
            if _pinyin not in pys.keys():
                # print("输入的拼音没有对应的拼音1: ", _pinyin)
                return [["", "拼音错误：  " + _pinyin]]
        for _word in pys[_pinyin]:

            _pro_word = obs[_word][_pinyin]     # _pro_word:  当前这个字_word对应的拼音是_pinyin的概率，多音字处理

            if _word not in model.keys():
                continue
            # 创建新节点，用于计算保存这一层的最大路径
            new_node.setdefault(_word, dict())
            new_node[_word]["score"] = -1
            new_node[_word]["path"] = list()

            # 计算前边节点的所有字到当前字的距离
            for pre_word in pre_node:   # pre_word: 上一个节点的某一个字

                if _word not in model[pre_word]["words"].keys():
                    # 如果两个字没有联系，默认最小值
                    this_pro = first[_word] * 0.11
                else:
                    _cnt = model[pre_word]["words"][_word] / model[pre_word]["cnt"]
                    this_pro = _pro_word * model[pre_word]["words"][_word]
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


def get_input():
    deep = 3
    while True:
        inp = input("请输入要转换的拼音： ").strip()
        if len(inp) == 0:
            print("无输入，退出中")
            break
        result = translate(inp, deep)
        for path in result:
            print(path[0], path[1])


def read_from_file(in_path, out_path, encode="utf-8"):
    print("输入文件路径：", in_path)
    print("输出文件路径：", out_path)
    with open(in_path, "r", encoding=encode) as fin, open(out_path, "w", encoding=encode) as fout:
        while fout:
            data = fin.readline()
            # print(data)
            if data == "":
                break
            result = translate(data)
            fout.write(result[0][1])
            fout.write("\n")

    print("转换完成。")


if __name__ == "__main__":

    num = len(sys.argv)
    _init()
    if num == 1:
        print("输入格式为: chengxu \"pinyin\"")
        print("      or: chengxu input_path output_path")
        get_input()
    elif num == 2:
        print(translate(sys.argv[1], 3)[0][1])
    elif num == 3:
        read_from_file(sys.argv[1], sys.argv[2])
    else:
        print("输入有误")
        print("输入格式为: chengxu \"pinyin\"")
        print("      or: chengxu input_path output_path")





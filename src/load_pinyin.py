import json

# 拼音 -> 汉字
pys = dict()
# 汉字：{拼音's}
hz2py = dict()
# 多音字
multi = list()


def read_from_pinyin_file(path):
    with open(path, 'r', encoding='gbk') as fout:

        for pinyin in fout:
            pinyin = pinyin.strip("\n").split(" ")
            key = pinyin[0]
            pinyin.remove(pinyin[0])
            pys[key] = pinyin


# 获取当前字对应的拼音列表
def _init(path):
    read_from_pinyin_file(path)
    for _py in pys:
        for _word in pys[_py]:
            if _word not in hz2py.keys():
                hz2py.setdefault(_word, dict())
                hz2py[_word][_py] = 1
            else:
                if _word not in multi:
                    multi.append(_word)
                hz2py[_word][_py] = 1


def get_hz2py():
    return hz2py


def get_multi():
    # print("get multi")
    return multi


def is_multi(word):
    if word in multi:
        return True
    return False


if __name__ == "__main__":
    # _init(os.path.join(os.path.abspath(os.path.dirname(os.getcwd())), "data", "pinyin", "拼音汉字表.txt"))
    print(json.dumps(hz2py, ensure_ascii=False, indent=4))
    # print(multi)
    print(is_multi("么"))

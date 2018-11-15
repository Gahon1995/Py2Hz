import time
from src import utils
from src import multi_base_train

PROJECT_PATH = utils.PROJECT_PATH

BASE_MODEL = utils.BASE_MODEL
PROB_MODEL = utils.PROB_MODEL

cnt_words = dict()
cnt_hz2py = dict()
cnt_model = dict()


def _init():
    global cnt_words, cnt_hz2py, cnt_model
    data = utils.read_json_file(BASE_MODEL)
    # 所有汉字列表  {"你"：cnt,,,}
    cnt_words = data["words"]
    # 所有的汉字对应的拼音列表 {"和": {"he": cnt, "huo": cnt}}
    cnt_hz2py = data["hz2py"]
    # 词组关系 {"你": {"cnt": cnt, "words": {"好":cnt, "们": cnt } } }
    cnt_model = data["model"]


def _init_all():
    global cnt_words, cnt_hz2py, cnt_model
    # 所有汉字列表  {"你"：cnt,,,}
    # 所有的汉字对应的拼音列表 {"和": {"he": cnt, "huo": cnt}}
    # 词组关系 {"你": {"cnt": cnt, "words": {"好":cnt, "们": cnt } } }

    cnt_words, cnt_hz2py, cnt_model = multi_base_train.get_cnt()


# 使用词库计算每个字的频率
def gen_words():
    global cnt_words

    count = 0
    kind = 0
    # 无优化
    for word in cnt_words:
        kind += 1
        count += cnt_words[word]

    for word in cnt_words:
        cnt_words[word] = (cnt_words[word] + 1)/(count + kind)
    # 平滑处理那些没有出现过的值
    cnt_words["default"] = 1.0 / (count + kind)

    # 尝试优化


def gen_hz2py():
    global cnt_hz2py

    for _word in cnt_hz2py:
        _count = 0
        for py in cnt_hz2py[_word]:
            _count += cnt_hz2py[_word][py]

        for py in cnt_hz2py[_word]:
            cnt_hz2py[_word][py] = cnt_hz2py[_word][py] / _count


def gen_model():
    global cnt_model

    _base = 1
    _base_count = 2

    for _pre in cnt_model:
        for _back in cnt_model[_pre]["words"]:
            _word_cnt = max(cnt_model[_pre]["words"][_back] / _base, _base_count)
            _pro = round((_word_cnt + 1) / (cnt_model[_pre]["cnt"] / _base), 8)
            cnt_model[_pre]["words"][_back] = max(_pro, 1e-9)
        # cnt_model[_pre]["default"] = 1.0 / (cnt_model[_pre]["cnt"] / _base)


def _save_json():
    print("保存数据...")
    model = dict()
    model["words"] = cnt_words
    model["hz2py"] = cnt_hz2py
    model["model"] = cnt_model
    model["pinyin"] = utils.pys
    utils.save_json_file(PROB_MODEL, model)

    print("保存完成...")


# 直接从原始语料开始训练
def start_train_all():
    print("开始训练数据....")
    multi_base_train.train()
    print("开始转换数据")
    _init_all()
    gen_hz2py()
    gen_model()
    gen_words()

    print("转换完成")
    # 保存最终模型
    _save_json()


# 从中间计数的文件中读取文件进行训练
def start_train_alone():
    print("开始训练数据....")
    print("开始转换数据")
    _init()
    gen_hz2py()
    gen_model()
    gen_words()

    print("转换完成")
    _save_json()


if __name__ == "__main__":
    _start = time.time()

    # start_train_all()   # 从语料库开始训练
    start_train_alone()     # 从二次数据中读取后开始训练

    _end = time.time()

    print("总共耗时： ", round((_end - _start)/60, 2), "分钟")




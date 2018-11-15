from src import translate
import os

PROJECT_PATH = os.path.abspath(os.path.dirname(os.getcwd()))

# print(PROJECT_PATH)

# TODO - 将路径转换为多平台通用的格式

# DATA_PATH = PROJECT_PATH + "/data/pinyindata.txt"
TEST_DATA_PATH = os.path.join(PROJECT_PATH, "data", "pinyindata.txt")

translate._init()

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

        t = translate.translate(data, 1)

        count += len(target)
        for i in range(0, len(t[0][1])):

            if t[0][1][i] == target[i]:
                right += 1
        # if t[0][1] != target:
        print(t[0][1], target)
    print(right/count)

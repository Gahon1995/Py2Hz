# 文件说明

## 1、 目录结构
    |   README.md
    |—— bin: 可执行文件路径
    |       translate.exe
    |
    |—— data:
    |       input.txt       -> 输入文件 (gbk编码）
    |       output.txt      -> 结果输出文件 (gbk编码）
    |       prob_model.json -> 模型数据
    |
    |—— report:
    |           report.pdf
    |
    |—— src:
    |       utils.py                ->  工具类，用于模型生成判断
    |       multi_base_train.py     ->  多线程字频统计
    |       gen_model.py            ->  频率模型生成函数
    |       translate.py            ->  拼音转汉字主函数
    |       file_to_trans.py        ->  测试文件，得出正确率
    |
    |—— train:
    |       article:      部分训练语料
    |            |——   sina_news_gbk   -> 新浪新闻材料，JSON格式(内容太大，没上传)
    |            |——   others          -> 其他文本材料
    |       data:         训练所用到的一些数据
    |
    |—— UI：         使用PyQt5制作的一个简单界面
    |       main.py     ->  主界面
    |       ui_trans.py ->  使用PyUIC通过ui文件生成
    |       ui_trans.ui ->  使用QtDesigner设计的布局文件
    |
## 2、 使用说明
### 1. 训练
1. 从头开始

将 `gen_model.py` 中的 "start_train_all()" 取消注释，然后运行。
使用该方法将会去读取train/article里边的内容进行训练
结果会生成基于频数的模型和基于概率的模型。

2. 从基于词频的模型修改开始

将 `gen_model.py` 中的 "start_train_alone()" 取消注释，然后运行。
使用该方法将会读取`train/data/base_model.json`文件进行处理
会读取之前生成的基于词频的模型文件，然后进行处理得到基于概率的模型

### 2. 拼音转汉字
一共有三种使用方式

1、 封装软件使用

使用方式为  `translate.exe "待转换的拼音"` 或者 `translate.exe input_path output_path`或 `translate.exe input_path output_path encode`的方式来进行转换

2、 运行`translate.py`文件来使用

使用方式为 `pyhon3 translate.py "待转换的拼音` 或者 `pyhon3 translate.py input_path output_path`或者`pyhon3 translate.py input_path output_path encode`

3、 运行UI文件下的`main.py`文件将会显示 一个UI界面，方便操作（前提得先安装好QT相关库)

## 3. 注意事项
1. input_file 的编码默认为gbk,如果打开失败，请尝试在路径后边增加encode方式。
2. output_file 的编码方式同时也保存为gbk

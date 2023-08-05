#!/usr/bin/python3

"""
@author: 张伟
@time: 2018/3/7 9:28
"""
import os
import re


class Mate(object):
    data = list()
    text = str()
    date_rg = r'(\d{4}年\d{1,2}月\d{1,2}日)|(\d{4}\S\d{1,2}\S\d{1,2})|[a-zA-Z]*'

    def __init__(self, list_file=None):
        """
        初始化
        :param list_file 分词字典,可以是链表也可以是文件地址
        """
        self.p = os.path.sep
        if type(list_file) is list:
            self.load_list(list_file)
        elif type(list_file) is str:
            self.load_file(list_file)

    def load_list(self, ls):
        """
        加载链表字典，注意如果链表中包含换行符，自动清除。
        :param ls: 链表，一维链表[key,key,.....]
        :return: None
        """
        if '\n' in ls[0]:
            self.data = [f[:-1] for f in ls]
        else:
            self.data = ls

    def load_file(self, file):
        """
        加载文件字典
        :param file: 词库文件地址
        :return: None
        """
        with open(file=file, encoding='utf-8-sig') as f:
            self.load_list(f.readlines())
            f.close()

    def __mate_num(self, obj):
        r = re.match(self.date_rg, obj, re.M | re.I)
        if r:
            start, end = r.span()
            w = obj[start:end]
            return w
        return ''

    def mate(self, input_string):
        """
        分词文本
        :param input_string:  输入文本字符串
        :return: 分割好的字符串
        """
        self.text = input_string + " "  # 最后加一个空格是保证能匹配到最后一个字
        out_string = str()
        lens = len(self.text) + 1
        j = 0  # 第几个字
        flag = 0  # 标识截断词的位置
        while j < lens:
            for k in range(j + 2, lens):
                word = self.text[j:k]  # 起始匹配值
                deviation = 0  # 匹配偏移量
                if 47 < ord(self.text[j]) < 58 or 89 < ord(self.text[j]) < 123:
                    word = self.__mate_num(self.text[j:j + 11])
                    if not len(word):
                        break
                    out_string += self.text[flag:j] + self.p  # 没有匹配到的词
                    out_string += word + self.p  # 匹配到的词
                    j = j + len(word)
                    flag = j
                    break
                else:
                    while word in self.data:
                        """核心算法"""
                        deviation += 1
                        word = self.text[j:k + deviation]
                    if deviation != 0:
                        if len(self.text[flag:j]):
                            out_string += self.text[flag:j] + self.p  # 没有匹配到的词
                        out_string += word[:-1] + self.p  # 匹配到的词
                        j = k + deviation - 1
                        flag = j
                        j -= 1
                        break
            j += 1
        out_string += self.text[flag:]  # 加入最后的词
        return out_string

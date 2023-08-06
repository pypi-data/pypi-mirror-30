#!/usr/bin/python3

"""
@author: 张伟
@time: 2018/3/7 9:28
"""
import os
import re


class Mate(object):
    data = set()
    text = str()
    stop = set()
    date_rg = r'(\d{4}年\d{1,2}月\d{1,2}日)|(\d{4}\S\d{1,2}\S\d{1,2})|([A-Za-z0-9]*)'

    def __init__(self, list_file_extend=None, list_file_stop=None):
        """
        初始化
        :param list_file_extend 扩展字典,可以是链表也可以是文件地址
        :param list_file_stop 停用字典。可以是链表也可以是文件地址
        """
        self.p = os.path.sep
        if type(list_file_extend) is list:
            self.load_list(list_file_extend)
        elif type(list_file_extend) is str:
            self.load_file(list_file_extend)

        if type(list_file_stop) is list:
            self.stop.update(list_file_stop)
        elif type(list_file_stop) is str:
            with open(file=list_file_stop, encoding='utf-8-sig') as f:
                self.stop.update([fs[:-1] for fs in f.readlines()])
                f.close()
        flags = list(range(47, 56)) + list(range(64, 90)) + list(range(96, 123))  # 初始化数字和字母的Unicode值
        self.d = dict(map(lambda x: (x, True), flags))
        path = os.path.dirname(os.path.realpath(__file__))
        self.load_file(path + self.p + 'dict')

    def load_list(self, ls):
        """
        加载链表字典，注意如果链表中包含换行符，自动清除。
        :param ls: 链表，一维链表[key,key,.....]
        :return: None
        """
        if '\n' in ls[0]:
            self.data.update([f[:-1] for f in ls])
        else:
            self.data.update(ls)

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
                if self.d.get(ord(self.text[j])):
                    word = self.__mate_num(self.text[j:j + 10])
                    if not len(word):
                        break
                    if self.text[flag:j] not in self.stop:
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
                            if self.text[flag:j] not in self.stop:
                                out_string += self.text[flag:j] + self.p  # 没有匹配到的词
                        out_string += word[:-1] + self.p  # 匹配到的词
                        j = k + deviation - 1
                        flag = j
                        j -= 1
                        break
            j += 1
        if self.text[flag:-1] not in self.stop:
            out_string += self.text[flag:-1]  # 加入最后的词
        return out_string

    def to_list(self, split_words):
        return split_words.split(self.p)[:-1]

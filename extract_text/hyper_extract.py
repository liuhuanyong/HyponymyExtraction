#!/usr/bin/env python3
# coding: utf-8
# File: extract.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-9

import re
import pymongo
import jieba.posseg as pseg
import os

class HyponomyExtraction:
    def __init__(self):
        self.conn = pymongo.MongoClient()

    '''对正文进行规范化处理，去除空白符'''
    def remove_noisy(self, content):
        return content.replace('\xa0','').replace('\u3000', '').replace(' ', '。').replace('（','').replace('）','')

    '''进行分句处理'''
    def spilt_sent(self, content):
        content = self.remove_noisy(content)
        punc = "！？｡。，：；､？?！!。；;：:\n\r,—"
        return [i for i in re.split(r'[%s]'%punc, content) if i]

    '''通过分词，看看是否符合情况'''
    def pos_filter(self, s):
        if not s:
            return []
        wds = [w.word for w in pseg.cut(s)]
        pos = [w.flag for w in pseg.cut(s) if w.flag[0]]

        if len(''.join(wds))<2:
            return []
        if 'n' not in pos:
            return []
        return ''.join(wds)

    '''通过分词，看看是否符合情况'''
    def pos_extract(self, s):
        if not s:
            return []
        # wds = [w.word+'_'+w.flag for w in pseg.cut(s) if w.flag[0] in ['n','v','a']]
        # wds = [w.word for w in pseg.cut(s) if w.flag[0] in ['n','v','a']]
        wds = [w.word for w in pseg.cut(s) if w.flag[0] not in ['d','m','q','p','u','r','w','x','i'] and len(w.word) > 1]
        pos = [w.flag for w in pseg.cut(s) if w.flag[0] not in ['d','m','q','p','u','r','w','x','i'] and len(w.word) > 1]
        if len(wds)>3 or 'n' not in pos:
            return []
        return ''.join(wds)

    '''A是一种Ｂ'''
    def ruler1(self, string):
        data = []
        pattern = re.compile(r'(.*)是一(种|个|类)(.*)')
        res = pattern.findall(string)
        if res:
            sub = self.pos_filter(res[0][0])
            big = self.pos_filter(res[0][2])
            if sub and big:
                data.append([sub, big])
        return data

    '''A是B的一种'''
    def ruler2(self, string):
        data = []
        pattern = re.compile(r'(.*)是(.*)的一(种|个|类)')
        res = pattern.findall(string)
        if res:
            sub = self.pos_filter(res[0][0])
            big = self.pos_filter(res[0][1])
            if sub and big:
                data.append([sub, big])
        return data

    '''抽取主函数'''
    def extract_main(self, sent):
        data = []
        res1 = self.ruler1(sent)
        res2 = self.ruler2(sent)
        data += res1
        data += res2
        return data

    '''插数据库'''
    def process_mongo(self):
        count = 0
        for item in self.conn['novel']['data'].find():
            count += 1
            content = item['content']
            sents = self.spilt_sent(content)
            for sent in sents:
                data = self.extract_main(sent)
                if data:
                    info = {}
                    info['sent'] = sent
                    info['data'] = data
                    print(count, sent, data)
                    self.conn['novel']['candi'].insert(info)

    '''对候选句子进行处理'''
    def process_candis(self):
        f = open('hyper_rels.txt', 'w+')
        count = 0
        e_dict = {}
        for item in self.conn['novel']['candi'].find():
            count += 1
            print(count)
            data = item['data']
            for i in data:
                big = i[1]
                sub = i[0]
                big = self.pos_extract(big)
                sub = self.pos_extract(sub)
                pair = '-->'.join([sub, big])
                if pair not in e_dict:
                    e_dict[pair] = 1
                else:
                    e_dict[pair] += 1
        for item in sorted(e_dict.items(), key=lambda asd:asd[1], reverse=True):
            f.write(item[0] + ' ' + str(item[1])+'\n')
        f.close()

    '''对候选句子进行处理'''
    def process_candis2(self):
        f = open('hyper_rels2.txt', 'w+')
        count = 0
        e_dict = {}
        for item in self.conn['novel']['candi'].find():
            count += 1
            print(count)
            data = item['data']
            for i in data:
                big = i[1]
                sub = i[0]
                big = self.pos_extract(big)
                sub = self.pos_extract(sub)
                if big and sub:
                    pair = '-->'.join([sub, big])
                    print(pair)

                if pair not in e_dict:
                    e_dict[pair] = 1
                else:
                    e_dict[pair] += 1
        for item in sorted(e_dict.items(), key=lambda asd:asd[1], reverse=True):
            f.write(item[0] + ' ' + str(item[1])+'\n')
        f.close()


    '''对抽取处理的关系进行图谱展示'''

content = '''油加醋，或者去涂脂抹粉“打造”它。历史是不需要加工的。无形的音乐是一种灵魂，而肺癌是癌症的一种'''
handler = HyponomyExtraction()
handler.process_candis2()

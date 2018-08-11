#!/usr/bin/env python3
# coding: utf-8
# File: kb_search.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-11
import os
class SemanticBaike:
    def __init__(self):
        cur = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        concept_file = os.path.join(cur, 'baike_concept.txt')
        self.tmp_file = os.path.join(cur, 'word_concept.txt')
        self.concept_dict = self.collect_baikeconcept(concept_file)

    '''加载百科上下位概念'''
    def collect_baikeconcept(self, concept_file):
        concept_dict = {}
        for line in open(concept_file):
            line = line.strip().split('->')
            if not line:
                continue
            instance = line[0]
            category = line[1]
            if instance not in concept_dict:
                concept_dict[instance] = [category]
            else:
                concept_dict[instance].append(category)
        return concept_dict

    '''基于百科上下位词典进行遍历查询'''
    def walk_concept_chain(self, word):
        chains = []
        hyper_words = self.concept_dict.get(word, '')
        print(hyper_words)
        if not hyper_words:
            return

        for hyper in hyper_words:
            print(word, hyper)
            hyper_words = self.concept_dict.get(hyper, '')
            for hyper_ in hyper_words:
                print(hyper, hyper_)
                hyper_words = self.concept_dict.get(hyper_, '')
                for hyper_ in hyper_words:
                    print(hyper, hyper_)
                    hyper_words = self.concept_dict.get(hyper_, '')
                    for hyper_ in hyper_words:
                        print(hyper, hyper_)
        return

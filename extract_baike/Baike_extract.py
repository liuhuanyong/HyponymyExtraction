#!/usr/bin/env python3
# coding: utf-8
# File: Baike_extract.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-11

from urllib import request
from lxml import etree
from urllib import parse
import jieba.posseg as pseg
import os

'''构造显示图谱'''
class CreatePage:
    def __init__(self, html_name):
        self.html_name = html_name
        self.base = '''
    <html>
    <head>
      <script type="text/javascript" src="VIS/dist/vis.js"></script>
      <link href="VIS/dist/vis.css" rel="stylesheet" type="text/css">
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    </head>
    <body>

    <div id="VIS_draw"></div>
    <script type="text/javascript">
      var nodes = data_nodes;
      var edges = data_edges;

      var container = document.getElementById("VIS_draw");

      var data = {
        nodes: nodes,
        edges: edges
      };

      var options = {
          nodes: {
              shape: 'dot',
              size: 25,
              font: {
                  size: 14
              }
          },
          edges: {
              font: {
                  size: 14,
                  align: 'left'
              },
              color: 'red',
              arrows: {
                  to: {enabled: true, scaleFactor: 0.5}
              },
              smooth: {enabled: true}
          },
          physics: {
              enabled: true
          }
      };

      var network = new vis.Network(container, data, options);

    </script>
    </body>
    </html>
    '''

    '''生成数据'''
    def collect_data(self, nodes, edges):
        node_dict = {node: index for index, node in enumerate(nodes)}
        data_nodes = []
        data_edges = []
        for node, id in node_dict.items():
            data = {}
            data["group"] = 'Event'
            data["id"] = id
            data["label"] = node
            data_nodes.append(data)

        for edge in edges:
            data = {}
            data['from'] = node_dict.get(edge[0])
            data['label'] = 'is-a'
            data['to'] = node_dict.get(edge[1])
            data_edges.append(data)
        return data_nodes, data_edges

    '''生成html文件'''
    def create_html(self, data_nodes, data_edges):
        f = open('{0}.html'.format(self.html_name), 'w+')
        html = self.base.replace('data_nodes', str(data_nodes)).replace('data_edges', str(data_edges))
        f.write(html)
        f.close()


'''图谱展示'''
class EventGraph:
    def __init__(self, relfile, html_name):
        relfile = relfile
        self.html_name = html_name
        self.event_dict, self.node_dict = self.collect_events(relfile)

    '''统计事件频次'''
    def collect_events(self, relfile):
        event_dict = {}
        node_dict = {}
        for line in open(relfile):
            event = line.strip()
            print(event)
            if not event:
                continue
            nodes = event.split('->')
            for node in nodes:
                if node not in node_dict:
                    node_dict[node] = 1
                else:
                    node_dict[node] += 1

            if event not in event_dict:
                event_dict[event] = 1
            else:
                event_dict[event] += 1

        return event_dict, node_dict

    '''过滤低频事件,构建事件图谱'''
    def filter_events(self, event_dict, node_dict):
        edges = []
        nodes = []
        for event in sorted(event_dict.items(), key=lambda asd: asd[1], reverse=True)[:2000]:
            e1 = event[0].split('->')[0]
            e2 = event[0].split('->')[1]
            if e1 in node_dict and e2 in node_dict:
                nodes.append(e1)
                nodes.append(e2)
                edges.append([e1, e2])
            else:
                continue
        return edges, nodes

    '''调用VIS插件,进行事件图谱展示'''
    def show_graph(self):
        edges, nodes = self.filter_events(self.event_dict, self.node_dict)
        handler = CreatePage(self.html_name)
        data_nodes, data_edges = handler.collect_data(nodes, edges)
        handler.create_html(data_nodes, data_edges)

class BaiduBaike:
    def get_html(self, url):
        return request.urlopen(url).read().decode('utf-8').replace('&nbsp;', '')

    def info_extract_baidu(self, word):  # 百度百科
        url = "http://baike.baidu.com/item/%s" % parse.quote(word)
        print(url)
        selector = etree.HTML(self.get_html(url))
        info_list = list()
        info_list.append(self.extract_baidu(selector))
        polysemantics = self.checkbaidu_polysemantic(selector)
        if polysemantics:
            info_list += polysemantics
        infos = [info for info in info_list if len(info) > 2]

        return infos

    def extract_baidu(self, selector):
        info_data = {}
        if selector.xpath('//h2/text()'):
            info_data['current_semantic'] = selector.xpath('//h2/text()')[0].replace('    ', '').replace('（','').replace('）','')
        else:
            info_data['current_semantic'] = ''
        if info_data['current_semantic'] == '目录':
            info_data['current_semantic'] = ''

        info_data['tags'] = [item.replace('\n', '') for item in selector.xpath('//span[@class="taglist"]/text()')]
        if selector.xpath("//div[starts-with(@class,'basic-info')]"):
            for li_result in selector.xpath("//div[starts-with(@class,'basic-info')]")[0].xpath('./dl'):
                attributes = [attribute.xpath('string(.)').replace('\n', '') for attribute in li_result.xpath('./dt')]
                values = [value.xpath('string(.)').replace('\n', '') for value in li_result.xpath('./dd')]
                for item in zip(attributes, values):
                    info_data[item[0].replace('    ', '')] = item[1].replace('    ', '')
        return info_data

    def checkbaidu_polysemantic(self, selector):
        semantics = ['https://baike.baidu.com' + sem for sem in
                     selector.xpath("//ul[starts-with(@class,'polysemantList-wrapper')]/li/a/@href")]
        names = [name for name in selector.xpath("//ul[starts-with(@class,'polysemantList-wrapper')]/li/a/text()")]
        info_list = []
        if semantics:
            for item in zip(names, semantics):
                selector = etree.HTML(self.get_html(item[1]))
                info_data = self.extract_baidu(selector)
                info_data['current_semantic'] = item[0].replace('    ', '').replace('（','').replace('）','')
                if info_data:
                    info_list.append(info_data)
        return info_list

class HudongBaike:
    def get_html(self, url):
        return request.urlopen(url).read().decode('utf-8').replace('&nbsp;', '')

    def info_extract_hudong(self, word):  # 互动百科
        url = "http://www.baike.com/wiki/%s" % parse.quote(word)
        print(url)
        selector = etree.HTML(self.get_html(url))
        info_list = list()
        info_data = self.extract_hudong(selector)
        if selector.xpath('//li[@class="current"]/strong/text()'):
            info_data['current_semantic'] = selector.xpath('//li[@class="current"]/strong/text()')[0].replace('    ', '').replace('（','').replace('）','')
        else:
            info_data['current_semantic'] = ''
        info_list.append(info_data)
        polysemantics = self.checkhudong_polysemantic(selector)
        if polysemantics:
            info_list += polysemantics
        infos = [info for info in info_list if len(info) > 2]
        return infos

    def extract_hudong(self, selector):
        info_data = {}
        info_data['desc'] = selector.xpath('//div[@id="content"]')[0].xpath('string(.)')
        info_data['intro'] = selector.xpath('//div[@class="summary"]')[0].xpath('string(.)').replace('编辑摘要', '')
        info_data['tags'] = [item.replace('\n', '') for item in selector.xpath('//p[@id="openCatp"]/a/text()')]
        for info in selector.xpath('//td'):
            attribute = info.xpath('./strong/text()')
            val = info.xpath('./span')
            if attribute and val:
                value = val[0].xpath('string(.)')
                info_data[attribute[0].replace('：','')] = value.replace('\n','').replace('  ','').replace('    ', '')
        return info_data

    def checkhudong_polysemantic(self, selector):
        semantics = [sem for sem in selector.xpath("//ul[@id='polysemyAll']/li/a/@href") if 'doc_title' not in sem]
        names = [name for name in selector.xpath("//ul[@id='polysemyAll']/li/a/text()")]
        info_list = list()
        if semantics:
            for item in zip(names, semantics):
                selector = etree.HTML(self.get_html(item[1]))
                info_data = self.extract_hudong(selector)
                info_data['current_semantic'] = item[0].replace('（','').replace('）','')
                if info_data:
                    info_list.append(info_data)
        return info_list

class SougouBaike:
    def get_html(self, url):
        return request.urlopen(url).read().decode('utf-8').replace('&nbsp;', '')

    def find_sofouid(self, word):
        url = "http://baike.sogou.com/Search.e?sp=S%s" % parse.quote(word)
        print(url)
        selector = etree.HTML(self.get_html(url))
        id = selector.xpath('//h2/a/@href')[0].split(';')[0]
        info_url = "http://baike.sogou.com/%s"%id
        return info_url

    def info_extract_sogou(self, word):
        info_url = self.find_sofouid(word)
        selector = etree.HTML(self.get_html(info_url))
        info_list = list()
        info_data = self.extract_sogou(selector)
        if selector.xpath('//li[@class="current_item"]/text()'):
            info_data['current_semantic'] = selector.xpath('//li[@class="current_item"]/text()')[0].replace('    ', '').replace('（','').replace('）','')
        else:
            info_data['current_semantic'] = ''

        info_list.append(info_data)
        polysemantics = self.checksogou_polysemantic(selector)
        if polysemantics:
            info_list += polysemantics
        infos = [info for info in info_list if len(info) > 2]
        return infos

    def extract_sogou(self, selector):
        info_data = {}
        info_data['tags'] = [item.replace('\n', '') for item in selector.xpath('//div[@class="relevant_wrap"]/a/text()')]
        if selector.xpath('//li[@class="current_item"]/text()'):
            info_data['current_semantic'] = selector.xpath('//li[@class="current_item"]/text()')[0].replace('    ', '').replace('（','').replace('）','')
        else:
            info_data['current_semantic'] = ''
        tables = selector.xpath('//table[@class="abstract_list"]')
        for table in tables:
            attributes = table.xpath('./tbody/tr/th/text()')
            values = [td.xpath('string(.)') for td in table.xpath('./tbody/tr/td')]
            for item in zip(attributes, values):
                info_data[item[0].replace(' ', '').replace('\xa0','')] = item[1].replace('    ', '')
        return info_data

    def checksogou_polysemantic(self, selector):
        semantics = ['http://baike.sogou.com' + sem.split('?')[0] for sem in selector.xpath("//ol[@class='semantic_item_list']/li/a/@href")]
        names = [name for name in selector.xpath("//ol[@class='semantic_item_list']/li/a/text()")]
        info_list = list()
        if semantics:
            for item in zip(names, semantics):
                selector = etree.HTML(self.get_html(item[1]))
                info_data = self.extract_sogou(selector)
                info_data['current_semantic'] = item[0].replace('（','').replace('）','')
                if info_data:
                    info_list.append(info_data)
        return info_list

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


    '''根据instance本身抽取其概念'''
    def extract_concept(self, word):
        wds = [w.word for w in pseg.cut(word) if w.flag[0] in ['n']]
        if not wds:
            return ''
        else:
            return wds[-1]

    '''对三大百科得到的semantic概念进行对齐'''
    def extract_main(self, word):
        f = open(self.tmp_file, 'w+')
        baidu = BaiduBaike()
        hudong = HudongBaike()
        sogou = SougouBaike()
        semantic_dict = {}
        semantics = []
        tuples = []
        concepts_all = []

        baidu_info = [[i['current_semantic'], i['tags']] for i in baidu.info_extract_baidu(word)]
        hudong_info = [[i['current_semantic'], i['tags']] for i in hudong.info_extract_hudong(word)]
        sogou_info = [[i['current_semantic'], i['tags']] for i in sogou.info_extract_sogou(word)]
        semantics += baidu_info
        semantics += hudong_info
        semantics += sogou_info
        for i in semantics:
            instance = i[0]
            concept = i[1]
            if not instance:
                continue
            if instance not in semantic_dict:
                semantic_dict[instance] = concept
            else:
                semantic_dict[instance] += concept

        # 对从百科知识库中抽取得到的上下位关系进行抽取

        for instance, concepts in semantic_dict.items():
            concepts = set([i for i in concepts if i not in ['', ' ']])
            concept_pre = self.extract_concept(instance)
            concepts_all += concepts
            concepts_all += [concept_pre]
            tuples.append([word, instance])
            tuples.append([instance, concept_pre])
            for concept in concepts:
                tuples.append([instance, concept])

        # 对词汇本身上下位义进行上下位抽取
        tmps = [[i, j] for i in concepts_all for j in concepts_all if j in i and i and j]
        tuples += tmps


        for tuple in tuples:
            if tuple[0] != tuple[1]:
                f.write('->'.join(tuple) + '\n')
        f.close()
        print(tuples)
        handler = EventGraph(self.tmp_file, word)
        handler.show_graph()


def show_graph():
    cur = '/'.join(os.path.realpath(__file__).split('/')[:-1])
    concept_file = os.path.join(cur, 'baike_concept.txt')
    handler = EventGraph(concept_file, 'baike_concept')
    handler.show_graph()


if __name__ == '__main__':
    handler = SemanticBaike()
    handler.extract_main('长江')

    # handler.walk_concept_chain('西瓜')



#!/usr/bin/env python3
# coding: utf-8
# File: kb_search.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-8-11
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

class SemanticBaike:
    def __init__(self):
        cur = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        concept_file = os.path.join(cur, 'baike_concept.txt')
        self.tmp_file = os.path.join(cur, 'word_concept.txt')
        self.path = []
        self.concept_dict, self.down_concept_dict = self.collect_baikeconcept(concept_file)

    '''加载百科上下位概念'''
    def collect_baikeconcept(self, concept_file):
        concept_dict = {}
        down_concept_dict = {}
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

            if category not in down_concept_dict:
                down_concept_dict[category] = [instance]
            else:
                down_concept_dict[category].append(instance)

        return concept_dict, down_concept_dict

    '''基于百科上下位词典进行遍历查询'''
    def walk_up_hyper(self, word):
        f = open(self.tmp_file, 'w+')
        hyper_words = self.concept_dict.get(word, '')
        if not hyper_words:
            return

        for hyper in hyper_words:
            depth = 0
            self.path.append('->'.join([word, hyper]))
            self.back_hyper_up(hyper, depth)

    '''基于既定知识库的深度遍历'''
    def back_hyper_up(self, word, depth):
        depth += 1
        if depth > 5:
            return
        if not word:
            return
        hyper_words = self.concept_dict.get(word, '')
        if not hyper_words:
            return []
        for hyper in hyper_words:
            self.path.append('->'.join([word, hyper]))
            for hyper_ in hyper_words:
                if hyper == 'root':
                    return
                self.back_hyper_up(hyper_, depth)


    '''基于百科上下位词典进行遍历查询'''
    def walk_down_hyper(self, word):
        hyper_words = self.down_concept_dict.get(word, '')
        if not hyper_words:
            return
        for hyper in hyper_words:
            depth = 0
            self.path.append('->'.join([word, hyper]))
            self.back_hyper_down(hyper, depth)


    '''基于既定知识库的深度遍历'''
    def back_hyper_down(self, word, depth):
        depth += 1
        if depth > 1:
            return
        if not word:
            return
        hyper_words = self.down_concept_dict.get(word, '')
        if not hyper_words:
            return []
        for hyper in hyper_words:
            self.path.append('->'.join([hyper, word]))
            for hyper_ in hyper_words:
                if word == 'root':
                    return
                self.back_hyper_down(hyper_, depth)


    '''获取上位和下位'''
    def walk_concept_chain(self, word):
        f = open(self.tmp_file, 'w+')
        # 对其进行上位查找
        self.walk_up_hyper(word)
        #　对其进行下位查找
        # self.walk_down_hyper(word)
        for i in set(self.path):
            f.write(i + '\n')
        f.close()

        handler = EventGraph(self.tmp_file, word)
        handler.show_graph()


word = '孔子'
handler = SemanticBaike()
handler.walk_concept_chain(word)
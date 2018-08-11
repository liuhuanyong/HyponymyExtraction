# HyponymyExtraction
HyponymyExtraction and Graph based on KB Schema, Baike-kb and online text extract, 基于知识概念体系，百科知识库，以及在线搜索结构化方式的词语上下位抽取．
# 项目介绍
上下位关系是语言学概念。概括性较强的单词叫做特定性较强的单词的上位词（hypernym），特定性较强的单词叫做概括性较强的单词的下位词(hyponym)。比如我们说，苹果是一种水果，苹果就是水果的一个下位词，也可以称为一个实例，而水果则是苹果的一个上位词，也可以称为一个类．  
上下位这种语义关系是整个词汇语义关系中的一个重要内容，通过上下位关系，可以将世间万物进行组织和练联系起来，对于增进人们对某一实体或概念的认知上具有重要帮助  
自然语言文本中存储着大量的上下位关系知识，如经过语言专家编辑整理形成的概念语义词典，如同义词词林，中文主题概念词典，hownet等，也存在开放百科知识平台当中，有效地利用这些信息，能够支持多项应用，如：
1) 基于上下位关系的知识问答
2) 基于上下位关系的知识推荐
3) 基于上下位关系的文本理解
本项目主要解决第一个问题，本项目的应用场景是：用户输入一个需要了解的词语，后台通过查询既定知识库，从百百科知识库，在线非结构化文本中进行抽取，形成关于该词语的上下位词语网络，并以图谱这一清晰明了的方式展示出来．

# 本项目将采用三种方式来完成这一目标
1)基于既定知识库的直接查询，对应extract_kb  
2)基于在线百科知识库的抽取，对应extract_baike  
3)基于在线文本的结构化抽取，对应extract_text  

# 项目分解

# 1)基于既定知识库的直接查询
苹果上下位
![image](https://github.com/liuhuanyong/HyponymyExtraction/blob/master/image/concept-apple.png)
长江上下位
![image](https://github.com/liuhuanyong/HyponymyExtraction/blob/master/image/concept-river.png)
孔子上下位
![image](https://github.com/liuhuanyong/HyponymyExtraction/blob/master/image/concept-kongzi.png)

# 2)基于在线百科的概念抽取
苹果上下位
![image](https://github.com/liuhuanyong/HyponymyExtraction/blob/master/image/kb-apple.png)
小米上下位
![image](https://github.com/liuhuanyong/HyponymyExtraction/blob/master/image/kb-xiaomi.png)
姚明上下位
![image](https://github.com/liuhuanyong/HyponymyExtraction/blob/master/image/kb-yaoming.png)


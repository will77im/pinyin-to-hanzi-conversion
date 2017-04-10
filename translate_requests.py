# -*- coding: utf-8 -*-

import requests
from lxml import html

r = requests.post("http://www.cncorpus.org/CpsPinyinTagger.aspx",
                  data={'__VIEWSTATE':'/wEPDwUKMTIyNzIxMTE0NmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgMFBEJEQ1QFBEJEU1oFBEJEU1rxwfNVbDxGh0SzvsNW7cZY4dKdfovOPE9qD0l8oRytiA==',
                        '__VIEWSTATEGENERATOR':'06EE97BC',
                        '__EVENTVALIDATION':'/wEWBwKdhfP6AgK5lIXIBAKTmJvSBQLJ5p+HDgK5mbXLCwK7q7GGCAKliMfhC0+oR8FVMlTdJA+RB9bIs2BiLyiL/dtKsY1EfLRhp96E',
                        'TBin':'输入一段文字，点击“标注汉语拼音”按钮，显示文本的汉语拼音自动标注结果。',
                        'BT1':'Marking Pinyin',
                        '0':'BDSZ',
                        'TBout':''})

tree = html.fromstring(r.content)

pinyin = tree.xpath('//*[@id="TBout"]/text()')

for i in pinyin:
      print i
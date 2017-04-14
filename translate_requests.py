# -*- coding: utf-8 -*-

import requests
from lxml import html


def translate(input):
    data = {
        '__VIEWSTATE': '/wEPDwUKMTIyNzIxMTE0NmQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgMFBEJEQ1QFBEJEU1oFBEJEU1rxwfNVbDxGh0SzvsNW7cZY4dKdfovOPE9qD0l8oRytiA==',
        '__VIEWSTATEGENERATOR': '06EE97BC',
        '__EVENTVALIDATION': '/wEWBwKdhfP6AgK5lIXIBAKTmJvSBQLJ5p+HDgK5mbXLCwK7q7GGCAKliMfhC0+oR8FVMlTdJA+RB9bIs2BiLyiL/dtKsY1EfLRhp96E',
        'TBin': input,
        'BT1': 'Marking Pinyin',
        '0': 'BDSZ',
        'TBout': ''}

    r = requests.post("http://www.cncorpus.org/CpsPinyinTagger.aspx", data=data)

    tree = html.fromstring(r.content)

    pinyin = tree.xpath('//*[@id="TBout"]/text()')

    return pinyin

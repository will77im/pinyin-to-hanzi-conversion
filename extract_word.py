# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import re
import os

pinyin_root_dir = '2474/2474/Lcmc/data/pinyin/'
character_root_dir = '2474/2474/Lcmc/data/character/'

pinyin_list = []
character_list = []

global pinyin_table


def read_all_pinyin():
    global pinyin_table
    pinyin_table = set(open('pinyin.txt').read().splitlines())


def extract_from_xml(root_dir, l):
    current_dic = os.getcwd()
    all_file = os.listdir(current_dic + '/' + root_dir)

    for file_name in all_file:
        print file_name
        tree = ET.parse(current_dic + '/' + root_dir + '/' + file_name)
        root = tree.getroot()
        all_sentence = root.iter('s')

        for sentence in all_sentence:
            for pinyin_word in sentence.findall('w'):
                l.append(pinyin_word.text)
            l.append('EOS')


read_all_pinyin()

extract_from_xml(pinyin_root_dir, pinyin_list)
extract_from_xml(character_root_dir, character_list)

flag = False
with codecs.open('all_in_one.txt', 'w', 'utf-8') as output_file:
    i = 0
    for idx in range(len(pinyin_list)):
        if pinyin_list[idx] == 'EOS' and flag:
            flag = False
            output_file.write('\n')
            continue

        pinyin_sub_before = re.sub(u'[\xb7\uff0e\uff10-\uff19]', '', pinyin_list[idx])
        pinyin_sub = re.sub(u'[^\u0061-\u007A0-9]', '', pinyin_sub_before)

        char_sub = re.sub(u'[^\u4e00-\u9fa5]', '', character_list[idx])

        pinyin = [x for x in re.split(ur'\d', pinyin_sub)[:-1] if x != '']

        char = list(char_sub)
        if len(pinyin) == 0 or len(pinyin) != len(char):
            continue

        pinyin = [x if x in pinyin_table else 'ERROR ' + x for x in pinyin]

        z = zip(pinyin, char)
        output_file.write(' '.join(map(lambda x: x[0] + '/' + x[1], z)) + ' ')
        flag = True

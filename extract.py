# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import re

pinyin_root_dir = '2474/2474/Lcmc/data/pinyin/'
character_root_dir = '2474/2474/Lcmc/data/character/'

pinyin_list = []
character_list = []


def extract_from_xml(root_dir, l):
    for offset in range(18):
        # for offset in range(1):
        if offset == 8 or offset == 14 or offset == 16:
            continue
        # file_name = f
        file_name = root_dir + ('LCMC_%s.xml' % (chr(65 + offset)))
        print file_name
        tree = ET.parse(file_name)
        root = tree.getroot()
        all_sentence = root.iter('s')

        for sentence in all_sentence:
            for pinyin_word in sentence.findall('w'):
                l.append(pinyin_word.text)

            l.append('EOS')


extract_from_xml(pinyin_root_dir, pinyin_list)
extract_from_xml(character_root_dir, character_list)

# w = codecs.open('ttt.txt', 'w', 'utf-8')
with codecs.open('all_in_one.txt', 'w', 'utf-8') as output_file:
    i = 0
    for idx in range(len(pinyin_list)):
        if pinyin_list[idx] == 'EOS':
            output_file.write('\n')
            continue

        pinyin_sub = re.sub(u'[\xb7\uff0e\uff10-\uff19]', '', pinyin_list[idx])
        char_sub = re.sub(u'[^\u4e00-\u9fa5]', '', character_list[idx])

        pinyin = [x for x in re.split(ur'\d', pinyin_sub)[:-1] if x != '']
        char = list(char_sub)
        if len(pinyin) == 0 or len(pinyin) != len(char):
            continue

        z = zip(pinyin, char)
        output_file.write(' '.join(map(lambda x: x[0] + '/' + x[1], z)) + ' ')

        # if len(pinyin) != len(char):
        #     print pinyin, pinyin_sub, list(pinyin_list[idx]), type(pinyin_list[idx]), character_list[idx], char
        #
        #     w.write('line ' + str(i) + '\t' + pinyin_list[idx] + '\t' + character_list[idx] + '\n')
# w.close()

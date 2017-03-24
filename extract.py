# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs

pinyin_root_dir = '2474/2474/Lcmc/data/pinyin/'
character_root_dir = '2474/2474/Lcmc/data/character/'

pinyin_list = []
character_list = []


def extract_from_xml(root_dir, l):
    for offset in range(18):
    # for offset in range(1):
        if offset == 8 or offset == 14 or offset == 16:
            continue
        file_name = root_dir + ('LCMC_%s.xml' % (chr(65 + offset)))
        # with codecs.open(file_name) as file:
        print file_name
        tree = ET.parse(file_name)
        root = tree.getroot()

        all_sentence = root.iter('s')
        for sentence in all_sentence:
            for pinyin_word in sentence.findall('w'):
                # print pinyin.text
                l.append(pinyin_word.text)
            # print 'EOS'
            l.append('EOS')
        # exit()


extract_from_xml(pinyin_root_dir, pinyin_list)
extract_from_xml(character_root_dir, character_list)

print len(pinyin_list)
print len(character_list)

print pinyin_list[:10]
print character_list[:10]

with codecs.open('all_in_one', 'w', 'utf-8') as output_file:
    for idx in range(len(pinyin_list)):
        if pinyin_list[idx] == 'EOS':
            output_file.write('\n')
            continue
        # print type(character_list[idx])
        # exit()
        # try:
            # output_file.write(pinyin_list[idx] + '/' + character_list[idx].encode('utf-8') + ' ')
        output_file.write(pinyin_list[idx] + '/' + character_list[idx] + ' ')
        # except:
        #     print type(character_list[idx])
        #     print character_list[idx]





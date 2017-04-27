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

        word_count = 0
        skip = False
        for sentence in all_sentence:
            temp_list = []
            for word in sentence:
                if word.tag == 'c' and word_count > 0:
                    temp_list.append('EOS')
                    word_count = 0
                elif word.tag == 'w':
                    if u'\xb7' in word.text:
                        skip = True
                        break
                    temp_list.append(word.text)
                    word_count += 1
            if skip:
                skip = False
                continue
            if word_count > 0:
                temp_list.append('EOS')
            l += temp_list


def write_output():

    flag = False
    with codecs.open('data/all_in_one.txt', 'w', 'utf-8') as output_file:
        i = 0
        goto_eos = False
        sentence = ''
        for idx in range(len(pinyin_list)):
            if pinyin_list[idx] == 'EOS':
                if flag:
                    output_file.write(sentence + '\n')
                    flag = False
                if goto_eos:
                    goto_eos = False
                sentence = ''
                continue

            if goto_eos:
                continue

            if bool(re.search(ur'[A-Za-z0-9\u0061-\u007A]', character_list[idx])):
                flag = False
                goto_eos = True
                continue

            pinyin_sub_before = re.sub(u'[\xb7\uff0e\uff10-\uff19]', '', pinyin_list[idx])
            pinyin_sub = re.sub(u'[^\u0061-\u007A0-9]', '', pinyin_sub_before)

            char_sub = re.sub(u'[^\u4e00-\u9fa5]', '', character_list[idx])

            # pinyin = [x for x in re.split(ur'\d', pinyin_sub)[:-1] if x != '']

            # char = list(char_sub)
            # if len(pinyin) == 0 or len(pinyin) != len(char):
            #     continue
            #
            # pinyin = [x if x in pinyin_table else 'ERROR ' + x for x in pinyin]

            # z = zip(pinyin_sub, char)
            if len(pinyin_sub) == 0 or len(char_sub) == 0:
                continue
            sentence += pinyin_sub + '/' + char_sub + ' '
            flag = True


def process():
    read_all_pinyin()

    extract_from_xml(pinyin_root_dir, pinyin_list)
    extract_from_xml(character_root_dir, character_list)
    write_output()

if __name__ == "__main__":
    process()

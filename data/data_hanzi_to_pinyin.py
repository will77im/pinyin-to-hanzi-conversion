# -*- coding: utf-8 -*-
from subprocess import PIPE, Popen
import unicodedata

DATA_FILE = 'data_content.txt'
OUTPUT_FILE = 'data_content_pinyin.txt'

with open(DATA_FILE, 'r') as data_file, open(OUTPUT_FILE, 'w') as output_file:
    for line in data_file:
        sentence = line.strip()
        print sentence
        print type(sentence)
        process = Popen(['trans', '-show-original', 'n', 'zh-CN:zh-CN', sentence], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        print stdout + 'a'
        words = stdout.split('\n')
        data = (words[1].split('(')[1].split(')')[0].decode('utf-8'))
        data = ''.join((c for c in unicodedata.normalize('NFD', data) if unicodedata.category(c) != 'Mn'))
        output_file.write(data + '\n')

# -*- coding: utf-8 -*-
from subprocess import PIPE, Popen
import unicodedata
import time

# DATA_FILE = 'data_content.txt'
DATA_FILE = 'ddd.txt'
OUTPUT_FILE = 'data_content_pinyin.txt'

start = time.time()

i = 0
with open(DATA_FILE, 'r') as data_file, open(OUTPUT_FILE, 'w') as output_file:
    for line in data_file:
        # process = Popen(['trans', '-show-original', 'n', ':zh-CN', line], stdout=PIPE, stderr=PIPE)
        process = Popen(['trans', '-show-original-phonetics', 'Y', line], stdout=PIPE, stderr=PIPE)
        # process = Popen(['trans', '-b', '-show-original', 'zh-CN:zh-CN', line], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        # print stdout
        # exit()
        words = stdout.split('\n')
        data = (words[1].split('(')[1].split(')')[0].decode('utf-8'))
        data = ''.join((c for c in unicodedata.normalize('NFD', data) if unicodedata.category(c) != 'Mn'))
        output_file.write(data + '\n')
        # exit()
        # i += 1
        # print i
        # if i >= 100:
        #     break
end = time.time()
print end - start

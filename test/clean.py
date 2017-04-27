# -*- coding: utf-8 -*-
import codecs
import re
import time

i = 0
# start = time.time()
with codecs.open('../data/testset.txt', encoding='utf-8') as input, \
        codecs.open('../data/cut_testset.txt', 'w', 'utf-8') as output:
    max_len = -1
    min_len = 999999
    t = ''
    for line in input:
        count = 0
        l = line.strip().split(u' ')
        for w in l:
            ww = w.split(u'/')
            hanzi = ww[1]
            count += len(hanzi)
        # if count > max_len:
        #     max_len = count
        #     t = line
        # if count < min_len:
        #     min_len = count
        if count < 4 or count > 36:
            continue
        i += count
        output.write(line)

print i
# print max_len
# print min_len
# print t
# end = time.time()
# print end - start

# s = u'\u67aa\u679d'
# print s

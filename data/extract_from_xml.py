# -*- coding: utf-8 -*-#
import re
import codecs
from multiprocessing import Pool
from multiprocessing import Manager

import translate_requests
import num2hanzi

INPUT_XML = 'news_tensite_xml.dat'
OUTPUT_FILE = 'content_hanzi_pinyin.txt'

# manager = Manager()
# num_map = manager.dict()

# ll = [627275, 647533, 647307, 572483, 697819, 996811, 214685, 643627, 549693, 544835]


def extract(input, output, idx):
    print input
    i = 0
    nn = 0
    num_map = {}
    content_pattern = re.compile(r'(?<=<content>).*(?=</content>)|(?<=<contenttitle>).*(?=</contenttitle>)')
    sentence_pattern = re.compile(u'\u3002|\uFF1F|\uFF01')
    num_pattern = re.compile(u'[\uff10-\uff19]+\uff0e?[\uff10-\uff19]*[\u5e74\uff05]?')
    punctuation_pattern = re.compile(u'[^\u4e00-\u9fa5\uff10-\uff19\uff0e\uff05]+')
    # with open(INPUT_XML, 'r') as xml_file, codecs.open(OUTPUT_FILE, 'w', 'utf-8') as output_file:
    # xx = open(input_file_name).readlines()
    # print len(xx)

    with open(input) as xml_file, codecs.open(output, 'w', 'utf-8') as output_file:
        count = 0

        hanzi = ''
        for line in xml_file:
            # if nn < ll[idx]:
            #     nn += 1
            #     continue
            content = re.search(content_pattern, line)
            if content is None:
                continue
            content = content.group().decode('GBK', 'ignore')
            # split paragraph into sentences
            content = re.split(sentence_pattern, content)
            # iterate each sentence
            for c in content:
                sentence = re.sub(punctuation_pattern, ' ', c)

                if len(sentence) != 0:
                    word_list = re.split(num_pattern, sentence)
                    nums_list = re.findall(num_pattern, sentence)

                    if len(nums_list) != 0:
                        sentence = word_list[0]
                        for ii, num in enumerate(nums_list):
                            if num in num_map:
                                sentence += num_map[num]
                            else:
                                num_trans = num2hanzi.translate(num)
                                sentence += num_trans
                                num_map[num] = num_trans

                            sentence += word_list[ii + 1]
                    count += len(sentence)
                    hanzi += sentence + '\n'

            if count > 90000:
                hanzi_pinyin = translate_requests.translate(hanzi)
                output_file.write(' '.join(hanzi_pinyin).replace('\r', '') + '\n')
                count = 0
                hanzi = ''

                i += 1
                if i % 10 == 0:
                    print str(idx) + ':' + str(i)

                    # if i == 6000:
                    #     print i
                    # break
                    # i += 1
        hanzi_pinyin = translate_requests.translate(hanzi)
        output_file.write(' '.join(hanzi_pinyin).replace('\r', '') + '\n')
        print str(idx) + ':success'
        return

if __name__ == '__main__':
    p = Pool(10)
    input_file_name = 'news_tensite_xml.dat.'
    output_file_name = 'content_hanzi_pinyin.txt.2.'

    for idx in range(10):
        p.apply_async(extract, args=(input_file_name + chr(idx + ord('b')), output_file_name + str(idx + 1), idx,))

    p.close()
    p.join()
    #
    # idx = 0
    # extract(input_file_name + chr(idx + ord('b')), output_file_name + str(idx + 1), idx)

    # cProfile.run('extract()')

import codecs

import extract
import extract_word
import generate_pinyin_hanzi_dict
import random
import count_words
import re

# INPUT_FILE = 'data/clean_content_hanzi_pinyin'
INPUT_FILE = 'data/all_corpus_new'
TRAINING_FILE = 'data/trainset.txt'
TEST_FILE = 'data/testset.txt'
TRAINING_SET_PCNT = 0.9


def create_training_test_set():
    with open(INPUT_FILE, 'r') as input_file, open(TRAINING_FILE, 'w') as training_file, \
            open(TEST_FILE, 'w') as test_file:
        for line in input_file:
            l = line.strip()
            if len(l) == 0:
                continue
            l = l.lower().split()
            # print l.split('/')
            l = map(lambda x: '/'.join(x.split('/')[::-1]), l)
            # print l
            # exit()
            if random.random() < TRAINING_SET_PCNT:
                training_file.write(re.sub(r'\d', '', ' '.join(l)) + '\n')
            else:
                test_file.write(' '.join(l) + '\n')


def clean_test_set():
    with codecs.open('../data/testset.txt', encoding='utf-8') as input, \
            codecs.open('../data/cut_testset.txt', 'w', 'utf-8') as output:
        for line in input:
            count = 0
            l = line.strip().split(u' ')
            for w in l:
                ww = w.split(u'/')
                hanzi = ww[1]
                count += len(hanzi)
            if count < 4 or count > 36:
                continue
            output.write(line)


# extract.process()
# extract_word.process()
# create_training_test_set()
print 'creating training and testing set'
create_training_test_set()

print 'remove short and long sentences in test set'
clean_test_set()

print 'generating pinyin hanzi dictionary'
generate_pinyin_hanzi_dict.generate_dict()

print 'generating ngrams'
count_words.count_words()

print 'hmm learn...'
# hmmlearn
print 'hmm decode...'
# hmmdecode

# hmm

# measure

# -*- coding: utf-8 -*-

import json
import math
import time
import codecs


class ViterbiDecoder(object):
    def __init__(self, target_file_name):
        self.emission_prob = {}
        self.transition_prob = {}
        self.initial_prob = {}
        self.target_file_name = target_file_name
        # self.all_tags = []
        self.pinyin_hanzi = {}
        self.total_hanzi = 0.0
        self.all_pinyin = {}
        self.yuanyin = set([u'i', u'u', u'v'])
        # self.grams = {}
        self.unigram = {}
        self.train_corpus_len = 0
        self.unknown_pinyin = {}

    def read_all_pinyin(self):
        with codecs.open('data/pinyin.txt', encoding='utf-8') as pinyin_file:
            for lines in pinyin_file:
                pinyin = lines.strip()
                pinyin_list = list(pinyin)
                first_letter = pinyin_list[0]
                if first_letter not in self.all_pinyin:
                    self.all_pinyin[first_letter] = set()
                self.all_pinyin[first_letter].add(pinyin)

    def read_pinyin_hanzi_dict(self):
        with codecs.open('data/pinyin_hanzi.txt', encoding='utf-8') as pinyin_hanzi_file:
            for lines in pinyin_hanzi_file:
                items = lines.strip().split('\t')
                pinyin = items[0]
                hanzi = items[1].split()
                self.pinyin_hanzi[pinyin] = hanzi

    def load_model(self):
        with open("data/hmmmodel.txt") as model_file, open('data/word_counts.txt') as grams_file:
            hmm_model = json.load(model_file)
            # model = yaml.load(model_file)
            self.initial_prob = hmm_model[0]
            self.transition_prob = hmm_model[1]
            self.emission_prob = hmm_model[2]

            self.unigram = json.load(grams_file)['1']
            self.train_corpus_len = self.transition_prob['len']

    def backtrack(self, words, backpointer, last_tag):
        sequence = [None] * len(words)
        sequence[-1] = last_tag
        pre_tag = last_tag
        for idx in range(len(words) - 2, -1, -1):
            pre_tag = backpointer[idx][pre_tag]
            sequence[idx] = pre_tag
        return ' '.join(map(lambda x: x[0] + '/' + x[1], zip(words, sequence)))

    def sub_decode(self, pinyin_list):
        backpointer = [None] * (len(pinyin_list) - 1)
        prob_matrix = [None] * len(pinyin_list)

        prob_matrix[0] = {}
        first_pinyin = pinyin_list[0]
        if first_pinyin not in self.pinyin_hanzi:
            return '-'

        pre_hanzi_list = self.pinyin_hanzi[first_pinyin]

        for hanzi in self.pinyin_hanzi[first_pinyin]:
            e = self.emission_prob[hanzi][first_pinyin]
            prob_matrix[0][hanzi] = self.initial_prob[hanzi] + e

        for idx in range(1, len(pinyin_list)):
            prob_matrix[idx] = {}
            backpointer[idx - 1] = {}
            pinyin = pinyin_list[idx]
            back = ""
            if pinyin not in self.pinyin_hanzi:
                return '-'

            for cur_hanzi in self.pinyin_hanzi[pinyin]:
                cur_max_prob = -float('Inf')

                e = self.emission_prob[cur_hanzi][pinyin]

                for pre_hanzi in pre_hanzi_list:
                    if pre_hanzi not in self.transition_prob:
                        self.transition_prob[pre_hanzi] = {}
                    if cur_hanzi not in self.transition_prob[pre_hanzi]:
                        if pre_hanzi in self.unigram:
                            self.transition_prob[pre_hanzi][cur_hanzi] = math.log(
                                0.4 * self.unigram[pre_hanzi] / self.train_corpus_len)
                        else:
                            self.transition_prob[pre_hanzi][cur_hanzi] = math.log(1 / self.train_corpus_len)

                    # prob = prob_matrix[idx - 1][pre_hanzi] + trans_prob
                    prob = prob_matrix[idx - 1][pre_hanzi] + self.transition_prob[pre_hanzi][cur_hanzi]

                    if prob > cur_max_prob:
                        cur_max_prob = prob
                        back = pre_hanzi

                cur_max_prob += e

                backpointer[idx - 1][cur_hanzi] = back
                prob_matrix[idx][cur_hanzi] = cur_max_prob

            pre_hanzi_list = self.pinyin_hanzi[pinyin]

        max_tuple = max([(prob_matrix[-1][tag], tag) for tag in prob_matrix[-1]])
        res = self.backtrack(pinyin_list, backpointer, max_tuple[1])

        return res

    def viterbi_decode(self):
        i = 0
        with codecs.open(self.target_file_name,encoding='utf-8') as target_file:
            with codecs.open("data/hmmoutput.txt", 'w', encoding='utf-8') as output_file:
                for lines in target_file:
                    words = lines.strip().split()
                    pinyin = []
                    for w in words:
                        pinyin.append(w.split('/')[0])
                    if len(pinyin) == 0:
                        continue

                    target_pinyin = []
                    for p in pinyin:
                        if p in self.pinyin_hanzi:
                            target_pinyin.append(p)
                        else:
                            target_pinyin.extend(self.segment_pinyin(p))

                    # print target_pinyin
                    res = self.sub_decode(target_pinyin)

                    i += 1
                    output_file.write(res + '\n')

    def segment_pinyin(self, source):
        if source in self.unknown_pinyin:
            return self.unknown_pinyin[source]
        resultList = []
        begin = 0
        sourceLen = len(source)

        last = ''
        while begin < sourceLen:

            firstLetter = source[begin]
            if firstLetter in self.yuanyin:
                begin -= 1
                firstLetter = source[begin]
                resultList[-1] = last[:-1]

            step = 1
            temp = source[begin]
            for i in range(6):
                if begin + i + 1 > sourceLen:
                    break
                piece = source[begin:begin + i + 1]
                if piece in self.all_pinyin[firstLetter]:
                    temp = piece
                    step = i + 1
            resultList.append(temp)
            last = temp
            begin += step
        self.unknown_pinyin[source] = resultList
        return resultList

    def process(self):
        self.read_pinyin_hanzi_dict()
        self.read_all_pinyin()
        start = time.time()

        self.load_model()
        end = time.time()
        print end - start
        self.viterbi_decode()


if __name__ == "__main__":
    decoder = ViterbiDecoder('data/testset.txt')
    decoder.process()

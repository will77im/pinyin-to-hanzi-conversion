# -*- coding: utf-8 -*-

# date: 03/10/17
# author: Guocheng Chen
# email: guochenc@usc.edu
# description: pos tagger with Viterbi algorithm

import sys
import getopt
import json
import math
import segment2
import time
import cPickle


class ViterbiDecoder(object):
    def __init__(self, target_file_name):
        self.emission_prob = {}
        self.transition_prob = {}
        self.initial_prob = {}
        self.target_file_name = target_file_name
        self.all_tags = []
        self.pinyin_hanzi = {}
        self.total_hanzi = 0.0
        self.all_pinyin = {}
        self.yuanyin = set(['i', 'u', 'v'])

    def recursive_encode(self, obj):
        if isinstance(obj, dict):
            return {self.recursive_encode(key): self.recursive_encode(value) for key, value in obj.iteritems()}
        elif isinstance(obj, unicode):
            return obj.encode('utf-8')
        else:
            return obj

    def encode2utf(self):
        self.initial_prob = self.recursive_encode(self.initial_prob)
        self.transition_prob = self.recursive_encode(self.transition_prob)
        self.emission_prob = self.recursive_encode(self.emission_prob)

    def read_all_pinyin(self):
        with open('data/pinyin.txt') as pinyin_file:
            for lines in pinyin_file:
                pinyin = lines.strip()
                pinyin_list = list(pinyin)
                first_letter = pinyin_list[0]
                if first_letter not in self.all_pinyin:
                    self.all_pinyin[first_letter] = set()
                self.all_pinyin[first_letter].add(pinyin)

        # exit()

    def read_pinyin_hanzi_dict(self):
        s = set()
        with open('data/pinyin_hanzi.txt') as pinyin_hanzi_file:
            for lines in pinyin_hanzi_file:
                items = lines.strip().split('\t')
                pinyin = items[0]
                hanzi = items[1].split()
                self.pinyin_hanzi[pinyin] = hanzi

                for w in hanzi:
                    s.add(w)
        self.total_hanzi = float(len(hanzi))

    def load_model(self):
        with open("data/hmmmodel.txt") as model_file:
            model = json.load(model_file)
            # model = cPickle.load(model_file)
            self.initial_prob = model[0]
            self.transition_prob = model[1]
            self.emission_prob = model[2]
            # print self.initial_prob
            # exit()
            self.encode2utf()
            self.all_tags = [tag for tag in self.initial_prob]

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
            # print hanzi
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
                # print cur_hanzi

                e = self.emission_prob[cur_hanzi][pinyin]

                for pre_hanzi in pre_hanzi_list:

                    # try:
                    if pre_hanzi in self.transition_prob and cur_hanzi in self.transition_prob[pre_hanzi]:
                        trans_prob = self.transition_prob[pre_hanzi][cur_hanzi]
                    elif pre_hanzi in self.transition_prob:
                        trans_prob = math.log(1 / self.transition_prob[pre_hanzi]['total'])
                    else:
                        trans_prob = math.log(1 / self.total_hanzi)

                    prob = prob_matrix[idx - 1][pre_hanzi] + trans_prob

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
        with open(self.target_file_name) as target_file:
            with open("data/hmmoutput.txt", 'w') as output_file:
                for lines in target_file:
                    words = lines.strip().split()
                    pinyin = []
                    for w in words:
                        pinyin.append(w.split('/')[0])
                    if len(pinyin) == 0:
                        continue

                    # pinyin = [p if p in self.pinyin_hanzi else segment.seg(p) for p in pinyin]
                    target_pinyin = []
                    for p in pinyin:
                        if p in self.pinyin_hanzi:
                            target_pinyin.append(p)
                        else:
                            target_pinyin.extend(self.seg(p))

                    # print target_pinyin
                    res = self.sub_decode(target_pinyin)

                    i += 1
                    output_file.write(res + '\n')

    def seg(self, source):
        # print 'into', source
        resultList = []
        begin = 0
        sourceLen = len(source)
        # print type(pyzhDict['n'])

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
        # result = ' '.join(resultList)
        # print 'success'
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
    # opts, args = getopt.getopt(sys.argv[1:], '')
    # decoder = ViterbiDecoder(args[0])
    decoder = ViterbiDecoder('data/testset.txt')
    # decoder = ViterbiDecoder('trainset.txt')
    decoder.process()

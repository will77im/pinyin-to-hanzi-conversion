# -*- coding: utf-8 -*-

# date: 03/10/17
# author: Guocheng Chen
# email: guochenc@usc.edu
# description: pos tagger with Viterbi algorithm

import sys
import getopt
import json
import math


class ViterbiDecoder(object):
    def __init__(self, target_file_name):
        self.emission_prob = {}
        self.transition_prob = {}
        self.initial_prob = {}
        self.target_file_name = target_file_name
        self.all_tags = []
        self.pinyin_hanzi = {}
        self.total_hanzi = 0.0

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

    def read_pinyin_hanzi_dict(self):
        s = set()
        with open('pinyin_hanzi.txt') as pinyin_hanzi_file:
            for lines in pinyin_hanzi_file:
                items = lines.strip().split('\t')
                pinyin = items[0]
                hanzi = items[1].split()
                self.pinyin_hanzi[pinyin] = hanzi

                for w in hanzi:
                    s.add(w)
        self.total_hanzi = float(len(hanzi))

    def load_model(self):
        with open("hmmmodel.txt") as model_file:
            model = json.load(model_file)
            self.initial_prob = model[0]
            self.transition_prob = model[1]
            self.emission_prob = model[2]
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

            for cur_hanzi in self.pinyin_hanzi[pinyin]:
                cur_max_prob = -float('Inf')
                e = self.emission_prob[cur_hanzi][pinyin]

                for pre_hanzi in pre_hanzi_list:

                    # try:
                    if pre_hanzi in self.transition_prob and cur_hanzi in self.transition_prob[pre_hanzi]:
                        trans_prob = self.transition_prob[pre_hanzi][cur_hanzi]
                    elif pre_hanzi in self.transition_prob:
                        trans_prob = math.log(1 / self.transition_prob[pre_hanzi]['total'])
                    else:
                        trans_prob = math.log(1 / self.total_hanzi)

                    # print trans_prob
                    # trans_prob = math.log(trans_prob)
                    # except:
                    #     print pre_hanzi
                    #     exit()

                    prob = prob_matrix[idx - 1][pre_hanzi] + trans_prob

                    if prob > cur_max_prob:
                        cur_max_prob = prob
                        back = pre_hanzi

                cur_max_prob += e

                backpointer[idx - 1][cur_hanzi] = back
                prob_matrix[idx][cur_hanzi] = cur_max_prob

            pre_hanzi_list = self.pinyin_hanzi[pinyin]

        # for b in backpointer:
        #     print ' '.join([x for x in b])
        #     print

        max_tuple = max([(prob_matrix[-1][tag], tag) for tag in prob_matrix[-1]])
        res = self.backtrack(pinyin_list, backpointer, max_tuple[1])

        return res

    def viterbi_decode(self):
        i = 0
        with open(self.target_file_name) as target_file:
            with open("hmmoutput.txt", 'w') as output_file:
                for lines in target_file:
                    words = lines.strip().split()
                    pinyin = []
                    for w in words:
                        pinyin.append(w.split('/')[0])
                    res = self.sub_decode(pinyin)

                    i += 1
                    # print res
                    # if i == 10:


                        # exit()
                    output_file.write(res + '\n')

    def process(self):
        self.read_pinyin_hanzi_dict()
        self.load_model()
        self.viterbi_decode()


if __name__ == "__main__":
    # opts, args = getopt.getopt(sys.argv[1:], '')
    # decoder = ViterbiDecoder(args[0])
    decoder = ViterbiDecoder('testset.txt')
    # decoder = ViterbiDecoder('trainset.txt')
    decoder.process()

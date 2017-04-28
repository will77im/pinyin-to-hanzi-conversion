# -*- coding: utf-8 -*-

import json
import math
import time
import codecs
import cProfile
import re
import norvig


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
        self.unigram = {}
        self.train_corpus_len = 0
        self.unknown_pinyin = {}

        self.train_corpus_len_1 = 0
        self.train_corpus_len_4 = 0

        self.ft = 0

        self.norvig_obj = None
        self.typo_correction = False
        self.typo_bigram_prev = False
        self.typo_bigram_next = False

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
            self.initial_prob = hmm_model[0]
            self.transition_prob = hmm_model[1]
            self.emission_prob = hmm_model[2]

            self.unigram = json.load(grams_file)['1']
            self.train_corpus_len = self.transition_prob['len']
            self.train_corpus_len_1 = math.log(1 / self.train_corpus_len)
            self.train_corpus_len_4 = math.log(0.4 / self.train_corpus_len)

    def backtrack(self, words, backpointer, last_tag):
        sequence = [None] * len(words)
        sequence[-1] = last_tag
        pre_tag = last_tag
        for idx in range(len(words) - 2, -1, -1):
            pre_tag = backpointer[idx][pre_tag]
            sequence[idx] = pre_tag
        del backpointer
        return ' '.join(map(lambda x: x[0] + '/' + x[1], zip(words, sequence)))

    # @profile
    def sub_decode(self, pinyin_list):
        backpointer = [None] * (len(pinyin_list) - 1)
        prob_matrix = [None] * len(pinyin_list)

        prob_matrix[0] = {}
        first_pinyin = pinyin_list[0]
        if first_pinyin not in self.pinyin_hanzi:
            # del backpointer[:]
            # del prob_matrix[:]
            if self.typo_correction and self.norvig_obj is not None:
                next_word = None
                if self.typo_bigram_next and len(pinyin_list) > 1:
                    next_word = pinyin_list[1]
                corrected = self.norvig_obj.correct_typo(first_pinyin, prev_word=None, next_word=next_word)
                if corrected == first_pinyin:
                    return '-'
                first_pinyin = corrected
            else:
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
                # del backpointer[:]
                # del prob_matrix[:]
                if self.typo_correction and self.norvig_obj is not None:
                    prev_word = None
                    next_word = None
                    if self.typo_bigram_prev:
                        prev_word = pinyin_list[idx-1]
                    if self.typo_bigram_next and idx < len(pinyin_list)-1:
                        next_word = pinyin_list[idx+1]
                    corrected = self.norvig_obj.correct_typo(pinyin, prev_word=prev_word, next_word=next_word)
                    if corrected == pinyin:
                        return '-'
                    pinyin = corrected
                else:
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
                                self.unigram[pre_hanzi]) + self.train_corpus_len_4
                        else:
                            self.transition_prob[pre_hanzi][cur_hanzi] = self.train_corpus_len_1

                    prob = prob_matrix[idx - 1][pre_hanzi] + self.transition_prob[pre_hanzi][cur_hanzi]

                    if prob > cur_max_prob:
                        cur_max_prob = prob
                        back = pre_hanzi

                cur_max_prob += e

                backpointer[idx - 1][cur_hanzi] = back
                prob_matrix[idx][cur_hanzi] = cur_max_prob

            pre_hanzi_list = self.pinyin_hanzi[pinyin]

        max_tuple = max([(prob_matrix[-1][tag], tag) for tag in prob_matrix[-1]])
        # res = self.backtrack(pinyin_list, backpointer, max_tuple[1])
        # words, backpointer, last_tag
        # words = pinyin_list
        # last_tag = max_tuple[1]
        sequence = [None] * len(pinyin_list)
        sequence[-1] = max_tuple[1]
        pre_tag = max_tuple[1]
        for idx in range(len(pinyin_list) - 2, -1, -1):
            pre_tag = backpointer[idx][pre_tag]
            sequence[idx] = pre_tag

        # del backpointer[:]
        # del prob_matrix[:]

        return ' '.join(map(lambda x: x[0] + '/' + x[1], zip(pinyin_list, sequence)))

        # del prob_matrix
        # del backpointer

        # return res

    def viterbi_decode(self):
        i = 0
        with codecs.open(self.target_file_name, encoding='utf-8') as target_file:
            with codecs.open("data/hmmoutput.txt", 'w', encoding='utf-8') as output_file:
                for lines in target_file:
                    # self.ft += 1
                    # if self.ft % 5000 == 0:
                    #     print 'emi: ' + str(sys.getsizeof(self.emission_prob))
                    #     print 'tran: ' + str(sys.getsizeof(self.transition_prob))
                    #     print 'ini: ' + str(sys.getsizeof(self.initial_prob))
                    #     print 'unknown: ' + str(sys.getsizeof(self.unknown_pinyin))
                    #     print '---------'
                    words = lines.strip().split()
                    pinyin = []
                    flag = False
                    for w in words:
                        ww = w.split('/')[0]
                        if ww == '':
                            flag = True
                            break
                        pinyin.append(ww)
                    # if len(pinyin) == 0:
                    #     continue
                    if flag:
                        output_file.write('-\n')
                        continue
                    target_pinyin = []

                    for p in pinyin:
                        pinyin_no_tone = re.sub(r'\d', '', p)
                        if pinyin_no_tone in self.pinyin_hanzi:
                            target_pinyin.append(pinyin_no_tone)
                        else:
                            pinyin_split = re.findall(r'[a-zA-Z]+', p)
                            # if p not in self.unknown_pinyin:
                            #     self.unknown_pinyin[p] = pinyin_split
                            # target_pinyin.extend(self.unknown_pinyin[p])
                            # print pinyin_split[:-1]
                            # print lines
                            # exit()
                            target_pinyin.extend(pinyin_split)

                    res = self.sub_decode(target_pinyin)
                    # res = self.sub_decode2(target_pinyin)

                    i += 1
                    output_file.write(res + '\n')

    def sub_decode2(self, l):
        return "test"

    def process(self, typo_correction=False, typo_train_file=None, typo_bigram_prev=False, typo_bigram_next=False):
        self.typo_correction = typo_correction
        self.typo_bigram_prev = typo_bigram_prev
        self.typo_bigram_next = typo_bigram_next
        if self.typo_correction and typo_train_file:
            self.norvig_obj = norvig.Norvig(typo_train_file)

        self.read_pinyin_hanzi_dict()
        self.read_all_pinyin()
        start = time.time()

        self.load_model()
        end = time.time()
        print end - start
        self.viterbi_decode()

    def main(self):
        cProfile.runctx('self.process()', globals(), locals())


if __name__ == "__main__":
    # decoder = ViterbiDecoder('data/cut_testset.txt')
    decoder = ViterbiDecoder('data/cut_lcmc_a')
    # decoder = ViterbiDecoder('data/ttt')
    # cProfile.run(decoder.process())
    decoder.process(typo_correction=False, typo_train_file='data/trainset.txt', typo_bigram_prev=False, typo_bigram_next=False)
    # decoder.main()

# -*- coding: utf-8 -*-

import math
import json


class HMM(object):
    def __init__(self, input):
        self.train_file_name = input
        self.emission_prob = {}
        self.transition_prob = {}

        self.initial_prob = {}
        self.transition_prob_template = {}
        self.total = 0.0

        # self.grams = {}

    def read_all_characters(self):
        self.initial_prob['total'] = 0.0
        # self.transition_prob_template['total'] = 0.0
        with open('data/pinyin_hanzi.txt') as pinyin_hanzi_file:
            for lines in pinyin_hanzi_file:
                chars = lines.strip().split('\t')[1].split()
                for char in chars:
                    if char not in self.initial_prob:
                        self.initial_prob[char] = 1
                        self.initial_prob['total'] += 1

                        # self.transition_prob_template[char] = 1
                        # self.transition_prob_template['total'] += 1
                        self.total += 1

    def convert2log(self):
        for tag in self.initial_prob:
            if tag == "total":
                continue
            if self.initial_prob[tag] == 0:
                self.initial_prob[tag] = -1000000
            else:
                self.initial_prob[tag] = math.log(self.initial_prob[tag] / self.initial_prob["total"])
        # del self.initial_prob["total"]

        # for tag in self.transition_prob:
        #     for trans_tag in self.transition_prob[tag]:
        #         if trans_tag == "total":
        #             continue
        #         self.transition_prob[tag][trans_tag] = math.log(
        #             self.transition_prob[tag][trans_tag] / self.transition_prob[tag]["total"])
                # del self.transition_prob[tag]["total"]

        for tag in self.emission_prob:
            for word in self.emission_prob[tag]:
                if word == "# total #":
                    continue
                self.emission_prob[tag][word] = math.log(
                    self.emission_prob[tag][word] / self.emission_prob[tag]["# total #"])
            del self.emission_prob[tag]["# total #"]

    def load_corpus(self, smoothing='default'):
        with open(self.train_file_name) as input_file:
            for lines in input_file:
                items = lines.strip().split()
                idx = 0
                pre_tag = ""
                for word_tag in items:
                    s = word_tag.split('/')
                    word = s[0]
                    tag = s[1]

                    if idx == 0:
                        # initial probability
                        self.initial_prob[tag] = self.initial_prob.get(tag, 0) + 1
                        self.initial_prob["total"] += 1
                    else:
                        # transition probability

                        if smoothing == 'default':

                            if pre_tag not in self.transition_prob:
                                self.transition_prob[pre_tag] = {'total': self.total}

                            self.transition_prob[pre_tag][tag] = self.transition_prob[pre_tag].get(tag, 1) + 1
                            self.transition_prob[pre_tag]["total"] += 1

                        else:
                            pass

                    # emission probability
                    if tag not in self.emission_prob:
                        self.emission_prob[tag] = {"# total #": 0.0}

                    self.emission_prob[tag][word] = self.emission_prob[tag].get(word, 0) + 1
                    self.emission_prob[tag]["# total #"] += 1

                    idx += 1
                    pre_tag = tag

    def load_grams(self):
        with open('data/word_counts.txt') as grams_file:
            grams_model = json.load(grams_file)
            bigram_stats = grams_model['2']
            unigram_stats = grams_model['1']

            for bigram in bigram_stats:
                grams = bigram.split(u',')
                pre_word = grams[0]
                cur_word = grams[1]

                if pre_word in unigram_stats:
                    if pre_word not in self.transition_prob:
                        self.transition_prob[pre_word] = {}
                    self.transition_prob[pre_word][cur_word] = math.log(
                        float(bigram_stats[bigram]) / unigram_stats[pre_word])

            # self.transition_prob['len'] = {}
            self.transition_prob['len'] = float(sum(unigram_stats.values()))

    def output_model(self):
        model = [self.initial_prob, self.transition_prob, self.emission_prob]
        output_file = open("data/hmmmodel.txt", 'w')
        # json.dump(model, output_file, ensure_ascii=False, indent=4)
        json.dump(model, output_file, indent=4)
        output_file.close()

    def process(self):
        self.read_all_characters()
        self.load_corpus(smoothing='stupid')
        self.load_grams()
        self.convert2log()
        self.output_model()


if __name__ == "__main__":
    hmm = HMM('data/trainset.txt')
    hmm.process()

# -*- coding: utf-8 -*-

# date: 03/10/17
# author: Guocheng Chen
# email: guochenc@usc.edu
# description: learn the HMM

import sys
import math
import copy
import json
import getopt


class HMM(object):
    def __init__(self, input):
        self.train_file_name = input
        self.emission_prob = {}
        self.transition_prob = {}
        # self.initial_prob = {'DI': 1, 'DD': 1, 'DA': 1, 'WW': 1, 'FF': 1, 'DT': 1, 'DR': 1, 'DP': 1, 'PR': 1, 'PP': 1,
        #                      'PT': 1, 'PX': 1, 'NC': 1, 'RG': 1, 'PD': 1, 'NP': 1, 'RN': 1, 'PI': 1, 'VA': 1, 'P0': 1,
        #                      'CC': 1, 'VM': 1, 'AO': 1, 'AQ': 1, 'VS': 1, 'ZZ': 1, 'CS': 1, 'II': 1, 'SP': 1,
        #                      'total': 29.0}
        # self.transition_prob_template = {'DI': 1, 'DD': 1, 'DA': 1, 'WW': 1, 'FF': 1, 'DT': 1, 'DR': 1, 'DP': 1,
        #                                  'PR': 1, 'PP': 1,
        #                                  'PT': 1, 'PX': 1, 'NC': 1, 'RG': 1, 'PD': 1, 'NP': 1, 'RN': 1, 'PI': 1,
        #                                  'VA': 1, 'P0': 1,
        #                                  'CC': 1, 'VM': 1, 'AO': 1, 'AQ': 1, 'VS': 1, 'ZZ': 1, 'CS': 1, 'II': 1,
        #                                  'SP': 1,
        #                                  'total': 29.0}

        self.initial_prob = {}
        self.transition_prob_template = {}
        self.total = 0.0
        # self.transition_prob

    def read_all_characters(self):
        self.initial_prob['total'] = 0.0
        # self.transition_prob_template['total'] = 0.0
        with open('pinyin_hanzi.txt') as pinyin_hanzi_file:
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

        for tag in self.transition_prob:
            for trans_tag in self.transition_prob[tag]:
                if trans_tag == "total":
                    continue
                self.transition_prob[tag][trans_tag] = math.log(
                    self.transition_prob[tag][trans_tag] / self.transition_prob[tag]["total"])
            # del self.transition_prob[tag]["total"]

        for tag in self.emission_prob:
            for word in self.emission_prob[tag]:
                if word == "# total #":
                    continue
                self.emission_prob[tag][word] = math.log(
                    self.emission_prob[tag][word] / self.emission_prob[tag]["# total #"])
            del self.emission_prob[tag]["# total #"]

    def load_corpus(self):
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

                        if pre_tag not in self.transition_prob:
                            self.transition_prob[pre_tag] = {'total': self.total}

                        self.transition_prob[pre_tag][tag] = self.transition_prob[pre_tag].get(tag, 1) + 1
                        self.transition_prob[pre_tag]["total"] += 1

                    # emission probability
                    if tag not in self.emission_prob:
                        self.emission_prob[tag] = {"# total #": 0.0}

                    self.emission_prob[tag][word] = self.emission_prob[tag].get(word, 0) + 1
                    self.emission_prob[tag]["# total #"] += 1

                    idx += 1
                    pre_tag = tag

    def output_model(self):
        model = [self.initial_prob, self.transition_prob, self.emission_prob]
        output_file = open("hmmmodel.txt", 'w')
        json.dump(model, output_file, ensure_ascii=False, indent=4)
        output_file.close()

    def process(self):
        self.read_all_characters()
        self.load_corpus()
        self.convert2log()
        self.output_model()


if __name__ == "__main__":
    # opts, args = getopt.getopt(sys.argv[1:], '')
    hmm = HMM('all_in_one.txt')
    hmm.process()

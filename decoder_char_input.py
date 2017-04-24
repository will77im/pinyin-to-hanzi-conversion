# -*- coding: utf-8 -*-
import json
import math
import time
import codecs

def add_reverse(l,words):
    for i in list(reversed(words)):
        l.append(i)
def split_words(pinyin_list, hanzis, n):
    res = []
    end  = n-1 
    for i in range(0,end):
        hanzi = hanzis[i]
        pinyin = pinyin_list[i]
        str = hanzi+'/'+pinyin
        res.append(str)
    hanzi = hanzis[n-1:]
    pinyin = pinyin_list[n-1]
    str = hanzi+'/'+pinyin
    res.append(str)
    return res
class ViterbiDecoder(object):
    def __init__(self, target_file_name):
        self.emission_prob = {}
        self.transition_prob = {}
        self.initial_prob = {}
        self.target_file_name = target_file_name
        self.pinyin_hanzi = {}
        self.total_hanzi = 0.0
        self.all_pinyin = {}
        self.yuanyin = set([u'i', u'u', u'v'])
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
            print 'loading json'
            hmm_model = json.load(model_file)
            print 'json is loaded'
            self.initial_prob = hmm_model[0]
            print 'json is loaded'
            self.transition_prob = hmm_model[1]
            print 'transition is loaded'
            self.emission_prob = hmm_model[2]
            print 'emission is loaded'
            self.unigram = json.load(grams_file)['1']
            self.train_corpus_len = self.transition_prob['len']


    def backtrack(self, words, backpointer, last_tag,hanzi_at_loc):
        end = len(words)-1
        idx = end
        pre_tag = last_tag
        last_n = hanzi_at_loc[idx][last_tag]
        l = []
        idx -= hanzi_at_loc[idx][last_tag]
        w = split_words(words[len(words)-last_n:],pre_tag,last_n)
        add_reverse(l,w)
        while idx >= 0:
            tmp = pre_tag
            pre_tag = backpointer[idx][pre_tag]
            step = hanzi_at_loc[idx][pre_tag]
            w = split_words(words[idx-step+1:idx+1],pre_tag,step)
            add_reverse(l,w)
            idx -= step
        res = ''
        for i in reversed(l):
            res += i + ' '
        res = res.strip()
        return res
    def sub_decode(self, pinyin_list):
        backpointer = [{} for i in range(len(pinyin_list))]
        prob_matrix = [{} for i in range(len(pinyin_list))]
        pinyin_at_loc = {}
        hanzi_at_loc = [{} for i in range(len(pinyin_list))]
        pre_pinyin = ''
        for n in range(1,5):
            if n >= len(pinyin_list):
                break
            first_pinyin = ''
            for p in pinyin_list[0:n]:
                first_pinyin += p
            if first_pinyin not in self.pinyin_hanzi:
                continue
            for hanzi in self.pinyin_hanzi[first_pinyin]:
                e = self.emission_prob[hanzi][first_pinyin]

                hanzi_at_loc[n-1][hanzi] = n
                prob_matrix[n-1][hanzi] = self.initial_prob[hanzi] + e
                pinyin_at_loc[n-1] = []
                pinyin_at_loc[n-1].append((first_pinyin,n))
        for idx in range(1, len(pinyin_list)):
            tag = ''
            backpointer[idx - 1] = {}
            if idx not in pinyin_at_loc:
                pinyin_at_loc[idx] = []
            for n in range(1,5):
                if idx - n >= 0:
                    pinyin = ''
                    for p in pinyin_list[idx-n+1:idx+1]:
                        pinyin += p
                    back = ''
                    if pinyin not in self.pinyin_hanzi:
                        continue
                    t = idx-n
                    if t in pinyin_at_loc:
                        pre_pinyin_list = pinyin_at_loc[t]

                    for cur_hanzi in self.pinyin_hanzi[pinyin]:
                        if cur_hanzi in prob_matrix[idx]:
                            continue
                        hanzi_at_loc[idx][cur_hanzi] = n
                        pinyin_at_loc[idx].append((pinyin,n))
                        cur_max_prob = -float('Inf')
                        prob_matrix[idx][cur_hanzi] = cur_max_prob
                        e = self.emission_prob[cur_hanzi][pinyin]
                        pre_hanzi_list = []
                        if len(pre_pinyin_list) != 0:
                            for pre_pinyin in pre_pinyin_list:
                                for hanzi in self.pinyin_hanzi[pre_pinyin[0]]:
                                    pre_hanzi_list.append(hanzi)
                        for pre_hanzi in pre_hanzi_list:
                            if pre_hanzi not in self.transition_prob:
                                self.transition_prob[pre_hanzi] = {}
                            if cur_hanzi not in self.transition_prob[pre_hanzi]:
                                if pre_hanzi in self.unigram:
                                    self.transition_prob[pre_hanzi][cur_hanzi] = math.log(
                                        0.4 * self.unigram[pre_hanzi] / self.train_corpus_len)
                                else:
                                    self.transition_prob[pre_hanzi][cur_hanzi] = math.log(1 / self.train_corpus_len)         
                            prob = prob_matrix[idx - n][pre_hanzi] 
                            prob += self.transition_prob[pre_hanzi][cur_hanzi]
                            if prob > cur_max_prob:
                                cur_max_prob = prob
                                back = pre_hanzi
                                tag = cur_hanzi
                        cur_max_prob += e
                        prob_matrix[idx][cur_hanzi] = cur_max_prob
                        t = idx-n
                        backpointer[t][cur_hanzi] = back
        max_tuple = max([(prob_matrix[-1][tag], tag) for tag in prob_matrix[-1]])
        res = self.backtrack(pinyin_list, backpointer, max_tuple[1],hanzi_at_loc)
        return res

    def viterbi_decode(self):
        i = 0
        line_count = 0
        with codecs.open(self.target_file_name,encoding='utf-8') as target_file:
            with codecs.open("data/hmmoutput_c.txt", 'w', encoding='utf-8') as output_file:
                for lines in target_file:
                    line_count += 1
                    words = lines.strip().split()
                    pinyin = []
                    for w in words:
                        s = w.split('/')[1]
                        s = ''.join([i for i in s if not i.isdigit()])
                        pinyin.append(s)
                    if len(pinyin) == 0:
                        continue
                    target_pinyin = []
                    for p in pinyin:
                        if p in self.pinyin_hanzi:
                            target_pinyin.append(p)
                        else:
                            pass
                    res = self.sub_decode(target_pinyin)
                    output_file.write(res + '\n')
                    if line_count % 10 == 0:
                        print line_count
    def process(self):
        self.read_pinyin_hanzi_dict()
        self.read_all_pinyin()
        start = time.time()
        print 'try to load model'
        self.load_model()
        print 'model loading complete'
        end = time.time()
        print end - start
        self.viterbi_decode()


if __name__ == "__main__":
    decoder = ViterbiDecoder('data/sample.txt')
    decoder.process()
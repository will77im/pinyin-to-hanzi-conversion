'''
Credit to Peter Norvig
'''
import re
from collections import Counter


class Norvig(object):

    WORDS = {}
    WORD_BIGRAMS = {}

    def __init__(self, input_file):
        self.create_word_dict(input_file)

    def words(self, text):
        return re.findall(r'\w+', re.sub(r'[^a-zA-Z ]', '', text).lower())

    def create_word_dict(self, input_file, bigrams=True):
        with open(input_file, 'r') as in_file:
            self.WORDS = Counter(self.words(in_file.read()))
            if bigrams:
                in_file.seek(0)
                lines = in_file.read().splitlines()
                for line in lines:
                    words = re.sub(r'[^a-zA-Z ]', '', line).lower().strip().split()
                    for i in range(len(words) - 1):
                        if words[i] not in self.WORD_BIGRAMS:
                            self.WORD_BIGRAMS[words[i]] = {}
                        if words[i+1] not in self.WORD_BIGRAMS[words[i]]:
                            self.WORD_BIGRAMS[words[i]][words[i+1]] = 1
                        else:
                            self.WORD_BIGRAMS[words[i]][words[i+1]] += 1

    def P(self, word, N=sum(WORDS.values())):
        "Probability of `word`."
        return self.WORDS[word] / N

    def correction(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.WORDS)

    def edits1(self, word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def correct_typo(self, word, prev_word=None, next_word=None):
        candidates = self.candidates(word)
        if word in candidates:
            return word
        if (prev_word is None and next_word is None) or len(self.WORD_BIGRAMS) == 0:
            highest_freq = 0
            best_word = word
            for w in candidates:
                if self.WORDS[w] > highest_freq:
                    highest_freq = self.WORDS[w]
                    best_word = w
            return best_word
        freqs = dict.fromkeys(candidates, 0)
        if prev_word is not None:
            for cur_word in candidates:
                if prev_word in self.WORD_BIGRAMS and cur_word in self.WORD_BIGRAMS[prev_word]:
                    freqs[cur_word] = self.WORD_BIGRAMS[prev_word][cur_word]
        if next_word is not None:
            for cur_word in candidates:
                if cur_word in self.WORD_BIGRAMS and next_word in self.WORD_BIGRAMS[cur_word]:
                    freqs[cur_word] += self.WORD_BIGRAMS[cur_word][next_word]
        return max(freqs, key=freqs.get)

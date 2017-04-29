import norvig
import random
import string
import re

TEST_FILE = 'data/all_corpus_new_test2'
NORVIG_TRAIN_FILE = 'data/all_corpus_new_train2'

ERROR_THRESHOLDS = [0.25, 0.5, 0.75]
EDIT_DIST2_RATE = 0.1
SUBSET_PCT = 0.15
TEST_WORD_PCT = 0.05

def create_train_test_set():
    train_pct = 0.98
    with open("data/all_corpus_new", "r") as corpus_file, \
        open(NORVIG_TRAIN_FILE, 'w') as train_file, \
        open(TEST_FILE, 'w') as test_file:
        for line in corpus_file:
            if random.random() < SUBSET_PCT:
                if random.random() < train_pct:
                    train_file.write(line)
                else:
                    test_file.write(line)


def apply_insert_error(word):
    error_idx = random.randint(0, len(word)-1)
    return word[:error_idx] + random.choice(string.ascii_lowercase) + word[error_idx:]


def apply_del_error(word):
    if len(word) < 2:
        return word
    error_idx = random.randint(0, len(word)-1)
    return word[:error_idx] + word[error_idx+1:]


def apply_transpose_error(word):
    if len(word) < 2:
        return word
    error_idx = random.randint(0, len(word) - 2)
    return word[:error_idx] + word[error_idx + 1] + word[error_idx] + word[error_idx+1:]


def apply_replace_error(word):
    error_idx = random.randint(0, len(word) - 1)
    new_char = random.choice(string.ascii_lowercase)
    while new_char == word[error_idx]:
        new_char = random.choice(string.ascii_lowercase)
    return word[:error_idx] + new_char + word[error_idx+1:]


def apply_typo(word):
    error_type = random.random()
    if error_type < ERROR_THRESHOLDS[0]:
        return apply_insert_error(word)
    elif error_type < ERROR_THRESHOLDS[1]:
        return apply_del_error(word)
    elif error_type < ERROR_THRESHOLDS[2]:
        return apply_transpose_error(word)
    else:
        return apply_replace_error(word)


def compute_accuracy(stats):
    return str(float(stats[0]) / float(stats[1]))


def measure_spell_correction_accuracy():
    unigram_stats = [0, 0] # correct, total
    bigram_prev_stats = [0, 0]
    bigram_prev_next_stats = [0, 0]
    n = norvig.Norvig(NORVIG_TRAIN_FILE)
    print "Done training\n"
    with open(TEST_FILE, 'r') as test_file:
        for line in test_file:
            cleaned_line = re.sub(r'[^a-zA-Z ]', '', line).lower()
            words = cleaned_line.strip().split()
            for i in range(len(words)):
                if random.random() > TEST_WORD_PCT:
                    continue
                word = words[i]
                unigram_stats[1] += 1
                typo = apply_typo(word)
                if random.random() < EDIT_DIST2_RATE:
                    typo = apply_typo(typo)
                    while typo == word:
                        typo = apply_typo(typo)
                # unigram test
                correction = n.correct_typo(typo)
                if correction == word:
                    unigram_stats[0] += 1
                # bigram_prev test
                if i > 0:
                    bigram_prev_stats[1] += 1
                    correction = n.correct_typo(typo, prev_word=words[i-1])
                    if correction == word:
                        bigram_prev_stats[0] += 1
                    if i < len(words) - 1:
                        bigram_prev_next_stats[1] += 1
                        correction = n.correct_typo(typo, prev_word=words[i - 1], next_word=words[i+1])
                        if correction == word:
                            bigram_prev_next_stats[0] += 1
    print 'Unigram accuracy:', compute_accuracy(unigram_stats), unigram_stats
    print 'Bigram Prev accuracy:', compute_accuracy(bigram_prev_stats), bigram_prev_stats
    print 'Bigram Prev Next accuracy:', compute_accuracy(bigram_prev_next_stats), bigram_prev_next_stats

if __name__ == "__main__":
    #create_train_test_set()
    measure_spell_correction_accuracy()
import random
import re
import string

TEST_FILE = 'testset.txt'
OUTPUT_FILE = 'testset_typos.txt'
TYPO_RATE = 0.34
ERROR_THRESHOLDS = [0.25, 0.5, 0.75]
SECOND_TYPO_RATE = 0.3
EDIT_DIST2_RATE = 0.1


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


def apply_typo(words, typo_idx):
    typo_word_parts = words[typo_idx].strip().split('/')
    split_tones = re.findall('\d+|\D+', typo_word_parts[0])
    typo_char_idx = 2 * random.randint(0, (len(split_tones) - 1) / 2)
    word = split_tones[typo_char_idx]

    error_type = random.random()
    if error_type < ERROR_THRESHOLDS[0]:
        word = apply_insert_error(word)
    elif error_type < ERROR_THRESHOLDS[1]:
        word = apply_del_error(word)
    elif error_type < ERROR_THRESHOLDS[2]:
        word = apply_transpose_error(word)
    else:
        word = apply_replace_error(word)

    split_tones[typo_char_idx] = word
    typo_word_parts[0] = ''.join(split_tones)
    return typo_word_parts[0] + '/' + typo_word_parts[1]


def add_typos():
    with open(TEST_FILE, 'r') as test_file, open(OUTPUT_FILE, 'w') as out_file:
        for line in test_file:
            if random.random() > TYPO_RATE:
                out_file.write(line)
                continue
            words = line.strip().split()
            typo_idx = random.randint(0, len(words)-1)
            words[typo_idx] = apply_typo(words, typo_idx)
            if random.random() < EDIT_DIST2_RATE:
                words[typo_idx] = apply_typo(words, typo_idx)
            if random.random() < SECOND_TYPO_RATE and len(words) > 1:
                second_typo_idx = random.randint(0, len(words)-1)
                while second_typo_idx == typo_idx:
                    second_typo_idx = random.randint(0, len(words)-1)
                words[second_typo_idx] = apply_typo(words, second_typo_idx)
                if random.random() < EDIT_DIST2_RATE:
                    words[second_typo_idx] = apply_typo(words, second_typo_idx)
            new_sentence = ' '.join(words) + '\n'
            out_file.write(new_sentence)

if __name__ == "__main__":
    add_typos()

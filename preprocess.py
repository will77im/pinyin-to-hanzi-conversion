import extract
import extract_word
import generate_pinyin_hanzi_dict
import random

# INPUT_FILE = 'data/all_in_one.txt'
INPUT_FILE = 'data/clean_content_hanzi_pinyin'
TRAINING_FILE = 'data/trainset.txt'
TEST_FILE = 'data/testset.txt'
TRAINING_SET_PCNT = 0.9


def create_training_test_set():
    with open(INPUT_FILE, 'r') as input_file, open(TRAINING_FILE, 'w') as training_file, \
            open(TEST_FILE, 'w') as test_file:
        for line in input_file:
            l = line.lower()
            if random.random() < TRAINING_SET_PCNT:
                training_file.write(l)
            else:
                test_file.write(l)


# extract.process()
# extract_word.process()
create_training_test_set()
generate_pinyin_hanzi_dict.generate_dict()

# hmm

# measure

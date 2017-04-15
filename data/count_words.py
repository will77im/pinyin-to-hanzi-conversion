import json

INPUT_FILE = 'clean_content_hanzi_pinyin_50000_line'
OUTPUT_FILE = 'word_counts.txt'


def count_words(n_gram=2, char_level=False):
    '''
    :param: n_gram: n-gram (2 for bigram, 3 for trigram, etc)
    :param char_level: True for character level counts, and False for word level
    :return: nothing, writes to file
    '''
    word_count_dict = {}
    with open(INPUT_FILE, 'r') as in_file, open(OUTPUT_FILE, 'w') as out_file:
        lines = in_file.read().splitlines()
        for line in lines:
            pinyin_hanzi = line.strip().split(' ')
            hanzi = [x.split('/')[1] for x in pinyin_hanzi]
            if not char_level:
                for i in range(len(hanzi)):
                    for n in range(n_gram):
                        if i < n:
                            break
                        cur_word = ''.join(hanzi[i - n : i + 1])
                        if cur_word not in word_count_dict:
                            word_count_dict[cur_word] = 1
                        else:
                            word_count_dict[cur_word] += 1
            else:
                pass
        json.dump(word_count_dict, out_file)

import json

INPUT_FILE = 'clean_content_hanzi_pinyin'
OUTPUT_FILE = 'word_counts.txt'


def count_words(n_gram=2, char_level=False):
    '''
    :param: n_gram: n-gram (2 for bigram, 3 for trigram, etc)
    :param char_level: True for character level counts, and False for word level
    :return: nothing, writes to file
    '''
    # dict format = {'1': {word:count, ...}, '2': {word:count, ...}, ...}
    word_count_dict_dict = {}
    for n in range(1, n_gram + 1):
        word_count_dict_dict[n] = {}
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
                        if cur_word not in word_count_dict_dict[n+1]:
                            word_count_dict_dict[n+1][cur_word] = 1
                        else:
                            word_count_dict_dict[n+1][cur_word] += 1
            else:
                pass
        json.dump(word_count_dict_dict, out_file)

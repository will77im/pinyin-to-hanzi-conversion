HMM_OUTPUT_FILE = 'data/hmmoutput.txt'
TEST_SET_FILE = 'data/testset.txt'


def correct_hmm_output(hmm_line, test_line, i):
    hmm_p_h = [l.split('/') for l in hmm_line.strip().split(' ')]
    out_p_h = [l.split('/') for l in test_line.strip().split(' ')]
    # print i
    for i in range(len(out_p_h)):
        while hmm_p_h[i][0] != out_p_h[i][0]:
            hmm_p_h[i] = [hmm_p_h[i][0] + hmm_p_h[i+1][0], hmm_p_h[i][1] + hmm_p_h[i+1][1]]
            del hmm_p_h[i+1]
    return hmm_p_h, out_p_h


def find_accuracy():
    total_words = 0
    total_sentences = 0
    correct_words = 0
    correct_sentences = 0
    with open(HMM_OUTPUT_FILE, 'r') as hmm_out_file, open(TEST_SET_FILE, 'r') as test_set_file:
        lines1 = hmm_out_file.read().splitlines()
        lines2 = test_set_file.read().splitlines()

        for i in range(len(lines1)):
            if len(lines1[i].strip()) == 0 or lines1[i].strip() == '-':
                continue

            pinyin_hanzi1, pinyin_hanzi2 = correct_hmm_output(lines1[i], lines2[i], i)
            hanzi1 = [l[1] for l in pinyin_hanzi1]
            hanzi2 = [l[1] for l in pinyin_hanzi2]
            sentence_incorrect = 0
            incorrect_words = 0
            for j in range(len(hanzi1)):
                total_words += 1
                if hanzi1[j] == hanzi2[j]:
                    correct_words += 1
                else:
                    incorrect_words += 1
            if incorrect_words <= 1:
                correct_sentences += 1
            total_sentences += 1
    word_accuracy = float(correct_words) / total_words
    sentence_accuracy = float(correct_sentences) / total_sentences
    print 'Word-Level Accuracy: ' + str(word_accuracy) + '\n'
    print 'Sentence-Level Accuracy: ' + str(sentence_accuracy) + '\n'

find_accuracy()

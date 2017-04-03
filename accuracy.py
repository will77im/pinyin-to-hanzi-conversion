HMM_OUTPUT_FILE = 'testset2.txt'
TEST_SET_FILE = 'testset.txt'

def find_accuracy():
    total_words = 0
    total_sentences = 0
    correct_words = 0
    correct_sentences = 0
    with open(HMM_OUTPUT_FILE, 'r') as hmm_out_file, open(TEST_SET_FILE, 'r') as test_set_file:
        lines1 = hmm_out_file.read().splitlines()
        lines2 = test_set_file.read().splitlines()
        for i in range(len(lines1)):
            if len(lines1[i].strip()) == 0:
                continue
            pinyin_hanzi1 = [l.split('/')[1] for l in lines1[i].strip().split(' ')]
            pinyin_hanzi2 = [l.split('/')[1] for l in lines2[i].strip().split(' ')]
            sentence_incorrect = False
            for j in range(len(pinyin_hanzi1)):
                total_words += 1
                if pinyin_hanzi1[j] == pinyin_hanzi2[j]:
                    correct_words += 1
                else:
                    sentence_incorrect = True
            if not sentence_incorrect:
                correct_sentences += 1
            total_sentences += 1
    word_accuracy = float(correct_words) / total_words
    sentence_accuracy = float(correct_sentences) / total_sentences
    print 'Word-Level Accuracy: ' + str(word_accuracy) + '\n'
    print 'Sentence-Level Accuracy: ' + str(sentence_accuracy) + '\n'

find_accuracy()

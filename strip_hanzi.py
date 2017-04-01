INPUT_FILE = 'testset.txt'
OUTPUT_FILE = 'testsetstripped.txt'

def strip_hanzi():
    with open(INPUT_FILE, 'r') as input_file, open(OUTPUT_FILE, 'w') as output_file:
        lines = input_file.read().splitlines()
        for line in lines:
            s = line.split(' ')
            pinyin = [x.split('/')[0] for x in s]
            pinyin = ' '.join(pinyin)
            output_file.write(pinyin + '\n')

strip_hanzi()

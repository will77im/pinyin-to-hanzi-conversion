def generate_dict():
    pinyin_hanzi = {}

    count = 0

    with open('data/trainset.txt') as input_file:
        for lines in input_file:
            items = lines.strip().split()
            for p_h in items:
                t = p_h.split('/')
                pinyin = t[0]
                hanzi = t[1]

                if pinyin not in pinyin_hanzi:
                    pinyin_hanzi[pinyin] = {}
                pinyin_hanzi[pinyin][hanzi] = pinyin_hanzi[pinyin].get(hanzi, 0) + 1

    with open('data/pinyin_hanzi.txt', 'w') as output_file:
        for pinyin in pinyin_hanzi:
            output_file.write(pinyin + '\t')
            count += len(pinyin_hanzi[pinyin])

            t = [w for w, y in sorted(pinyin_hanzi[pinyin].iteritems(), key=lambda x: x[1], reverse=True)]

            output_file.write(' '.join(t) + '\n')


if __name__ == "__main__":
    generate_dict()

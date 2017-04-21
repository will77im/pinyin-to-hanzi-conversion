#coding=utf-8
import string
inputDataFile = open('input.txt')
inputLines = inputDataFile.readlines()

inputCorpusFile = open('pinyin_hanzi.txt')
corpusDataLines = inputCorpusFile.readlines()


outputFile = open('output.txt', 'w')
existFlag=0

for inputLine in inputLines:
	inputLine = inputLine.strip()
	pinyinArray = inputLine.split(' ')
	for pinyin in pinyinArray:		
		
		for corpusDataLine in corpusDataLines:
			existFlag =0
			corpusDataLine  = corpusDataLine.strip()
			corpusPinyinHanziArray = corpusDataLine.split('	')
			if corpusPinyinHanziArray[0] ==pinyin:
				hanzi = corpusPinyinHanziArray[1].split(' ')
				outputFile.write(pinyin + '/' + hanzi[0] + ' ')
				existFlag =1
				break
		if existFlag==0 :
			outputFile.write(pinyin + '/NONE'  + ' ')
	outputFile.write('\n')

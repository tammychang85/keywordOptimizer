'''
Implementation of Rapid Automatic Keyword Extraction (RAKE) algorithm for Chinese
Original algorithm described in: Rose, S., Engel, D., Cramer, N., & Cowley, W. (2010).
Automatic Keyword Extraction from Individual Documents. In M. W. Berry & J. Kogan
(Eds.), Text Mining: Theory and Applications: John Wiley & Sons. 
'''
__author__ = "Ruoyang Xu"

import jieba
import jieba.posseg as pseg
import operator
import json
from collections import Counter


# Data structure for holding data
class Word():
    def __init__(self, char, freq = 0, deg = 0):
        self.freq = freq
        self.deg = deg
        self.char = char

    def returnScore(self):
        return self.deg/self.freq

    def updateOccur(self, phraseLength):
        self.freq += 1
        self.deg += phraseLength

    def getChar(self):
        return self.char

    def updateFreq(self):
        self.freq += 1

    def getFreq(self):
        return self.freq

# Check if contains num (and english?
def notNumStr(instr):
    for item in instr:
        if item.isdigit():
            return False
    return True

# Read Target Case if Json
def readSingleTestCases(testFile):
    with open(testFile) as json_data:
        try:
            testData = json.load(json_data)
        except:
            # This try block deals with incorrect json format that has ' instead of "
            data = json_data.read().replace("'",'"')
            try:
                testData = json.loads(data)
                # This try block deals with empty transcript file
            except:
                return ""
    returnString = ""
    for item in testData:
        try:
            returnString += item['text']
        except:
            returnString += item['statement']
    return returnString



def run(rawText, algo=0, mode=0):

    # position list for jieba(default)
    if algo == 0:
        # to exclude words with positon flags in the poSprty(default)
        if mode == 0:
            poSPrty = ['m','x','uj','ul','mq','u','v','f']
        # to choose words with positon flags in the poSprty
        else:
            poSPrty = poSPrty = ['n', 'nr', 'nrfg', 'nrt', 'ns', 'nt', 'nz', 'v', 'vn', 'eng']

    # position list for ckip
    else:
        # to exclude words with positon flags in the poSprty(default)
        if mode == 0:
            poSPrty = ['Ne','COMMACATEGORY', 'PERIODCATEGORY', 'QUESTIONCATEGORY', 'COLONCATEGORY', 'PARENTHESISCATEGORY', ' PAUSECATEGORY', 'Ta','Nf','T','V','Ng', 'WHITESPACE']
        # to choose words with positon flags in the poSprty
        else:
            poSPrty = ['Na', 'Nb', 'Nc', 'Nd','VA', 'VB', 'VC',
                        'CARDINA', 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 
                        'LOC', 'MONEY', 'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON',
                        'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']


    swLibList = [line.rstrip('\n') for line in open("data/stoplist/繁體中文停用詞表(1209個).txt",'r',encoding="utf-8")]# Construct Stopword Lib
    conjLibList = [line.rstrip('\n') for line in open("data/stoplist/簡轉繁中文分隔詞詞庫.txt",'r',encoding="utf-8")]# Construct Phrase Deliminator Lib
    rawtextList = rawText # using different libs

    # Construct List of Phrases and Preliminary textList
    textList = []# record candidate expressions
    listofSingleWord = dict()# record keywords & keyphares
    meaningfulCount = 0# record the total num of content words
    lastWord = ''# used for segmentation
    for eachWord, flag in rawtextList:
        eachWord = eachWord.strip()

        if algo == 0:# if use jieba
            flag = flag.lower()
            
        if mode == 0:
            if eachWord in conjLibList or not notNumStr(eachWord) or eachWord in swLibList or flag in poSPrty or eachWord == '\n' or len(eachWord) < 2 :
                if lastWord != '|':
                    textList.append("|")
                    lastWord = "|"
            elif eachWord not in swLibList and eachWord != '\n':
                textList.append(eachWord)
                meaningfulCount += 1
                if eachWord not in listofSingleWord:
                    listofSingleWord[eachWord] = Word(eachWord)#  create a Word object
                lastWord = ''
        else:
            if eachWord in conjLibList or not notNumStr(eachWord) or eachWord in swLibList or flag not in poSPrty or eachWord == '\n' or len(eachWord) < 2 :
                if lastWord != '|':
                    textList.append("|")
                    lastWord = "|"
            elif eachWord not in swLibList and eachWord != '\n':
                textList.append(eachWord)
                meaningfulCount += 1
                if eachWord not in listofSingleWord:
                    listofSingleWord[eachWord] = Word(eachWord)#  create a Word object
                lastWord = ''

    # Construct List of list that has phrases as wrds
    newList = []# record keyphares
    tempList = []
    for everyWord in textList:
        if everyWord != '|':
            tempList.append(everyWord)
        else:
            newList.append(tempList)
            tempList = []


    tempStr = ''
    for everyWord in textList:
        if everyWord != '|':
            tempStr += everyWord + '|'
        else:
            if tempStr[:-1] not in listofSingleWord:
                #print(tempStr)
                listofSingleWord[tempStr[:-1]] = Word(tempStr[:-1])
                tempStr = ''

    # Update the entire List
    for everyPhrase in newList:
        res = ''
        for everyWord in everyPhrase:
            listofSingleWord[everyWord].updateOccur(len(everyPhrase))
            res += everyWord + '|'
        phraseKey = res[:-1]
        if phraseKey not in listofSingleWord:
            listofSingleWord[phraseKey] = Word(phraseKey)
        else:
            listofSingleWord[phraseKey].updateFreq()

    # Get score for entire Set
    outputList = dict()
    for everyPhrase in newList:

        if len(everyPhrase) > 5:
            continue
        score = 0
        phraseString = ''
        outStr = ''
        for everyWord in everyPhrase:
            score += listofSingleWord[everyWord].returnScore()
            phraseString += everyWord + '|'
            outStr += everyWord
        phraseKey = phraseString[:-1]
        freq = listofSingleWord[phraseKey].getFreq()
        if freq / meaningfulCount < 0.01 and freq < 3 :
            continue
        outputList[outStr] = score

    sorted_list = sorted(outputList.items(), key = operator.itemgetter(1), reverse = True)
    return sorted_list[:10]
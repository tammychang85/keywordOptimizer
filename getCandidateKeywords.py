# -*- coding:utf-8 -*-

import MyRake
import MyCkip
import jieba # includes posseg in it
import jieba.analyse # used to extract with TF-IDF & TextRank


# to seperate words from positons
def seperate(keywordsList):
    output = []
    for word in keywordsList:
        output.append(word[0])
    return output


def useJiebaRake(articleText, mode=0):
    tcTokenizer = jieba.Tokenizer(dictionary='data/Dictionary/dict.txt.big')# Set traditonal chinese dic for new tokenizer
    tcPosseg = jieba.posseg.POSTokenizer(tokenizer=tcTokenizer)# create new tokenizer
    tcPosseg = jieba.posseg.POSTokenizer(tokenizer=tcTokenizer)# create new tokenizer
    output = seperate(MyRake.run(tcPosseg.cut(articleText), 0, mode))
    return output


def useJiebaTFIDF(articleText):
    jieba.analyse.set_stop_words('data/stoplist/traditionalChineseConjunctionList.txt')# set stop words list
    jieba.analyse.set_idf_path('data/Dictionary/idf.txt.big')# set IDF dicti
    output = jieba.analyse.extract_tags(articleText, topK=10, withWeight=False, allowPOS=())
    return output


def useJiebaTextRank(articleText):
    output = jieba.analyse.textrank(articleText, topK=10, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
    return output


def useCkipRake(articleText, mode):
    output = seperate(MyRake.run(MyCkip.getWSList(articleText), 1, mode))
    return output


def outputResults(keywordsList, fileName):
    with open(fileName, 'w', encoding='utf-8') as f:
        for eachKeyword in keywordsList:
            f.write(eachKeyword + ' ')


def run(method, textPath):

    # record the texts where keywords need to be extract from
    articleText = []
    # save as the formatt that jieba requires
    with open(textPath,'r',encoding="utf-8") as f:
        articleText.append(f.read())
    # save as the formatt that ckip requires
    with open(textPath,'r',encoding="utf-8") as f:
        articleText.append(f.readlines())

    # restore the extracted keywords
    keywords = []

    # name of the result txt file
    fileName = ''

    # choosing method
    # 0:jiebaRake1, 1:jiebaRake2, 2:jibaTFIDF, 3:jiebaTexkRake, 4:ckipRake, 5:ckipRake2, 6:use all
    # difference between jiebaRake1 and jiebaRake2: the rule of choosing words
    # the former excludes words with some specific positon flags, while the latter chooses words with some specific positon flags
    if method == 0:
        keywords = useJiebaRake(articleText[0], 0)
        fileName = 'keywords/jiebaRake1.txt'

    elif method == 1:
        keywords = useJiebaRake(articleText[0], 1)
        fileName = 'keywords/jiebaRake2.txt'

    elif method == 2:
        keywords = useJiebaTFIDF(articleText[0])
        fileName = 'keywords/jiebaTFIDF.txt'

    elif method == 3:
        keywords = useJiebaTextRank(articleText[0])
        fileName = 'keywords/jiebaTexkRake.txt'

    elif method == 4:
        keywords = useCkipRake(articleText[1], 0)
        fileName = 'keywords/ckipRake.txt'

    elif method == 5:
        keywords = useCkipRake(articleText[1], 1)
        fileName = 'keywords/ckipRake2.txt'

    else:
        # ---extract with jieba---
        # using Rake(to extract by excluding words with positon flags in the poSprty)
        jiebaRake = useJiebaRake(articleText[0], 0)

        # using Rake(to extract by choosing words with positon flags in the poSprty)
        jiebaRake2 = useJiebaRake(articleText[0], 1)

        # using TFIDF
        jiebaTFIDF = useJiebaTFIDF(articleText[0])

        # using textRank
        jiebaTextRank = useJiebaTextRank(articleText[0])

        #---extract with ckip---
        # using Rake(to extract by excluding words with positon flags in the poSprty)
        ckipRake = useCkipRake(articleText[1], 0)

        # using Rake(to extract by choosing words with positon flags in the poSprty)
        ckipRake2 = useCkipRake(articleText[1], 1)

        # using TFIDF(to be added)

        # results
        temp = jiebaRake + jiebaRake2 + jiebaTFIDF + jiebaTextRank + ckipRake + ckipRake2

        # filter those duplicated keywords
        for eachKeyword in temp:
            if eachKeyword not in keywords:
                keywords.append(eachKeyword)

        fileName = 'keywords/All.txt'


    # write the output txt file
    outputResults(keywords, fileName)
    print(fileName, 'done')


if __name__ == '__main__':
    method = int(input('choose a method '))
    textPath = input('enter a text path')
    run(method, textPath)

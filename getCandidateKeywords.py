import MyRake
import MyCkip
import MyTFIDF
import jieba # includes posseg in it
import jieba.analyse # used to extract with TF-IDF & TextRank


# to seperate words from positons
def seperate(keywordsList):
    output = []
    for word in keywordsList:
        output.append(word[0])
    return output


def useJiebaRake(targetText, mode=0):
    tcTokenizer = jieba.Tokenizer(dictionary='data/Dictionary/dict.txt.big')# Set traditonal chinese dic for new tokenizer
    tcPosseg = jieba.posseg.POSTokenizer(tokenizer=tcTokenizer)# create new tokenizer
    tcPosseg = jieba.posseg.POSTokenizer(tokenizer=tcTokenizer)# create new tokenizer
    output = seperate(MyRake.run(tcPosseg.cut(targetText), 0, mode))
    return output


def useJiebaTFIDF(targetText):
    jieba.analyse.set_stop_words('data/stoplist/簡轉繁中文分隔詞詞庫.txt')# set stop words list
    jieba.analyse.set_idf_path('data/Dictionary/idf.txt.big')# set IDF dicti
    output = jieba.analyse.extract_tags(targetText, topK=10, withWeight=False, allowPOS=())
    return output


def useJiebaTextRank(targetText):
    output = jieba.analyse.textrank(targetText, topK=10, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
    return output

def useCkipRake(targetText, mode):
    output = seperate(MyRake.run(MyCkip.getWSList(targetText), 1, mode))
    return output


def useCkipTfIDF(targetText):
    pass


def outputResults(keywordsList, fileName):
    with open(fileName, 'w', encoding='utf-8') as f:
        for eachKeyword in keywordsList:
            f.write(eachKeyword + ' ')


def run(method):

    targetText = []
    with open('data/testCase/Google評論.txt','r',encoding="utf-8") as f:
        targetText.append(f.read())
    with open('data/testCase/Google評論.txt','r',encoding="utf-8") as f:
        targetText.append(f.readlines())

    keywords = []
    fileName = '' # name of the result txt file

    # choosing method
    # 0:jiebaRake1, 1:jiebaRake2, 2:jibaTFIDF, 3:jiebaTexkRake, 4:ckipRake, 5:ckipRake2, 6:ckipTFIDF, 7:use all
    if method == 0:
        keywords = useJiebaRake(targetText[0], 0)
        fileName = 'keywords/jiebaRake1.txt'
    
    elif method == 1:
        keywords = useJiebaRake(targetText[0], 1)
        fileName = 'keywords/jiebaRake2.txt'
    
    elif method == 2:
        keywords = useJiebaTFIDF(targetText[0])
        fileName = 'keywords/jiebaTFIDF.txt'
    
    elif method == 3:
        keywords = useJiebaTextRank(targetText[0])
        fileName = 'keywords/jiebaTexkRake.txt'
    
    elif method == 4:
        keywords = useCkipRake(targetText[1], 0)
        fileName = 'keywords/ckipRake.txt'
    
    elif method == 5:
        keywords = useCkipRake(targetText[1], 1)
        fileName = 'keywords/ckipRake2.txt'
    
    elif method == 6:
        # to be added
        pass
    
    else:
        resultList = []
        # ---extract with jieba---
        # using Rake(to extract by excluding words with positon flags in the poSprty)
        jiebaRake = useJiebaRake(targetText[0], 0)
        
        # using Rake(to extract by choosing words with positon flags in the poSprty)
        jiebaRake2 = useJiebaRake(targetText[0], 1)
        
        # using TFIDF
        jiebaTFIDF = useJiebaTFIDF(targetText[0])
        
        # using textRank
        jiebaTextRank = useJiebaTextRank(targetText[0])

        #---extract with ckip---
        # using Rake(to extract by excluding words with positon flags in the poSprty)
        ckipRake = useCkipRake(targetText[1], 0)
        
        # using Rake(to extract by choosing words with positon flags in the poSprty)
        ckipRake2 = useCkipRake(targetText[1], 1)

        # using TFIDF(to be added)

        # results
        keywords = jiebaRake + jiebaRake2 + jiebaTFIDF + jiebaTextRank + ckipRake + ckipRake2
        fileName = 'keywords/All.txt'

    # outout the results
    outputResults(keywords, fileName)
    print(fileName, 'done')

if __name__ == '__main__':
    method = int(input('choose a method： '))
    #targetText = 
    run(method)
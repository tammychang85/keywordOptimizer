from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# process keyword list form ckip for the use of TFIDF
def prepareText(ckipWordList):

    TextString = ' '# record keywords only & make them into a string
    # seperate words and positons
    for word in ckipWordList:
        if word[0] != '\n':
            TextString += word[0] + ' '
    TextString.rstrip(' ')

    return TextString


# extract keywords using TF-IDF
def run(TFIDFList):

    vectorizer=CountVectorizer()# count term frequency
    transformer=TfidfTransformer()# calaulta TF-IDF score

    # strat extracting
    tfidf=transformer.fit_transform(vectorizer.fit_transform(TFIDFList))
    keywords=vectorizer.get_feature_names()
    weights=tfidf.toarray()

    # combine keywords and weights
    keywordList = []
    for i, eachWeight in enumerate(weights):
        temp = []
        for j, eachKeyword in enumerate(keywords):
            temp.append((eachKeyword, weights[i][j]))
        keywordList.append(temp)

    # choose top10 keywords
    sortedList = []
    outputList = []

    # sort keywords by weights
    for eachList in keywordList:
        sortedList.append(sorted(eachList, key=lambda x:x[1], reverse=True)[0:10])
    
    # record keywords only
    for eachList in sortedList:
        temp = []
        for eachWord in eachList:
            temp.append(eachWord[0])
        outputList.append(temp)

    return outputList
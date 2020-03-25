# -*- coding: utf-8 -*-
import _locale
import generateKeywordIdeas as getkeywords
import estimateKeywordTraffic as getTraffics

_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])


# set default strategy parameters
def getDefaultStrategy():
    maxPopulation = 10  # maximum of keyword population
    minImprovement = 0.01  # minimum improvement rate of keywords acceptable between two iterations
    maxIteration = 10  # how many rouds of optimization shoud be taken
    parentNum = 3  # num of keywords used to find alternatives
    return maxPopulation, maxIteration, minImprovement, parentNum


# get seedKeywords depends on the keywordSources and seedmode
# seedmode 0 :use keywords, keywordSources is the path of a txt file (default)
# seedmode 1: use url, keywordSources is the url of the target web page
# return a string list of keywords
def generateSeed(keywordSources, customerID, seedMode=0):
    seedKeywords = []
    if seedMode == 0:
        temp = []
        with open(keywordSources, 'r', encoding="utf-8") as f:
            temp = f.read().strip().split(' ')

        # remove duplicate keywords
        for keyword in temp:
            if keyword not in seedKeywords:
                seedKeywords.append(keyword)

    else:
        seedKeywords = getkeywords.run(customerID, keywordSources, seedMode=1)  # call google api
    return seedKeywords


# estimate traffic for keywords
# return a list of keywords with traffic estimations depends on the scoreMode
# seedMode 0: get click through rate; 1:get daily click; 2:get daily impression
# seedMode 3: get both daily click and impression
def estimateTraffic(keywords, scoreMode):
    keywordRequests = []
    for eachKeyword in keywords:
        keywordRequests.append({'text': eachKeyword, 'matchType':'EXACT'})

    estimations = getTraffics.run(keywordRequests, scoreMode)  # call google api
    return estimations


# calculate scores for keywords by traffic estimations
# return a sorted list of keywords with their scores
def calaulateScore(keywordEstimations, scoreMode):
    scoreList = []
    if scoreMode == 0:
        for eachEstimation in keywordEstimations:
            scoreList.append({'text': eachEstimation['text'], 'score': eachEstimation['clickThroughRate']})
    elif scoreMode == 1:
        for eachEstimation in keywordEstimations:
            scoreList.append({'text': eachEstimation['text'], 'score': eachEstimation['click']})
    elif scoreMode == 2:
        for eachEstimation in keywordEstimations:
            scoreList.append({'text': eachEstimation['text'], 'score': eachEstimation['impression']})
    else:
        for eachEstimation in keywordEstimations:
            scoreList.append({'text': eachEstimation['text'], 'score': eachEstimation['click'] + eachEstimation['impression']})

    scoreList.sort(key=lambda x:x['score'], reverse=True)
    return scoreList


# find alternaltive keywords similar to parentKeywords
# return a string list of keywords
def findAlternatives(customerID, currentPopulation, parentNum):
    # parentKeywords = [keyword[0] for keyword in currentPopulation[0:parentNum]]
    parentKeywords = []
    for eachKeyword in currentPopulation:
        parentKeywords.append(eachKeyword['text'])
    alternatives = getkeywords.run(customerID, parentKeywords)  # call google api
    return alternatives


# get keywords that could find in article
def filterKeywords(articleKeywords, alternativePopulation, articleText):
    for eachKeyword in alternativePopulation:
        if eachKeyword['text'] in articleText and eachKeyword not in articleKeywords:
            articleKeywords.append(eachKeyword)
    return articleKeywords


# combine alternativePopulation and currentPopulation, remove the worst ones to fit the maxPopulaton(if need)
# return the nextPopulaion and improvement of the iteration
def evaluate(currentPopulation, alternativePopulation, maxPopulation):

    temp1 = currentPopulation + alternativePopulation
    temp1.sort(key=lambda x:x['score'], reverse=True)
    temp2 = []
    # remove duplicate keywords
    for keyword in temp1:
        if keyword not in temp2:
            temp2.append(keyword)

    # trim the population to fit maxPopulation
    nextPopulation = []
    if len(temp2) > maxPopulation:
        nextPopulation = temp2[0:maxPopulation]
    else:
        nextPopulation = temp2

    currentScore = sum(keyword['score'] for keyword in currentPopulation) / len(currentPopulation)  # average scores of the currentPopulation
    nextScore = sum(keyword['score'] for keyword in nextPopulation) / len(nextPopulation)  # average scors of the nexttPopulation

    iterationImprovement = (nextScore - currentScore) / currentScore  # improvement rate of this iteration
    return nextPopulation , iterationImprovement


# coordinate all the funtions above during the process of optimization
def optimize(customerID, keywordSources, articleText, strategies=None, seedMode=0, scoreMode=1):
    # initialize strategy parameters for optimization
    if strategies == None:
        # default strategies
        maxPopulation, maxIteration, minImprovement, parentNum = getDefaultStrategy()
    else:
        # manual strategies
        maxPopulation, maxIteration, minImprovement, parentNum = strategies
    currentIterarion = 0
    currentImprovement = float('inf')

    # optimization starts
    seedKeywords = generateSeed(keywordSources, customerID, seedMode)  # get a string list of keywords
    articleText = seedKeywords.copy()  # keywords that exist in article
    estimations = estimateTraffic(seedKeywords, scoreMode)  # get traffic estimations of seedKeywords
    currentPopulation = calaulateScore(estimations, scoreMode)  # get a sorted list of keywords with socres
    articleKeywords = currentPopulation.copy() # keywords that could find in the original article

    while currentIterarion < maxIteration and currentImprovement >= minImprovement:
        alternatives = findAlternatives(customerID, currentPopulation, parentNum)
        alternativePopulation = calaulateScore(estimateTraffic(alternatives, scoreMode), scoreMode)
        articleKeywords = filterKeywords(articleKeywords, alternativePopulation, articleText)
        currentPopulation, currentImprovement = evaluate(currentPopulation, alternativePopulation, maxPopulation)
        currentIterarion += 1

    # seperate keywords from their scores
    keywords = []
    for result in currentPopulation:
        keywords.append(result['text'])

    # retrive monthly searches value competition value for keywords
    recommendedKeywords = getkeywords.run(customerID, keywords, moreInfo=1)[0:len(keywords)]

    print('currentIterarion:', currentIterarion, 'currentImprovement:', currentImprovement)
    print('recommendedKeywords:', recommendedKeywords)
    print('articleKeywords:', articleKeywords)

    return recommendedKeywords, articleKeywords


if __name__ == '__main__':
    articleText = []
    with open('data/testCase/Google評論.txt', 'r', encoding="utf-8") as f:
        articleText = f.read()

    customerID = '3566761997'
    keywordSources = 'keywords/jiebaTFIDF.txt'
    optimize(customerID, keywordSources, articleText)

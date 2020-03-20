# -*- coding: utf-8 -*-
import locale
import sys
import _locale
import generateKeywordIdeas as getkeywords
import estimateKeywordTraffic as getTraffics


_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])


# set default strategy parameters
def setStrategy():
    maxPopulation = 10 # maximum of keyword population
    minImprovement = 0.01 # minimum improvement rate of keywords acceptable between two iterations
    maxIteration = 10 # how many rouds of optimization shoud be taken
    parentNum = 3 # num of keywords used to find alternatives
    return maxPopulation, maxIteration, minImprovement, parentNum


# get seedKeywords depends on the keywordSources and mode
# mode 0 :use keywords, keywordSources is the path of a txt file (default)
# mode 1: use url, keywordSources is the url of the target web page
# return a string list of keywords
def generateSeed(keywordSources, customerID, mode=0):
    seedKeywords = []
    if mode == 0:
        temp = []
        with open(keywordSources,'r', encoding="utf-8") as f:
            temp = f.read().strip().split(' ')

        # remove duplicate keywords
        for keyword in temp:
            if keyword not in seedKeywords:
                seedKeywords.append(keyword)

    else:
        seedKeywords = getkeywords.run(customerID, keywordSources, mode=1) # call google api
    return seedKeywords


# estimate traffic for keywords
# return a list of keywords with their traffic estimations
def estimateTraffic(keywords):
    keywordRequests = []
    for eachKeyword in keywords:
        keywordRequests.append({'text': eachKeyword, 'matchType':'EXACT'})

    estimations = getTraffics.run(keywordRequests)# call google api
    return estimations


# calculate scores for keywords by traffic estimations
# return a sorted list of keywords with their scores
def calaulateScore(keywordEstimations):
    scoreList = []
    for eachEstimation in keywordEstimations:
        scoreList.append({'text': eachEstimation['text'], 'score': eachEstimation['click'] + eachEstimation['impression']})

    scoreList.sort(key=lambda x:x['score'], reverse=True)
    return scoreList


# find alternaltive keywords similar to parentKeywords
# return a string list of keywords
def findAlternatives(customerID, currentPopulation, parentNum):
    #parentKeywords = [keyword[0] for keyword in currentPopulation[0:parentNum]]
    parentKeywords = []
    for eachKeyword in currentPopulation:
        parentKeywords.append(eachKeyword['text'])
    alternatives = getkeywords.run(customerID, parentKeywords)# call google api
    return alternatives


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


    currentScore = sum(keyword['score'] for keyword in currentPopulation) / len(currentPopulation) # average scores of the currentPopulation
    nextScore = sum(keyword['score'] for keyword in nextPopulation) / len(nextPopulation) # average scors of the nexttPopulation

    iterationImprovement = (nextScore - currentScore) / currentScore # improvement rate of this iteration
    return nextPopulation , iterationImprovement


# coordinate all the funtions above during the process of optimization
def optimize(customerID, keywordSources, strategies=None, mode=0):
    # initialize strategy parameters for optimization
    if strategies == None:
        # default strategies
        maxPopulation, maxIteration, minImprovement, parentNum = setStrategy()
    else:
        # manual strategies
        maxPopulation, maxIteration, minImprovement, parentNum = strategies
    currentIterarion = 0
    currentImprovement = float('inf')

    # optimization starts
    seedKeywords = generateSeed(keywordSources, customerID, mode) # get a string list of keywords
    estimations = estimateTraffic(seedKeywords) # get traffic estimations of seedKeywords
    currentPopulation = calaulateScore(estimations) # get a sorted list of keywords with socres

    while currentIterarion < maxIteration and currentImprovement >= minImprovement:
        alternatives = findAlternatives(customerID, currentPopulation, parentNum)
        alternativePopulation = calaulateScore(estimateTraffic(alternatives))
        currentPopulation, currentImprovement = evaluate(currentPopulation, alternativePopulation, maxPopulation)
        currentIterarion += 1

    # seperate keywords from their scores
    keywords = []
    for result in currentPopulation:
        keywords.append(result['text'])

    # retrive monthly searches value competition value for keywords
    outputs = getkeywords.run(customerID, keywords, moreInfo=1)[0:len(keywords)]
    
    print('currentIterarion:', currentIterarion, 'currentImprovement:', currentImprovement)
    print('results:', outputs)

    return outputs

if __name__ == '__main__':
    optimize(customerID, keywordSources, strategies=None, mode=0)


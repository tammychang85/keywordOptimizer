import generateKeywordIdeas as getkeywords
import estimateKeywordTraffic as getTraffics


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
        with open(keywordSources,'r',encoding="utf-8") as f:
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
    scoreLIst = []
    for eachEstimation in keywordEstimations:
        scoreLIst.append([eachEstimation[0], sum(eachEstimation[1])])
    scoreLIst.sort(key=lambda x:x[1], reverse = True)
    return scoreLIst


# find alternaltive keywords similar to parentKeywords
# return a string list of keywords
def findAlternatives(customerID, currentPopulation, parentNum):
    parentKeywords = [keyword[0] for keyword in currentPopulation[0:parentNum]]
    alternatives = getkeywords.run(customerID, parentKeywords)# call google api
    return alternatives


# combine alternativePopulation and currentPopulation, remove the worst ones to fit the maxPopulaton(if needed)
# return the nextPopulaion and improvement of the iteration
def evaluate(currentPopulation, alternativePopulation, maxPopulation):
    temp = currentPopulation + alternativePopulation
    temp.sort(key=lambda x:x[1], reverse = True)
    nextPopulation = []
    
    if len(temp) > maxPopulation:
        nextPopulation = temp[0:maxPopulation]
    else:
        nextPopulation = temp

    currentScore = sum(score[1] for score in currentPopulation) # total scores of the currentPopulation
    nextScore = sum(score[1] for score in nextPopulation) # total scors of the nexttPopulation
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
    cruuentIterarion = 0
    currentImprovement = float('inf')

    # optimization starts
    seedKeywords = generateSeed(keywordSources, customerID, mode) # get a string list of keywords
    Estimations = estimateTraffic(seedKeywords) # get traffic estimations of seedKeywords
    currentPopulation = calaulateScore(Estimations) # get a sorted list of keywords with socres

    while cruuentIterarion < maxIteration and currentImprovement >= minImprovement:
        alternatives = findAlternatives(customerID, currentPopulation, parentNum)
        alternativePopulation = calaulateScore(estimateTraffic(alternatives))
        currentPopulation, currentImprovement = evaluate(currentPopulation, alternativePopulation, maxPopulation)
        cruuentIterarion += 1

    # seperate keywords from their scores
    outputs = []
    for result in currentPopulation:
        outputs.append(result[0])
    
    print('cruuentIterarion:', cruuentIterarion, 'currentImprovement:', currentImprovement)
    print('results:', outputs)

    return outputs

if __name__ == '__main__':
    optimize(customerID, keywordSources, strategies=None, mode=0)


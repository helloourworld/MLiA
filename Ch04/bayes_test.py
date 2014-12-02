#coding=utf-8
#__author__ = 'yulj'
from numpy import *
import numpy as np
def loadDataSet():
    postingList=[['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                 ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                 ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                 ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                 ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                 ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
    classVec = [0,1,0,1,0,1]    #1 is abusive, 0 not
    return postingList,classVec

def createVocabList(dataSet):
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)
    return list(vocabSet)

def setOfWords2Vec(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1 #tag 1
        else:
            print "the word: %s is not in my Vocabulary!" % word
    return returnVec

list0Posts, listClasses = loadDataSet()
myVocabList = createVocabList(list0Posts)
print myVocabList
print setOfWords2Vec(myVocabList, list0Posts[0])
print setOfWords2Vec(myVocabList, list0Posts[3])

#朴素贝叶斯分类器训练函数
'''
文档矩阵trainMatrix, 每篇文档类别标签构成的向量trainCategory
1st, 计算文档属于侮辱性文档（class=1）的概率 P(1) ; P(0) = 1 - P(1)
对于多分类，代码修改
'''
def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory)/ float(numTrainDocs)
    p0Num = ones(numWords); p1Num = ones(numWords)      #change to ones()
    p0Denom = 2.0; p1Denom = 2.0                        #change to 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = np.log(p1Num/p1Denom)          #change to log()
    p0Vect = np.log(p0Num/p0Denom)          #change to log()
    return p0Vect,p1Vect,pAbusive

trainMat = []
for postinDoc in list0Posts:
    trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
numTrainDocs = len(trainMat)
numWords=len(trainMat[0])
pAbusive = sum(listClasses)/float(numTrainDocs)
print pAbusive
p0Num = ones(numWords);p1Num=ones(numWords)
p0Denom = 2.0;p1Denom = 2.0
for i,each in enumerate(trainMat):
    if listClasses[i] == 1:
        p1Num += each
        p1Denom += sum(each)
        print '*1*',p1Num,p1Denom
    else:
        p0Num += each
        p0Denom += sum(each)
        print '*0*',p0Num,p0Denom,sum(p0Num)
p1Vect = np.log(p1Num / p1Denom)
p0Vect = np.log(p0Num / p0Denom)
print p0Vect
print p1Vect
print max(p1Vect)
print myVocabList[argmax(p1Vect)]
'''
p0V, p1V,pAb = trainNB0(trainMat,listClasses)
print pAb
print p0V
print p1V
'''

def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    p1 = sum(vec2Classify * p1Vec) + log(pClass1)    #element-wise mult
    p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else:
        return 0

#def testingNB():
try:
    listOPosts,listClasses = loadDataSet()
    myVocabList = createVocabList(listOPosts)
    trainMat=[]
    for postinDoc in listOPosts:
        trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
    p0V,p1V,pAb = trainNB0(array(trainMat),array(listClasses))
    testEntry = ['love', 'my', 'dalmation']
    thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
    print thisDoc
    print sum(thisDoc*p1V)+log(0.5)
    print sum(thisDoc*p0V)+log(0.5)
    print testEntry,'classified as: ',classifyNB(thisDoc,p0V,p1V,pAb)
    testEntry = ['stupid', 'garbage']
    thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
    print testEntry,'classified as: ',classifyNB(thisDoc,p0V,p1V,pAb)
except:
    pass
#testingNB()
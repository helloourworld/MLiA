#coding=utf-8
#Apriori 辅助函数
__author__ = 'Administrator'
def loadDataSet():
    return [[1, 3, 4], [2, 3, 5], [1, 2, 3 , 5], [2, 5]]

def createC1(dataSet):
    C1 = []
    for transaction in dataSet:
        for item in transaction:
            if not [item] in C1:
                C1.append([item])
    C1.sort()
    return map(frozenset, C1) #map(None,c)

dataSet = loadDataSet()
C1 = createC1(dataSet)
print 'dataSet is :', dataSet
print '单项集is:', C1

def scanD(D, Ck, minSupport):
    ssCnt = {} # 单项集频数统计
    for tid in D:
        for can in Ck:
            if can.issubset(tid):
                if not ssCnt.has_key(can):ssCnt[can] = 1
                else:ssCnt[can] += 1
    numItems = float(len(D)) # total 频数
    retList = []
    supportData = {}
    for key in ssCnt:
        support = ssCnt[key] / numItems
        if support >= minSupport:
            retList.insert(0, key)
        supportData[key] = support
    return retList, supportData

L1, suppData0 = scanD(dataSet, C1, 0.5)
print '满足最小支持度的项集', L1
print suppData0

def aprioriGen(Lk, k): # creates Ck
    retList = []
    lenLk = len(Lk)
    for i in range(lenLk):
        for j in range(i+1, lenLk):
            L1 = list(Lk[i])[:k-2]; L2=list(Lk[j])[:k-2]  #前k-2个项相同时，将两个集合合并

            L1.sort();L2.sort()
            if L1 == L2:
                retList.append(Lk[i] | Lk[j])
    return retList

def apriori(dataSet, minSupport = 0.5):
    C1 = createC1(dataSet)
    D = map(set, dataSet)
    L1, supportData = scanD(D, C1, minSupport)
    L = [L1]
    k = 2
    while (len(L[k-2]) > 0):
        Ck = aprioriGen(L[k-2],k)
        Lk, supK = scanD(D,Ck,minSupport) # 扫描数据集，从Ck得到Lk
        supportData.update(supK)
        L.append(Lk)
        k += 1
    return L, supportData

L, suppData = apriori(dataSet)
print L
print L[0]
print L[1]
print L[2]

print aprioriGen(L[0],2)



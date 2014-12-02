#coding=utf-8

fr = open(r"F:\MLiA\ciku\ELECTRIC.txt")
for each in fr.readlines():
    print len(each.strip())
    if len(each) is 0:
        print "lll"
#coding=utf-8
#__author__ = 'yulj'
import urllib2
import datetime
import json
'''
通过DOM分析找到数据存储页面/pinggu/ajax/chartajax.aspx?dataType=4&city=%u5317%u4EAC&Class=defaultnew&year=1
通过替换city year参数进行不同城市不同年份数据的获取
格式如：
... [1409500800000,37248],[1412092800000,37401]]&[[1275321600000,22729]...
& 符号前为二手房价数据；& 符号后为新房房价数据
二者数据量不同，新房数据只的53期
其中数据日期转换使用datetime.datetime.fromtimestamp()____由王昊提出。
'''
#price_ajax = 'http://fangjia.fang.com/pinggu/ajax/chartajax.aspx?dataType=4&city=%u5317%u4EAC&Class=defaultnew&year=1'
price_ajax= 'file:///C:/Users/yulj/Desktop/chartajax.aspx.html'
data = urllib2.urlopen(price_ajax).read().split('&')
ershou = json.loads(data[0]); new = json.loads(data[1])
#print len(ershou); print len(new)
fw = open('price_bj.txt','w')
fw.write("二手房房价数据：\n")
for each in ershou:
    fw.write(datetime.datetime.fromtimestamp(each[0]/1000).strftime("%Y年%m月")+'\t'+str(each[1])+'\n')
fw.write("新房房价数据：\n")
for each in new:
    fw.write(datetime.datetime.fromtimestamp(each[0]/1000).strftime("%Y年%m月")+'\t'+str(each[1])+'\n')
fw.close()
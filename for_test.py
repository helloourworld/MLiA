#coding=utf-8
#__author__ = 'yulj'
from numpy import *
import numpy as np
from nltk.probability import FreqDist, DictionaryProbDist, ELEProbDist, sum_logs
import MySQLdb
import sys, os, re, string
reload(sys)
sys.setdefaultencoding('utf8')
conn = MySQLdb.connect(host='localhost', user = 'root', passwd = 'sas123', db = 'test')
cursor = conn.cursor()
#mysql = 'create table if not exists comment_test(comment varchar(128), class char)'
def del_data(data_del):
    try:
        mysql = 'drop table %s' % data_del
        cursor.execute(mysql)
        all = cursor.fetchall()
        if all:
            for ea in all:
                print ea
    except Exception, e:
        print e
    cursor.close()
del_data('jc_comment2_cutT')
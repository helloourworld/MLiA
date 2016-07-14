#coding=utf-8
#__author__ = 'yulj'
import operator
import jieba
import MySQLdb
import sys, os, re, string, time
import nltk
reload(sys)
sys.setdefaultencoding('utf-8')
import codecs
import numpy as np
#define 词库2Vec
#'F:\MLiA\ciku'
ciku = 'F:/MLiA/ciku/'
drop_string = ['有限公司','公司','股份有限公司','分公司','总公司','有限责任公司','集团','商业有限公司']
def loadVec_all():
    trainingFileList = os.listdir(ciku)
    m = len(trainingFileList)
    Vec_dict = {}
    for i in range(m):
        fileNameStr = trainingFileList[i]
        vec_class = fileNameStr.split('.')[0].upper()
        Vec_dict[vec_class] = loadVec(trainingFileList[i])
    return Vec_dict

def nodup(seq, idfun = None):
    if idfun is None:
        def idfun(x): return x
    seen={};result=[]
    for item in seq:
        marker = idfun(item)
        if item in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
def loadVec(file):
    fr = codecs.open(ciku+file,'rU')
    #read Class Vector
    Vec=[]
    for each in  fr.readlines():
        vc = each.strip()
        if len(vc) > 0:Vec.append(vc)
    fr.close()
    #nodup
    Vec = nodup(Vec)
    return Vec
def primary_class():
    postingList=[['汽车'],
                 ['商场'],
                 ['超市'],
                 ['母婴'],
                 ['餐饮'],
                 ['服装'],
                 ['酒店'],
                 ['旅游'],
                 ['医药'],
                 ['化妆品'],
                 ['BANK']]
    classVec = ['CAR','MALL','MARKET','MATERNAL','CATERING','CLOTHING','HOTEL','TOUR','MEDICINE','COSMETIC','BANKING']    #1-汽车 2-商场 3-超市 4-母婴用品 0-other ..
    return postingList,classVec
# 输入 词库loadDataSet for postingList, classVec
def loadDataSet():
    postingList,classVec = primary_class()
    Vec_dict = loadVec_all()
    for key in Vec_dict:
        if key in classVec:
            postingList[classVec.index(key.upper())] = Vec_dict[key]
        else:
            classVec.append(key)
            postingList.append(Vec_dict[key])
    return postingList,classVec

# 分类 return classify dist
def prob_classify(featureset, MCCstr):
        # Discard any feature names that we've never seen before.
        # Otherwise, we'll just assign a probability of 0 to
        # everything. [红旗洗车连锁超市 【汽车 超市】 超市]

        for i, class_label in enumerate(classVec):
            #print class_label,len(postingList[i])
            pass
        # Find the log probabilty of each label, given the features.
        # Start with the log probability of the label itself.
        logprob = {}; ciku_list = []
        if type(featureset) is list :
            for fname in featureset:
                for i in range(len(classVec)):
                    if fname in postingList[i]:
                        logprob[classVec[i]] = logprob.get(classVec[i], 0) + 1
                        ciku_list.append(fname)
        else:
            for i in range(len(classVec)):
                for each_ciku in postingList[i]:
                    if each_ciku in featureset:
                        logprob[classVec[i]] = logprob.get(classVec[i], 0) + 1
                        ciku_list.append(each_ciku)
                        #print featureset, ':', each_ciku
        for key in MCC_dict:
                if MCCstr in MCC_dict[key]:
                    logprob[key] = logprob.get(key, 0) + 3 # 增加原分类权重
        if not logprob:
                    logprob['Uk'] = 1
                    #print featureset, 'is not in any Class'
        return logprob, ciku_list

def customer_classify(class_set):
    postingList,classVec = loadDataSet()
    customer_class = {}
    for each_class in class_set:
        for i in range(len(classVec)):
            if each_class in classVec:
                customer_class[classVec[i]] = customer_class.get(classVec[i], 0) + 1
    if not each_class:
                    each_class['Unknown'] = 1
    return customer_class

# 输出 return分类
def classify(featureset,mccstr):
        res, ciku_list = prob_classify(featureset,mccstr)
        ciku_list2str = ','.join(each for each in ciku_list)
        sortedClass = sorted(res.iteritems(), key=operator.itemgetter(1), reverse=True)
        sorted_class_str=''
        if len(sortedClass) > 1:
            if sortedClass[0][1] == sortedClass[1][1]:
                sorted_class_str = ','.join(each[0] for each in sortedClass)
        else:
            sorted_class_str = ''
        return sortedClass[0][0], ciku_list2str, sorted_class_str

# 进行featureset 切分
def cut_featureset(data_in):
    porter = nltk.PorterStemmer()
    for each in drop_string:
        data_in = data_in.rstrip(each)
    featureset = [porter.stem(each.upper().encode('utf-8')) for each in jieba.cut(data_in, cut_all = True)] #由于词库全改为大写
    delCStr ='《》（）&%￥#@！｛｝【】 '
    delEStr = string.punctuation + ' ' + string.digits + delCStr #ASCII 标点符号，空格和数字
    featureset = featureset[:]
    for each in featureset:

        if each in delEStr:
            featureset.remove(each)
    return featureset

# 创建词库表
def ciku_database(ciku_data):
    try:
        postingList, classVec = loadDataSet()
        conn = MySQLdb.connect(host='localhost',user='root',passwd = 'sas123', db = 'bank1', autocommit=True)
        cursor = conn.cursor()
        mysql = 'drop table %s' %ciku_data
        cursor.execute(mysql)
        mysql = 'create table if not exists %s (token varchar(128), ListClasses varchar(8))' % ciku_data
        cursor.execute(mysql)
        sql = "insert into %s" % ciku_data + "(token, ListClasses) values (%s, %s)"
        val_temp = zip(postingList, classVec)
        ciku_list = []
        for ciku_lists in val_temp:
            for token_temp in ciku_lists[0]:
                ciku_list.append([token_temp.encode('gbk'), ciku_lists[-1]])
        try:
            cursor.executemany(sql, ciku_list)
        except Exception, e:
            print e
    except Exception, e:
        print e

def loadDataSet_from_db(ciku_data):
    try:
        conn = MySQLdb.connect(host='localhost',user='root',passwd = 'sas123', db = 'bank1', autocommit=True)
        cursor = conn.cursor()
        mysql = "select token, ListClasses from  %s" % ciku_data
        cursor.execute(mysql)
        all = cursor.fetchall()
        ciku_dict = {}
        for item in all:
            ciku_dict[item[1].upper()] = ciku_dict.get(item[1].upper(), []) + [item[0].strip().decode('gbk').encode('utf-8')]
        postingList = []
        classVec = ciku_dict.keys()
        for each in ciku_dict:
            postingList.append(ciku_dict[each])
        return postingList, classVec
    except Exception, e:
        print e

# 创建MCC分类表
def MCC_Cate_list(cate_data):
    try:
        # select into dict
        conn = MySQLdb.connect(host='localhost',user='root',passwd = 'sas123', db = 'bank1', autocommit=True)
        cursor = conn.cursor()
        mysql = "select MCC_Cate,MCC from %s" % ( cate_data)
        cursor.execute(mysql)
        all = cursor.fetchall()
        MCC_dict = {}
        for  item in all:
            MCC_dict[item[0].upper()] = MCC_dict.get(item[0].upper(), [])+[item[1].strip()]
        return MCC_dict
    except Exception, e:
        print e
#

# main 函数 main_deal
def main_deal(data_in, mccstr, cut = True):
    if cut:
        featureset = cut_featureset(data_in)
        featureset.append(data_in)
    else:

        try:
            featureset = data_in.decode('gbk').encode('utf-8').upper()
        except Exception,e:
            #print e,',Ok,Done!'
            featureset = data_in.upper()
    return classify(featureset, mccstr)

# 处理数据集
def excel_write(open_xls_name, write_xls_name):
    import xlrd, xlwt
    data = xlrd.open_workbook(open_xls_name)
    table = data.sheets()[0]
    wtxls = xlwt.Workbook()
    wt = wtxls.add_sheet('sheet1')
    nrows = table.nrows
    ncols = table.ncols
    colnames = table.row_values(0)
    pointrow = 0
    conn = MySQLdb.connect(host='localhost',user='root',passwd = 'sas123', db = 'bank1', autocommit=True)
    cursor = conn.cursor()
    mysql = "select account,comment,listClasses from sdt_comment2_ana limit 0,448"
    cursor.execute(mysql)
    alldata = cursor.fetchall()

    for rownum in range(1,nrows):
           row = table.row_values(rownum)
           if row:
                for i in range((len(colnames))):
                    wt.write(pointrow+rownum,i ,row[i])
                class_rec, ciku_list, sorted_class = main_deal(MySQLdb.escape_string(alldata[rownum-1][1]), cut=False)
                ciku_list2str = ','.join(each for each in ciku_list)
                if len(sorted_class) > 1:
                    if sorted_class[0][1] == sorted_class[1][1]:
                        sorted_class2str = ','.join(each[0] for each in sorted_class)
                else:
                    sorted_class2str = ''
                wt.write(pointrow + rownum, ncols+1, class_rec)
                wt.write(pointrow + rownum, ncols+2, ciku_list2str)
                wt.write(pointrow + rownum, ncols+3, sorted_class2str)
    wtxls.save(write_xls_name)

#excel_write('test.xls','out.xls')
def deal_work(num,raw_data,out_data,cut=False,num_all = False):
    conn = MySQLdb.connect(host='localhost',user='root',passwd = 'sas123', db = 'bank1', autocommit=True)
    cursor = conn.cursor()
    try:
        start_time = time.clock();print 'Start:'
        mysql = 'select count(*) from %s' % raw_data
        cursor.execute(mysql)
        temp_num = cursor.fetchone()[0]
        num = [num, temp_num][num_all]
        #mysql = "select host_cust_id, cust_postsc from depcard_event limit 0, %d" %num
        mysql = "select account,comment,listClasses from %s limit 0,%d" % ( raw_data,num)
        cursor.execute(mysql)
        alldata = cursor.fetchall()
        mysql = 'drop table %s' %out_data
        cursor.execute(mysql)
        mysql = 'create table if not exists %s (account varchar(21), comment varchar(378),former_class varchar(128), class char(10),ciku_list varchar(128),confuse_class varchar(128))' % out_data
        cursor.execute(mysql)
        if alldata:
                for rec in alldata:
                   try:
                        '''
                        msql = "insert into %s" % out_data +"(account, comment, former_class, class, ciku_list, confuse_class) values('%s', '%s', '%s', '%s', '%s', '%s');"
                        insert_list.append([str(rec[0]), MySQLdb.escape_string(str(rec[1])), MySQLdb.escape_string(rec[2]), class_rec.strip(), \
                                            MySQLdb.escape_string(ciku_list2str.encode('gbk')), MySQLdb.escape_string(sorted_class2str.encode('gbk'))])
                    '''
                        try:
                            class_rec, ciku_list2str, sorted_class2str = main_deal(MySQLdb.escape_string(rec[1]), MySQLdb.escape_string(rec[2]), cut=cut)
                            mysql = "insert into %s(account, comment, former_class, class, ciku_list, confuse_class) values('%s', '%s', '%s', '%s','%s', '%s')" \
                                % (out_data, str(rec[0]).strip(),MySQLdb.escape_string(str(rec[1]).strip()), MySQLdb.escape_string(rec[2].strip()),class_rec.strip() ,\
                                   MySQLdb.escape_string(ciku_list2str.strip().encode('gbk')), MySQLdb.escape_string(sorted_class2str.strip().encode('gbk')))
                        except:
                            mysql = "insert into %s(account, comment,  former_class,class, ciku_list, confuse_class) values('%s', '%s', '%s', '%s', '%s', '%s')" \
                                % (out_data, str(rec[0]).strip(),MySQLdb.escape_string(str(rec[1]).strip()), MySQLdb.escape_string(rec[2]),class_rec.strip() ,\
                                   MySQLdb.escape_string(ciku_list2str.strip().encode('gbk')), MySQLdb.escape_string(sorted_class2str.strip().encode('gbk')))
                        cursor.execute(mysql)
                   except Exception, e:
                        print e, rec[0]
        end_time = time.clock()
        print '执行时长:', int(end_time - start_time),'s'
    except Exception, e:
        print e
    finally:
        conn.close()

postingList,classVec = loadDataSet_from_db('ciku')
MCC_dict = MCC_Cate_list('mcc_cate')
deal_work(2000,'sdt_comment2_ana_chn','sdt_comment2_cutF',cut=False,num_all=False)
print postingList
print classVec
for each in postingList[0][:10]:
    print each
'''
import jieba.analyse
text = ''
tags = jieba.analyse.extract_tags(text,3)
'''
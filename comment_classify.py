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
    classVec = ['CAR','MALL','MARKET','MATERNAL','CATERING','CLOTHING','HOTEL','TOUR','MEDICINE','COSMETIC','BANK']    #1-汽车 2-商场 3-超市 4-母婴用品 0-other ..
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
def prob_classify(featureset):
        # Discard any feature names that we've never seen before.
        # Otherwise, we'll just assign a probability of 0 to
        # everything. [太原市 科美 餐饮服务 有限公司]
        postingList,classVec = loadDataSet()
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

#输出 return分类
def classify(featureset):
        res, ciku_list = prob_classify(featureset)
        sortedClassCount = sorted(res.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sortedClassCount[0][0], ciku_list, sortedClassCount

#进行featureset 切分
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

#main 函数 main_deal
def main_deal(data_in, cut = True):
    if cut:
        featureset = cut_featureset(data_in)
        featureset.append(data_in)
    else:

        try:
            featureset = data_in.decode('gbk').encode('utf-8')
        except Exception,e:
            print e,',Ok,Done!'

            featureset = data_in#.decode('gbk').encode('utf-8')
    return classify(featureset)

#处理数据集
def deal_work(num,raw_data,out_data,cut=False,num_all = False):
    conn = MySQLdb.connect(host='localhost',user='root',passwd = 'sas123', db = 'bank1', autocommit=True)
    cursor = conn.cursor()
    try:
        start_time = time.clock()
        mysql = 'select count(*) from %s' % raw_data
        cursor.execute(mysql)
        temp_num = cursor.fetchone()[0]
        num = [num, temp_num][num_all]
        #mysql = "select host_cust_id, cust_postsc from depcard_event limit 0, %d" %num
        mysql = "select account,comment,listClasses from %s limit 0,%d" % ( raw_data,num)
        cursor.execute(mysql)
        alldata = cursor.fetchall()
        if alldata:
            #mysql = 'create table if not exists jj_comment_cutF(account varchar(30), comment varchar(128), class char(8))'

            mysql = 'create table if not exists %s (account varchar(21), comment varchar(378), class char(8),former_class varchar(128),ciku_list varchar(128))' % out_data
            cursor.execute(mysql)

            with open(r'C:\Users\yulj\Desktop\res.txt','w') as fw:
                for rec in alldata:
                   try:
                        #print repr(rec[2])
                        class_rec, ciku_list, sorted_class = main_deal(MySQLdb.escape_string(rec[1]), cut=cut)
                        ciku_list2str = ','.join(each for each in ciku_list)
                        if len(sorted_class) > 1:
                            if sorted_class[0][1] == sorted_class[1][1]:
                                sorted_class2str = ','.join(each[0] for each in sorted_class)
                        else:
                            sorted_class2str = ''
                        fw.write(str(rec[0]).strip()+':'+ MySQLdb.escape_string(str(rec[1]).strip())+':'+ class_rec.strip()+':'+MySQLdb.escape_string(rec[2].strip())+':'+ciku_list2str.encode('gbk')+':' + sorted_class2str+'\n')
                        try:
                            mysql = "insert into %s(account, comment, class, former_class, ciku_list) values('%s', '%s', '%s', '%s','%s')" \
                                % (out_data, str(rec[0]).strip(),MySQLdb.escape_string(str(rec[1]).strip()), class_rec.strip() ,MySQLdb.escape_string(rec[2].strip()), MySQLdb.escape_string(ciku_list2str.strip().encode('gbk')))
                        except:
                            mysql = "insert into %s(account, comment, class, former_class, ciku_list) values('%s', '%s', '%s', '%s', '%s')" \
                                % (out_data, str(rec[0]).strip(),MySQLdb.escape_string(str(rec[1]).strip()), class_rec.strip() ,MySQLdb.escape_string(rec[2]), MySQLdb.escape_string(ciku_list2str.strip().encode('gbk')))
                        cursor.execute(mysql)

                   except Exception, e:
                        print e, rec[0]
        end_time = time.clock()
        print '执行时长:', int(end_time - start_time),'s'
    except Exception, e:
        print e

deal_work(200,'sdt_comment2_ana','sdt_comment2_cutF',cut=False,num_all=True)

'''
b = prob_classify(['北京','汽车技术服务'])
print b



test = main_deal('九龙坡区九龙园区振华石材经营部dogs',cut=False)
print test


test, ciku_l, sorted_class = main_deal('他行POS 购物退货',cut=False)
print test
for each in ciku_l:
    print each
'''
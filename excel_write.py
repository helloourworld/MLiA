#coding=utf-8
import xlsxwriter
import openpyxl

from os import listdir
import xlrd
import xlwt
def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
    except Exception, e:
        print e
    return data

FileList = listdir('J:\SAS_Platfrom_Apply')
m = len(FileList)
def excel_table_byindex( colnameindex=0, by_index=0):
    #colnameindex 表头所在行 by_index sheet1
    stat = xlwt.Workbook()
    stat_table = stat.add_sheet("Sheet1",)
    pointrow = 0
    for i in range(m):
        file_in = FileList[i]
        print file_in
        data = open_excel(r'J:/SAS_Platfrom_Apply/%s'  %file_in)
        table = data.sheets()[0]
        nrows = table.nrows
        ncols = table.ncols
        colnames = table.row_values(0)
        print nrows, ncols, colnames
        for rownum in range(1,nrows):
            row = table.row_values(rownum)
            if row:
                for i in range((len(colnames))):
                    stat_table.write(pointrow+rownum,i ,row[i])
        pointrow += nrows-1
    for i in range(len(colnames)):
        stat_table.write(0,i,colnames[i])
    stat.save('stat.xls')
#excel_table_byindex()



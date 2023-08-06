import os.path
import xlwt
import xlrd
from xlutils.copy import copy

class GenerateXls:
    
    __workbook = None
    __filename = ""
    __nrows = 0
    
    def __init__(self, filename, mode='a'):
        
        self.__filename = filename
        if(not os.path.exists(filename) or mode == 'w'):
            self.__workbook = xlwt.Workbook()
            ws = self.__workbook.add_sheet('APT报告',cell_overwrite_ok=True)
        elif(mode == 'a'):
            old_excel = xlrd.open_workbook(filename, formatting_info=True)
            self.__nrows = old_excel.sheets()[0].nrows
            self.__workbook = copy(old_excel)
        
    def __addPointer(self):
        self.__nrows += 1
    
    def configStyle(self, n):
        ws = self.__workbook.get_sheet(0)
        for i in range(n):
            ws.col(i).width = 9000    
        # ws.col(0).width = 9000#12000
        # ws.col(1).width = 9000
        # ws.col(2).width = 9000#5000
        # ws.col(3).width = 9000#5000
        # ws.col(4).width = 9000#5000
        # ws.col(5).width = 9000#8000
    
    def appendSingleLine(self, values, cellstyle=xlwt.easyxf(
             'font: name 微软雅黑;'
             'borders: left thin, right thin, top thin, bottom thin;'
             'alignment: horizontal center, vertical center;'
             )):
        ws = self.__workbook.get_sheet(0)
        ws.row(self.__nrows).set_style(xlwt.easyxf('font:height 360;'))

        for i in range(len(values)):
            if(i==0):
                continue
            ws.write(self.__nrows, i-1, values[i], cellstyle)
        # ws.write(self.__nrows, 0, values[0], cellstyle)
        # ws.write(self.__nrows, 1, values[1], cellstyle)
        # ws.write(self.__nrows, 2, values[2], cellstyle)
        # ws.write(self.__nrows, 3, values[3], cellstyle)
        # ws.write(self.__nrows, 4, values[4], cellstyle)
        # ws.write(self.__nrows, 5, values[5], cellstyle)
        
        self.__addPointer()
        
        return self
    
    def appendHeadLine(self, head=['文件名','文件SHA1','发布年份','发布日期','发布方','文件二进制']):

        self.configStyle(len(head)-1)
        return self.appendSingleLine(values = head, cellstyle=xlwt.easyxf(
             'font: name 微软雅黑;'
             'borders: left thin, right thin, top thin, bottom thin;'
             'alignment: horizontal center, vertical center;'
             'pattern: pattern solid, fore_colour gray25;'
             ))
        
    def appendMultiLines(self, res):

        for x in res:
            self.appendSingleLine(x)
        
    
    def exportXLS(self):
        
        self.__workbook.save(self.__filename)
    
    

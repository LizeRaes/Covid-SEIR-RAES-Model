import pandas as pd
import numpy as np
from raes_seir.model.parameters import Parameters
#from classes.parameters import *

class New_measure:

  def __init__(self, date, R0):
    self.date = date
    self.R0 = R0



class Measures:

    def __init__(self, dates, values):
        #init with default
        dataArray = np.array([dates,values])
        self.dataList = pd.DataFrame(np.transpose(dataArray), columns=['Date', 'Values'])
        self.dataList.insert(2, 'endDate', None)
        self.dataList = self.dataList.astype({'Date': np.datetime64, 'endDate':np.datetime64 , 'Values':float})
        self.resetEndDate()

    @classmethod
    def default(cls):
        date = '01/01/2020'
        date = pd.to_datetime(date, format = '%d/%m/%Y')
        R0 = 1.56
        return cls([date], [R0])
    
    @classmethod
    def fromList(cls, dates, values):
        #datesFormat = pd.to_datetime(dates, format = '%d/%m/%Y')
        datesFormat = pd.to_datetime(dates)
        return cls(datesFormat, values)

    @classmethod
    def fromXls(cls, xlsPath):
        #init from a xlsPath
        #currently default
        paramXls = pd.read_excel(xlsPath, sheet_name = 'R0')
        dates = np.array(paramXls['Date'])
        values = np.array(paramXls['R0'])
        return cls(dates, values)

    def resetEndDate(self):
        self.dataList = self.dataList.sort_values(by=['Date'])
        self.dataList.index = range(len(self.dataList))
        for i in range(len(self.dataList)-1):
            self.dataList.at[i, 'endDate'] = self.dataList.at[i+1, 'Date']
        self.dataList.at[len(self.dataList)-1, 'endDate'] = np.datetime64('2022-12-31')

    def getR0(self, lookDate):
        df = self.dataList
        result = df[(df['Date']<=lookDate) & (df['endDate']>lookDate)]
        return float(result['Values'])

    def addR0 (self, dateText, valueText):
        date = np.datetime64(dateText)
        value = (valueText)
        self.dataList = self.dataList.append({'Date': date, 'Values': value}, ignore_index = True)
        self.resetEndDate()

    def removeR0 (self, index):
        self.dataList=self.dataList.drop(index)
        self.resetEndDate()

    def __str__(self):
        return str(self.dataList)

    #TO DO
    def remove_latest_measure(self):
        todo = 1


def main():
    # my code here
    #testList = Measures.default()
    #testList = Measures.fromList(['2020-01-01','2020-02-01'],[1.45, 1.67])
    testList = Measures.fromXls('param_test.xlsx')
    print(testList)
    print(testList.dataList.dtypes)
    print(testList.dataList['Date'][1]-testList.dataList['Date'][0])
    
    testList.addR0('2020-03-14', 3.9)
    testList.addR0('2020-06-19', 7.9)
    
    lookDate = '2020-07-01'
    print(testList)
    print(testList.getR0(lookDate))
    
    testList.addR0('2020-08-14', 4.9)
    
    print(testList)
    print(testList.getR0(lookDate))
    
    testList.removeR0(1)
    
    print(testList)
    print(testList.getR0(lookDate))
    
    testList.removeR0(2)
    
    print(testList)
    print(testList.getR0(lookDate))
    
    testList.addR0('2020-06-26', 14.9)
    
    print(testList)
    print(testList.getR0(lookDate))
    print(testList.getR0('2020-03-14'))
    #print(testParam.R0)
    print('--')
    newlist = Measures.fromXls('param_test.xlsx')
    print(newlist)
    param = Parameters()
    print(newlist.getR0(np.datetime64(param.pivotDate)))
    

if __name__ == "__main__":
    main()

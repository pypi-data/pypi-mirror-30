#from xlrd import open_workbook
# from pandas import iNaT, NaT, Timestamp, Timedelta, OutOfBoundsDatetime
# import warnings
# warnings.filterwarnings("ignore", message="numpy.dtype size changed")
import pandas as df
# from pandas import iNaT, NaT, Timestamp, Timedelta, OutOfBoundsDatetime

pd = df.read_csv('C:\\Users\\kgueta\\AppData\\Local\\Continuum\\anaconda2\\envs\\chdlab\\DevConf.xlsx')

print df

# book = open_workbook('DevConf.xlsx')
# sheet1 = book.sheet_by_index(0)

# # read header values into the list    
# keys = [sheet1.cell(0, col_index).value for col_index in xrange(sheet1.ncols)]

# dict_list = []
# for row_index in xrange(1, sheet1.nrows):
#     d = {keys[col_index]: sheet.cell(row_index, col_index).value 
#          for col_index in xrange(sheet1.ncols)}
#     dict_list.append(d)

# print dict_list
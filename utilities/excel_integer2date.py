#!/usr/bin/env python

"""
O2unit_convert.py

Convert ml/l to Mm/kg or vice versa

Used for discreet oxygen samples from Mordy
"""
#System Stack
import datetime
import argparse

from netCDF4 import num2date

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 10, 30)
__modified__ = datetime.datetime(2014, 10, 30)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'SeaWater', 'Cruise', 'derivations'



"""----------------------------- Read from Excel O2 files ------------------"""

def readXlsx(fileName,**args):
 import zipfile
 from xml.etree.ElementTree import iterparse
 if "sheet" in args:
    sheet=args["sheet"]
 else:
    sheet=1
 if "header" in args:
    isHeader=args["header"]
 else:
    isHeader=False

 rows = []
 row = {}
 header = {}
 z=zipfile.ZipFile(fileName)
 # Get shared strings
 strings = [el.text for e, el in iterparse(z.open('xl/sharedStrings.xml')) if el.tag.endswith('}t')]
 value = ''

 # Open specified worksheet
 for e, el in iterparse(z.open('xl/worksheets/sheet%d.xml'%(sheet))):
    # get value or index to shared strings
    if el.tag.endswith('}v'): # <v>84</v>
        value = el.text
    if el.tag.endswith('}c'): # <c r="A3" t="s"><v>84</v></c>
        # If value is a shared string, use value as an index
        if el.attrib.get('t') == 's':
            value = strings[int(value)]
        # split the row/col information so that the row leter(s) can be separate
        letter = el.attrib['r'] # AZ22
        while letter[-1].isdigit():
            letter = letter[:-1]
        # if it is the first row, then create a header hash for the names
        # that COULD be used
        if rows ==[]:
            header[letter]=value
        else:
            if value != '': 
                # if there is a header row, use the first row's names as the row hash index
                if isHeader == True and letter in header:
                    row[header[letter]] = value
                else:
                    row[letter] = value

        value = ''
    if el.tag.endswith('}row'):
        rows.append(row)
        row = {}
 z.close()
 return rows
 
 """----------------------------- Main -------------------------------------"""
parser = argparse.ArgumentParser(description='Discreet Oxygen Unit Conversion')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('excelsheet', metavar='excelsheet', type=int,
               help='sheet in excel file')
parser.add_argument('integer', metavar='integer', type=str, help='column in excel file')               
parser.add_argument('timestr', metavar='timestr', type=str, help='timestr')               
         
args = parser.parse_args()

### example path - '/Users/bell/Data_Local/FOCI/discreetoxygendata/2014/aq1401/AQ1401_O2.xlsx'
W = readXlsx(args.DataPath, sheet=args.excelsheet)

pplus2date = False
if pplus2date is True:
    for index, row in enumerate(W):
        if index == 0:
            continue
        try:
            print num2date(int(row[args.integer]),args.timestr)
        except:
            print ''    

subsample = True
if subsample is True:
    for index, row in enumerate(W):
        if index == 0:
            continue
        if float(row['A'])%0.25 ==0:
            print "{0},{1}".format(row['A'], row['E'])

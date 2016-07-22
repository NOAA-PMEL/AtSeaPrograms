#!/usr/bin/env python

"""
O2unit_convert.py

Convert ml/l to Mm/kg or vice versa

Used for discreet oxygen samples from Mordy
"""
#System Stack
import datetime
import argparse

#Science Stack
import seawater as sw

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 10, 30)
__modified__ = datetime.datetime(2014, 10, 30)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'SeaWater', 'Cruise', 'derivations'

"""----------------------------- Density Correction ------------------------"""
def O2_conv(S,T,P,O2conc):
    """sal, temp, press, oxy conc"""
    sigmatheta_pri = sw.eos80.pden(S, T, P)
    density = (sigmatheta_pri / 1000)
    O2conc = O2conc / density
    return O2conc

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
parser.add_argument('sal', metavar='sal', type=str, help='column in excel file')               
parser.add_argument('temp', metavar='temp', type=str, help='column in excel file')               
parser.add_argument('press', metavar='press', type=str, help='column in excel file')               
parser.add_argument('oxy', metavar='oxy', type=str, help='column in excel file')               
args = parser.parse_args()

### example path - '/Users/bell/Data_Local/FOCI/discreetoxygendata/2014/aq1401/AQ1401_O2.xlsx'
W = readXlsx(args.DataPath, sheet=args.excelsheet)

print "umol/l to umol/kg \n"
for index, row in enumerate(W):
    if index == 0:
        continue
    try:
        print O2_conv(float(row[args.sal]),float(row[args.temp]),float(row[args.press]),float(row[args.oxy]))
    except:
        print ''    

print "sigma-t"
for index, row in enumerate(W):
    if index == 0:
        continue
    try:
        print sw.eos80.dens0(float(row[args.sal]),float(row[args.temp]))-1000
    except:
        print ''  
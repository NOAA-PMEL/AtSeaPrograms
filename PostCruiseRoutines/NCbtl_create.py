#!/usr/bin/env python

"""
 Background:
 --------
 NCbtl_create.py
 
 
 Purpose:
 --------
 Creates EPIC flavored .nc files for bottle (upcast) data
 
 File Format:
 ------------
 Assumes .xlsx file with following headers:
 cast	date	time	nb	Sal00	Sal11	Sbeox0Mm/Kg	Sbeox0PS	Sbeox1Mm/Kg	Sbeox1PS	Sigma-t00	PrDM	DepSM	T090C	T190C	Par	V0	V6	WetStar

 cast, date, time, nb are essential - all others will be filled in with missing values if they are not available

 02/03/2016 - modified btl2nc.py and NCbtl_create.py - EPIC variables (and any netcdf variables) are now defined in a *_epickeys.json file

"""

#System Stack
import datetime
import argparse
import collections
import sys

#Science Stack
from netCDF4 import Dataset
import numpy as np

# User Packages
import utilities.ConfigParserLocal as ConfigParserLocal
import btl2nc

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2015, 10, 02)
__modified__ = datetime.datetime(2015, 10, 02)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet','report'

"""----------------------------- Read from Excel files --------------------------------"""

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

##
# Convert an Excel number (presumed to represent a date, a datetime or a time) into
# a Python datetime.datetime
# @param xldate The Excel number
# @param datemode 0: 1900-based, 1: 1904-based.
# <br>WARNING: when using this function to
# interpret the contents of a workbook, you should pass in the Book.datemode
# attribute of that workbook. Whether
# the workbook has ever been anywhere near a Macintosh is irrelevant.
# @return a datetime.datetime object, to the nearest_second.
# <br>Special case: if 0.0 <= xldate < 1.0, it is assumed to represent a time;
# a datetime.time object will be returned.
# <br>Note: 1904-01-01 is not regarded as a valid date in the datemode 1 system; its "serial number"
# is zero.
# @throws XLDateNegative xldate < 0.00
# @throws XLDateAmbiguous The 1900 leap-year problem (datemode == 0 and 1.0 <= xldate < 61.0)
# @throws XLDateTooLarge Gregorian year 10000 or later
# @throws XLDateBadDatemode datemode arg is neither 0 nor 1
# @throws XLDateError Covers the 4 specific errors

def xldate_as_datetime(xldate, datemode):
    if datemode not in (0, 1):
        sys.exit()
        #raise XLDateBadDatemode(datemode)
    if xldate == 0.00:
        return datetime.time(0, 0, 0)
    if xldate < 0.00:
        sys.exit()
        #raise XLDateNegative(xldate)
    xldays = int(xldate)
    frac = xldate - xldays
    seconds = int(round(frac * 86400.0))
    assert 0 <= seconds <= 86400
    if seconds == 86400:
        seconds = 0
        xldays += 1
    if xldays == 0:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)
        return datetime.time(hour, minute, second)
    return (
        datetime.datetime.fromordinal(xldays + 693594 + 1462 * datemode)
        + datetime.timedelta(seconds=seconds)
        )
    
"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='xlsx btl to nc')
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .report_btl summary file')
parser.add_argument('output', metavar='output', type=str, help='output path')
parser.add_argument('CruiseID', metavar='CruiseID', type=str, help='CruiseID')
parser.add_argument('datemode', metavar='datemode', type=int, help='0 or 1 for 1900 or 1904 based excel dates')
parser.add_argument("-ib",'--inverted_bottle_order', action="store_true", help='flag if bottles are high to low')


args = parser.parse_args()

############################################
#                                          #
# Retrieve initialization paramters from 
#   various external files
### EPIC Dictionary definitions for WPAK data ###
# If these variables are not defined, no data will be archived into the nc file for that parameter.
EPIC_VARS_dict = ConfigParserLocal.get_config('bottle_epickeys.json')


### there can be multiple variables output from the upcast that may not be archived in the netcdf but the following are always
# archived whether they exist or not
header_example = ['cast', 'date', 'time', 'nb', 'Sal00', 'Sal11', 'Sbeox0Mm/Kg', 'Sbeox0PS', 'Sbeox1Mm/Kg', 'Sbeox1PS',\
                  'Sigma-t00', 'PrDM', 'DepSM', 'T090C', 'T190C', 'Par', 'V0', 'V6', 'WetStar', 'turbWETntu0', 'FlECO-AFL', 'CStarTr0']


### read in data file
# from each line, look for expected values to be archived filling in missing
# values with 1e35.  Build nc files as each cast cycles
excelfiles = args.inputpath
print "Reading file {0}".format(excelfiles)
W = readXlsx(excelfiles, sheet=1, header=True)
data = collections.OrderedDict()
for index, row in enumerate(W):
    if index==0:
        print row
    else:
        try:
            data[row['cast']+'_'+row['nb']] = row
        except:
            print "No btl log for {0}:{1}".format(row['cast'],row['nb'])


#start with cast ctd001 and go until ctd200 looking for 12 bottles a cast
firstcast=True
nb, Sal00, Sal11, Sbeox0Mm, Sbeox0ps = [], [], [], [], []
Sbeox1Mm, Sbeox1ps, Sigmat0, PrDm, DepSM = [], [], [], [], []
T090C, T190C, Par, WetStar = [],[],[],[]
turbWETntu0, FlECOAFL, CStarTr0 = [], [], []
btl_num = 0
if not args.inverted_bottle_order:
    btl_num = 0
    for index,val in enumerate(data):
        if (int(data[val]['nb']) > btl_num):
            try:
                Sal00 = Sal00 + [round(float(data[val]['Sal00']),4)]
            except:
                Sal00 = Sal00 + [1e35]
            try:
                Sal11 = Sal11 + [round(float(data[val]['Sal11']),4)]
            except:
                Sal11 = Sal11 + [1e35]
            try:
                Sbeox0Mm = Sbeox0Mm + [round(float(data[val]['Sbeox0Mm/Kg']),4)]
            except:
                Sbeox0Mm = Sbeox0Mm + [1e35]
            try:
                Sbeox0ps = Sbeox0ps + [round(float(data[val]['Sbeox0ps']),4)]
            except:
                Sbeox0ps = Sbeox0ps + [1e35]
            try:
                Sbeox1Mm = Sbeox1Mm + [round(float(data[val]['Sbeox1Mm/Kg']),4)]
            except:
                Sbeox1Mm = Sbeox1Mm + [1e35]
            try:
                Sbeox1ps = Sbeox1ps + [round(float(data[val]['Sbeox1ps']),4)]
            except:
                Sbeox1ps = Sbeox1ps + [1e35]
            try:
                Sigmat0 = Sigmat0 + [round(float(data[val]['Sigma-t00']),4)]
            except:
                Sigmat0 = Sigmat0 + [1e35]
            try:
                PrDm = PrDm + [round(float(data[val]['PrDM']),4)]
            except:
                try:
                    PrDm = PrDm + [round(float(data[val]['PrSM']),4)]
                except:
                    PrDm = PrDm + [1e35]
            try:
                DepSM = DepSM + [round(float(data[val]['DepSM']),4)]
            except:
                DepSM = DepSM + [1e35]
            try:
                T090C = T090C + [round(float(data[val]['T090C']),4)]
            except:
                T090C = T090C + [1e35]
            try:
                T190C = T190C + [round(float(data[val]['T190C']),4)]
            except:
                T190C = T190C + [1e35]
            try:
                Par = Par + [round(float(data[val]['Par']),4)]
            except:
                Par = Par + [1e35]
            try:
                WetStar = WetStar + [round(float(data[val]['WetStar']),4)]
            except:
                WetStar = WetStar + [1e35]
            try:
                turbWETntu0 = turbWETntu0 + [round(float(data[val]['turbWETntu0']),4)]
            except:
                try:
                    turbWETntu0 = turbWETntu0 + [round(float(data[val]['Obs']),4)]
                except:
                    turbWETntu0 = turbWETntu0 + [1e35]
            try:
                FlECOAFL = FlECOAFL + [round(float(data[val]['FlECO-AFL']),4)]
            except:
                FlECOAFL = FlECOAFL + [1e35]
            try:
                CStarTr0 = CStarTr0 + [round(float(data[val]['CStarTr0']),4)]
            except:
                CStarTr0 = CStarTr0 + [1e35]

            btl_num=int(data[val]['nb'])
            nb = nb + [int(data[val]['nb'])]
            cast = data[val]['cast']
            CruiseID = args.CruiseID
            dtime = btl2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                        isdatetime=True).get_EPIC_date()
            data_saved = False
        elif (int(data[val]['nb']) == btl_num) and data_saved:
            print "Working on one bottle Cast {0}-{1}".format(cast, CruiseID)

            #cycle through and build data arrays
            #create a "data_dic" and associate the data with an epic key
            #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
            # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
            # if it is below but not the epic dic, it will not make it to the nc file
            data_dic = {}
            data_dic['Tr_904'] = np.array(CStarTr0)
            data_dic['Trb_980'] = np.array(turbWETntu0)
            data_dic['S_42'] = np.array(Sal00)
            data_dic['S_41'] = np.array(Sal11)
            data_dic['D_3'] = np.array(DepSM)
            data_dic['fWS_973'] = np.array(WetStar)
            data_dic['F_903'] = np.array(FlECOAFL)
            data_dic['O_65'] = np.array(Sbeox0Mm)
            data_dic['OST_62'] = np.array(Sbeox0ps)
            data_dic['CTDOXY_4221'] = np.array(Sbeox1Mm)
            data_dic['CTDOST_4220'] = np.array(Sbeox1ps)
            data_dic['T_28'] = np.array(T090C)
            data_dic['T2_35'] = np.array(T190C)
            data_dic['BTL_103'] = np.array(nb)
            data_dic['PAR_905'] = np.array(Par)
            data_dic['ST_70'] = np.array(Sigmat0)
                
            #PMEL EPIC Conventions
            ncinstance = btl2nc.CTDbtl_NC(savefile=(args.output + CruiseID + cast.lower().replace('ctd', 'c') + '_btl.nc'))
            ncinstance.file_create()
            ncinstance.sbeglobal_atts(raw_data_file=excelfiles.split('/')[-1]) # 
            ncinstance.dimension_init(depth_len=len(PrDm))
            ncinstance.variable_init(EPIC_VARS_dict)
            ncinstance.add_data(EPIC_VARS_dict,data_dic)
            ncinstance.add_coord_data(depth=PrDm, time1=dtime[0], time2=dtime[1])
            ncinstance.close()


            #reinit array
            nb, Sal00, Sal11, Sbeox0Mm, Sbeox0ps = [], [], [], [], []
            Sbeox1Mm, Sbeox1ps, Sigmat0, PrDm, DepSM = [], [], [], [], []
            T090C, T190C, Par, WetStar = [],[],[],[]
            turbWETntu0, FlECOAFL, CStarTr0 = [], [], []
            try:
                Sal00 = Sal00 + [round(float(data[val]['Sal00']),4)]
            except:
                Sal00 = Sal00 + [1e35]
            try:
                Sal11 = Sal11 + [round(float(data[val]['Sal11']),4)]
            except:
                Sal11 = Sal11 + [1e35]
            try:
                Sbeox0Mm = Sbeox0Mm + [round(float(data[val]['Sbeox0Mm/Kg']),4)]
            except:
                Sbeox0Mm = Sbeox0Mm + [1e35]
            try:
                Sbeox0ps = Sbeox0ps + [round(float(data[val]['Sbeox0ps']),4)]
            except:
                Sbeox0ps = Sbeox0ps + [1e35]
            try:
                Sbeox1Mm = Sbeox1Mm + [round(float(data[val]['Sbeox1Mm/Kg']),4)]
            except:
                Sbeox1Mm = Sbeox1Mm + [1e35]
            try:
                Sbeox1ps = Sbeox1ps + [round(float(data[val]['Sbeox1ps']),4)]
            except:
                Sbeox1ps = Sbeox1ps + [1e35]
            try:
                Sigmat0 = Sigmat0 + [round(float(data[val]['Sigma-t00']),4)]
            except:
                Sigmat0 = Sigmat0 + [1e35]
            try:
                PrDm = PrDm + [round(float(data[val]['PrDM']),4)]
            except:
                try:
                    PrDm = PrDm + [round(float(data[val]['PrSM']),4)]
                except:
                    PrDm = PrDm + [1e35]
            try:
                DepSM = DepSM + [round(float(data[val]['DepSM']),4)]
            except:
                DepSM = DepSM + [1e35]
            try:
                T090C = T090C + [round(float(data[val]['T090C']),4)]
            except:
                T090C = T090C + [1e35]
            try:
                T190C = T190C + [round(float(data[val]['T190C']),4)]
            except:
                T190C = T190C + [1e35]
            try:
                Par = Par + [round(float(data[val]['Par']),4)]
            except:
                Par = Par + [1e35]
            try:
                WetStar = WetStar + [round(float(data[val]['WetStar']),4)]
            except:
                WetStar = WetStar + [1e35]
            try:
                turbWETntu0 = turbWETntu0 + [round(float(data[val]['turbWETntu0']),4)]
            except:
                try:
                    turbWETntu0 = turbWETntu0 + [round(float(data[val]['Obs']),4)]
                except:
                    turbWETntu0 = turbWETntu0 + [1e35]
            try:
                FlECOAFL = FlECOAFL + [round(float(data[val]['FlECO-AFL']),4)]
            except:
                FlECOAFL = FlECOAFL + [1e35]
            try:
                CStarTr0 = CStarTr0 + [round(float(data[val]['CStarTr0']),4)]
            except:
                CStarTr0 = CStarTr0 + [1e35]

            btl_num=int(data[val]['nb'])    
            nb = nb + [int(data[val]['nb'])]
            cast = data[val]['cast']
            CruiseID = args.CruiseID  
            dtime = btl2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                        isdatetime=True).get_EPIC_date()
            data_saved = False
        else:
            ###make netcdf
            print "Working on Cast {0}-{1}".format(cast, CruiseID)

            #cycle through and build data arrays
            #create a "data_dic" and associate the data with an epic key
            #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
            # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
            # if it is below but not the epic dic, it will not make it to the nc file
            data_dic = {}
            data_dic['Tr_904'] = np.array(CStarTr0)
            data_dic['Trb_980'] = np.array(turbWETntu0)
            data_dic['S_42'] = np.array(Sal00)
            data_dic['S_41'] = np.array(Sal11)
            data_dic['D_3'] = np.array(DepSM)
            data_dic['fWS_973'] = np.array(WetStar)
            data_dic['F_903'] = np.array(FlECOAFL)
            data_dic['O_65'] = np.array(Sbeox0Mm)
            data_dic['OST_62'] = np.array(Sbeox0ps)
            data_dic['CTDOXY_4221'] = np.array(Sbeox1Mm)
            data_dic['CTDOST_4220'] = np.array(Sbeox1ps)
            data_dic['T_28'] = np.array(T090C)
            data_dic['T2_35'] = np.array(T190C)
            data_dic['BTL_103'] = np.array(nb)
            data_dic['PAR_905'] = np.array(Par)
            data_dic['ST_70'] = np.array(Sigmat0)
                
            #PMEL EPIC Conventions
            ncinstance = btl2nc.CTDbtl_NC(savefile=(args.output + CruiseID + cast.lower().replace('ctd', 'c') + '_btl.nc'))
            ncinstance.file_create()
            ncinstance.sbeglobal_atts(raw_data_file=excelfiles.split('/')[-1]) # 
            ncinstance.dimension_init(depth_len=len(PrDm))
            ncinstance.variable_init(EPIC_VARS_dict)
            ncinstance.add_data(EPIC_VARS_dict,data_dic)
            ncinstance.add_coord_data(depth=PrDm, time1=dtime[0], time2=dtime[1])
            ncinstance.close()

            data_saved = True

            #reinit array
            nb, Sal00, Sal11, Sbeox0Mm, Sbeox0ps = [], [], [], [], []
            Sbeox1Mm, Sbeox1ps, Sigmat0, PrDm, DepSM = [], [], [], [], []
            T090C, T190C, Par, WetStar = [],[],[],[]
            turbWETntu0, FlECOAFL, CStarTr0 = [], [], []
            try:
                Sal00 = Sal00 + [round(float(data[val]['Sal00']),4)]
            except:
                Sal00 = Sal00 + [1e35]
            try:
                Sal11 = Sal11 + [round(float(data[val]['Sal11']),4)]
            except:
                Sal11 = Sal11 + [1e35]
            try:
                Sbeox0Mm = Sbeox0Mm + [round(float(data[val]['Sbeox0Mm/Kg']),4)]
            except:
                Sbeox0Mm = Sbeox0Mm + [1e35]
            try:
                Sbeox0ps = Sbeox0ps + [round(float(data[val]['Sbeox0ps']),4)]
            except:
                Sbeox0ps = Sbeox0ps + [1e35]
            try:
                Sbeox1Mm = Sbeox1Mm + [round(float(data[val]['Sbeox1Mm/Kg']),4)]
            except:
                Sbeox1Mm = Sbeox1Mm + [1e35]
            try:
                Sbeox1ps = Sbeox1ps + [round(float(data[val]['Sbeox1ps']),4)]
            except:
                Sbeox1ps = Sbeox1ps + [1e35]
            try:
                Sigmat0 = Sigmat0 + [round(float(data[val]['Sigma-t00']),4)]
            except:
                Sigmat0 = Sigmat0 + [1e35]
            try:
                PrDm = PrDm + [round(float(data[val]['PrDM']),4)]
            except:
                try:
                    PrDm = PrDm + [round(float(data[val]['PrSM']),4)]
                except:
                    PrDm = PrDm + [1e35]
            try:
                DepSM = DepSM + [round(float(data[val]['DepSM']),4)]
            except:
                DepSM = DepSM + [1e35]
            try:
                T090C = T090C + [round(float(data[val]['T090C']),4)]
            except:
                T090C = T090C + [1e35]
            try:
                T190C = T190C + [round(float(data[val]['T190C']),4)]
            except:
                T190C = T190C + [1e35]
            try:
                Par = Par + [round(float(data[val]['Par']),4)]
            except:
                Par = Par + [1e35]
            try:
                WetStar = WetStar + [round(float(data[val]['WetStar']),4)]
            except:
                WetStar = WetStar + [1e35]
            try:
                turbWETntu0 = turbWETntu0 + [round(float(data[val]['turbWETntu0']),4)]
            except:
                try:
                    turbWETntu0 = turbWETntu0 + [round(float(data[val]['Obs']),4)]
                except:
                    turbWETntu0 = turbWETntu0 + [1e35]
            try:
                FlECOAFL = FlECOAFL + [round(float(data[val]['FlECO-AFL']),4)]
            except:
                FlECOAFL = FlECOAFL + [1e35]
            try:
                CStarTr0 = CStarTr0 + [round(float(data[val]['CStarTr0']),4)]
            except:
                CStarTr0 = CStarTr0 + [1e35]

            btl_num=int(data[val]['nb'])    
            nb = nb + [int(data[val]['nb'])]
            cast = data[val]['cast']
            CruiseID = args.CruiseID
            try:
                dtime = btl2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                            isdatetime=True).get_EPIC_date()
            except:
                pass        
else:
    btl_num = 12
    for index,val in enumerate(data):
        if (int(data[val]['nb']) <= btl_num):
            try:
                Sal00 = Sal00 + [round(float(data[val]['Sal00']),4)]
            except:
                Sal00 = Sal00 + [1e35]
            try:
                Sal11 = Sal11 + [round(float(data[val]['Sal11']),4)]
            except:
                Sal11 = Sal11 + [1e35]
            try:
                Sbeox0Mm = Sbeox0Mm + [round(float(data[val]['Sbeox0Mm/Kg']),4)]
            except:
                Sbeox0Mm = Sbeox0Mm + [1e35]
            try:
                Sbeox0ps = Sbeox0ps + [round(float(data[val]['Sbeox0ps']),4)]
            except:
                Sbeox0ps = Sbeox0ps + [1e35]
            try:
                Sbeox1Mm = Sbeox1Mm + [round(float(data[val]['Sbeox1Mm/Kg']),4)]
            except:
                Sbeox1Mm = Sbeox1Mm + [1e35]
            try:
                Sbeox1ps = Sbeox1ps + [round(float(data[val]['Sbeox1ps']),4)]
            except:
                Sbeox1ps = Sbeox1ps + [1e35]
            try:
                Sigmat0 = Sigmat0 + [round(float(data[val]['Sigma-t00']),4)]
            except:
                Sigmat0 = Sigmat0 + [1e35]
            try:
                PrDm = PrDm + [round(float(data[val]['PrDM']),4)]
            except:
                try:
                    PrDm = PrDm + [round(float(data[val]['PrSM']),4)]
                except:
                    PrDm = PrDm + [1e35]
            try:
                DepSM = DepSM + [round(float(data[val]['DepSM']),4)]
            except:
                DepSM = DepSM + [1e35]
            try:
                T090C = T090C + [round(float(data[val]['T090C']),4)]
            except:
                T090C = T090C + [1e35]
            try:
                T190C = T190C + [round(float(data[val]['T190C']),4)]
            except:
                T190C = T190C + [1e35]
            try:
                Par = Par + [round(float(data[val]['Par']),4)]
            except:
                Par = Par + [1e35]
            try:
                WetStar = WetStar + [round(float(data[val]['WetStar']),4)]
            except:
                WetStar = WetStar + [1e35]
            try:
                turbWETntu0 = turbWETntu0 + [round(float(data[val]['turbWETntu0']),4)]
            except:
                turbWETntu0 = turbWETntu0 + [1e35]
            try:
                FlECOAFL = FlECOAFL + [round(float(data[val]['FlECO-AFL']),4)]
            except:
                FlECOAFL = FlECOAFL + [1e35]
            try:
                CStarTr0 = CStarTr0 + [round(float(data[val]['CStarTr0']),4)]
            except:
                CStarTr0 = CStarTr0 + [1e35]

            btl_num=int(data[val]['nb'])
            nb = nb + [int(data[val]['nb'])]
            cast = data[val]['cast']
            CruiseID = args.CruiseID
            dtime = btl2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                        isdatetime=True).get_EPIC_date() 
        else:
            ###make netcdf
            print "Working on Cast {0}-{1}".format(cast, CruiseID)

            #cycle through and build data arrays
            #create a "data_dic" and associate the data with an epic key
            #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
            # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
            # if it is below but not the epic dic, it will not make it to the nc file
            data_dic = {}
            data_dic['Tr_904'] = np.array(CStarTr0)
            data_dic['Trb_980'] = np.array(turbWETntu0)
            data_dic['S_42'] = np.array(Sal00)
            data_dic['S_41'] = np.array(Sal11)
            data_dic['D_3'] = np.array(DepSM)
            data_dic['fWS_973'] = np.array(WetStar)
            data_dic['F_903'] = np.array(FlECOAFL)
            data_dic['O_65'] = np.array(Sbeox0Mm)
            data_dic['OST_62'] = np.array(Sbeox0ps)
            data_dic['CTDOXY_4221'] = np.array(Sbeox1Mm)
            data_dic['CTDOST_4220'] = np.array(Sbeox1ps)
            data_dic['T_28'] = np.array(T090C)
            data_dic['T2_35'] = np.array(T190C)
            data_dic['BTL_103'] = np.array(nb)
            data_dic['PAR_905'] = np.array(Par)
            data_dic['ST_70'] = np.array(Sigmat0)
                
            #PMEL EPIC Conventions
            ncinstance = btl2nc.CTDbtl_NC(savefile=(args.output + CruiseID + cast.lower().replace('ctd', 'c') + '_btl.nc'))
            ncinstance.file_create()
            ncinstance.sbeglobal_atts(raw_data_file=excelfiles.split('/')[-1]) # 
            ncinstance.dimension_init(depth_len=len(PrDm))
            ncinstance.variable_init(EPIC_VARS_dict)
            ncinstance.add_data(EPIC_VARS_dict,data_dic)
            ncinstance.add_coord_data(depth=PrDm, time1=dtime[0], time2=dtime[1])
            ncinstance.close()


            #reinit array
            nb, Sal00, Sal11, Sbeox0Mm, Sbeox0ps = [], [], [], [], []
            Sbeox1Mm, Sbeox1ps, Sigmat0, PrDm, DepSM = [], [], [], [], []
            T090C, T190C, Par, WetStar = [],[],[],[]
            turbWETntu0, FlECOAFL, CStarTr0 = [], [], []
            try:
                Sal00 = Sal00 + [round(float(data[val]['Sal00']),4)]
            except:
                Sal00 = Sal00 + [1e35]
            try:
                Sal11 = Sal11 + [round(float(data[val]['Sal11']),4)]
            except:
                Sal11 = Sal11 + [1e35]
            try:
                Sbeox0Mm = Sbeox0Mm + [round(float(data[val]['Sbeox0Mm/Kg']),4)]
            except:
                Sbeox0Mm = Sbeox0Mm + [1e35]
            try:
                Sbeox0ps = Sbeox0ps + [round(float(data[val]['Sbeox0ps']),4)]
            except:
                Sbeox0ps = Sbeox0ps + [1e35]
            try:
                Sbeox1Mm = Sbeox1Mm + [round(float(data[val]['Sbeox1Mm/Kg']),4)]
            except:
                Sbeox1Mm = Sbeox1Mm + [1e35]
            try:
                Sbeox1ps = Sbeox1ps + [round(float(data[val]['Sbeox1ps']),4)]
            except:
                Sbeox1ps = Sbeox1ps + [1e35]
            try:
                Sigmat0 = Sigmat0 + [round(float(data[val]['Sigma-t00']),4)]
            except:
                Sigmat0 = Sigmat0 + [1e35]
            try:
                PrDm = PrDm + [round(float(data[val]['PrDM']),4)]
            except:
                try:
                    PrDm = PrDm + [round(float(data[val]['PrSM']),4)]
                except:
                    PrDm = PrDm + [1e35]
            try:
                DepSM = DepSM + [round(float(data[val]['DepSM']),4)]
            except:
                DepSM = DepSM + [1e35]
            try:
                T090C = T090C + [round(float(data[val]['T090C']),4)]
            except:
                T090C = T090C + [1e35]
            try:
                T190C = T190C + [round(float(data[val]['T190C']),4)]
            except:
                T190C = T190C + [1e35]
            try:
                Par = Par + [round(float(data[val]['Par']),4)]
            except:
                Par = Par + [1e35]
            try:
                WetStar = WetStar + [round(float(data[val]['WetStar']),4)]
            except:
                WetStar = WetStar + [1e35]
            try:
                turbWETntu0 = turbWETntu0 + [round(float(data[val]['turbWETntu0']),4)]
            except:
                turbWETntu0 = turbWETntu0 + [1e35]
            try:
                FlECOAFL = FlECOAFL + [round(float(data[val]['FlECO-AFL']),4)]
            except:
                FlECOAFL = FlECOAFL + [1e35]
            try:
                CStarTr0 = CStarTr0 + [round(float(data[val]['CStarTr0']),4)]
            except:
                CStarTr0 = CStarTr0 + [1e35]

            btl_num=int(data[val]['nb'])    
            nb = nb + [int(data[val]['nb'])]
            CruiseID = args.CruiseID
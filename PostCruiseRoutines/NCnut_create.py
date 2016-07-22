#!/usr/bin/env python

"""
 Background:
 --------
 NCbtl_create.py
 
 
 Purpose:
 --------
 Creates EPIC flavored .nc files for bottle (nutrient) data
 
 File Format:
 ------------
 Assumes .xlsx file with following headers:
 (first 7 columns are nutrient processed, next 5 come from btl files, last two are user created
 Cast	Niskin	PO4 (uM)	Sil (uM)	NO3 (uM)	NO2 (uM)	NH4 (uM)		cast	date	time	nb	PrDM	nisken match	PrDM Round
 
 must specify the units (micromoles/kg or micromoles/l)

 Built using Anaconda packaged Python:


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
import nut2nc

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet'

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


def xldate_as_datetime(xldate, datemode):
    """
    Convert an Excel number (presumed to represent a date, a datetime or a time) into
    a Python datetime.datetime
    @param xldate The Excel number
    @param datemode 0: 1900-based, 1: 1904-based.
    <br>WARNING: when using this function to
    interpret the contents of a workbook, you should pass in the Book.datemode
    attribute of that workbook. Whether
    the workbook has ever been anywhere near a Macintosh is irrelevant.
    @return a datetime.datetime object, to the nearest_second.
    <br>Special case: if 0.0 <= xldate < 1.0, it is assumed to represent a time;
    a datetime.time object will be returned.
    <br>Note: 1904-01-01 is not regarded as a valid date in the datemode 1 system; its "serial number"
    is zero.
    @throws XLDateNegative xldate < 0.00
    @throws XLDateAmbiguous The 1900 leap-year problem (datemode == 0 and 1.0 <= xldate < 61.0)
    @throws XLDateTooLarge Gregorian year 10000 or later
    @throws XLDateBadDatemode datemode arg is neither 0 nor 1
    @throws XLDateError Covers the 4 specific errors
    """



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
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .xlsx nutrient file')
parser.add_argument('sheet', metavar='sheet', type=int, help='sheet number in .xlsx file')
parser.add_argument('output', metavar='output', type=str, help='output path')
parser.add_argument('datemode', metavar='datemode', type=int, help='0 or 1 for 1900 or 1904 based excel dates')
parser.add_argument("-um_l",'--micromoles_liter', action="store_true", help='units of micromoles per liter')
parser.add_argument("-um_kg",'--micromoles_kilogram', action="store_true", help='units of micromoles per kg')

args = parser.parse_args()

if args.micromoles_liter:

    ############################################
    #                                          #
    # Retrieve initialization paramters from 
    #   various external files
    ### EPIC Dictionary definitions for WPAK data ###
    # If these variables are not defined, no data will be archived into the nc file for that parameter.
    EPIC_VARS_dict = ConfigParserLocal.get_config('nut_uml_epickeys.json')

    ### expected nutrient parameters
    nut_params = ['Sil (uM)', 'PO4 (uM)', 'NH4 (uM)','NO2 (uM)', 'NO3 (uM)']
    data_params = ['PrDM Round','nb','cast']

    ### read in data file
    # from each line, look for expected values to be archived filling in missing
    # values with 1e35.  Build nc files as each cast cycles
    excelfiles = args.inputpath
    print "Reading file {0}".format(excelfiles)
    W = readXlsx(excelfiles, sheet=args.sheet, header=True)
    data = collections.OrderedDict()
    for index, row in enumerate(W):
        if index==0:
            print row
        else:
            try:
                data[row['cast']+'_'+row['nb']] = row
            except:
                print "No btl log for {0}:{1}".format(row['Cast'],row['Niskin'])

    # cycle through each row in the ingested excel file.
    # The relationship between the bottle/niskin number of the current line compared to the 
    #   previous line dictates the if switch.  As long as the bottle number continues to increas
    #   data will be read and added to the existing array.  If the number decreases, it is assumed
    #   the data is now affiliated with the next cast
    sil,po4,nh4,no2,no3,press,bottle,CruiseID = [],[],[],[],[],[],[],[]
    btl_num = 0
    for index,val in enumerate(data):
        if (int(data[val]['nb']) > btl_num):
            try:
                sil = sil + [round(float(data[val]['Sil (uM)']),3)]
            except:
                sil = sil + [1e35]
            try:
                po4 = po4 + [round(float(data[val]['PO4 (uM)']),3)]
            except:
                po4 = po4 + [1e35]
            try:
                nh4 = nh4 + [round(float(data[val]['NH4 (uM)']),3)]
            except:
                nh4 = nh4 + [1e35]
            try:
                no2 = no2 + [round(float(data[val]['NO2 (uM)']),3)]
            except:
                no2 = no2 + [1e35]
            try:
                no3 = no3 + [round(float(data[val]['NO3 (uM)']),3)]
            except:
                no3 = no3 + [1e35]
            btl_num=int(data[val]['nb'])
            bottle = bottle + [int(data[val]['nb'])]
            try:
                press = press + [int(data[val]['PrDM Round'])]
            except: #missing depth information from bottle record
                press = press + [1e35]
                
            cast = data[val]['cast']
            CruiseID = data[val]['CruiseID']
            dtime = nut2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                        isdatetime=True).get_EPIC_date()
            data_saved = False

        elif (int(data[val]['nb']) == btl_num) and data_saved:
            ###make netcdf
            print "Working on single bottle Cast {0}-{1} : {2}".format(cast, CruiseID,dtime)

            #cycle through and build data arrays
            #create a "data_dic" and associate the data with an epic key
            #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
            # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
            # if it is below but not the epic dic, it will not make it to the nc file
            data_dic = {}
            data_dic['NH4_189'] = np.array(nh4)
            data_dic['NO3_182'] = np.array(no3)
            data_dic['SI_188'] = np.array(sil)
            data_dic['PO4_186'] = np.array(po4)
            data_dic['NO2_184'] = np.array(no2)
            data_dic['BTL_103'] = np.array(bottle)
                    
            #PMEL EPIC Conventions
            ncinstance = nut2nc.CTDbtl_NC(savefile=(args.output + CruiseID + cast.lower().replace('ctd', 'c') + '_nut.nc'))
            ncinstance.file_create()
            ncinstance.sbeglobal_atts(raw_data_file=excelfiles.split('/')[-1]) # 
            ncinstance.dimension_init(depth_len=len(press))
            ncinstance.variable_init(EPIC_VARS_dict)
            ncinstance.add_data(EPIC_VARS_dict,data_dic)
            ncinstance.add_coord_data(depth=press, time1=dtime[0], time2=dtime[1])
            ncinstance.close()

    
            #reinit array
            sil,po4,nh4,no2,no3,press,bottle = [],[],[],[],[],[],[]

            try:
                sil = sil + [round(float(data[val]['Sil (uM)']),3)]
            except:
                sil = sil + [1e35]
            try:
                po4 = po4 + [round(float(data[val]['PO4 (uM)']),3)]
            except:
                po4 = po4 + [1e35]
            try:
                nh4 = nh4 + [round(float(data[val]['NH4 (uM)']),3)]
            except:
                nh4 = nh4 + [1e35]
            try:
                no2 = no2 + [round(float(data[val]['NO2 (uM)']),3)]
            except:
                no2 = no2 + [1e35]
            try:
                no3 = no3 + [round(float(data[val]['NO3 (uM)']),3)]
            except:
                no3 = no3 + [1e35]
            try:
                press = press + [int(data[val]['PrDM Round'])]
            except: #missing depth information from bottle record
                press = press + [1e35]


            btl_num=int(data[val]['nb'])    
            bottle = bottle + [int(data[val]['nb'])]
            cast = data[val]['cast']
            CruiseID = data[val]['CruiseID']
            dtime = nut2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                        isdatetime=True).get_EPIC_date()  
            data_saved = False
        
        else:
            ###make netcdf
            print "Working on Cast {0}-{1} : {2}".format(cast, CruiseID,dtime)

            #cycle through and build data arrays
            #create a "data_dic" and associate the data with an epic key
            #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
            # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
            # if it is below but not the epic dic, it will not make it to the nc file
            data_dic = {}
            data_dic['NH4_189'] = np.array(nh4)
            data_dic['NO3_182'] = np.array(no3)
            data_dic['SI_188'] = np.array(sil)
            data_dic['PO4_186'] = np.array(po4)
            data_dic['NO2_184'] = np.array(no2)
            data_dic['BTL_103'] = np.array(bottle)
                    
            #PMEL EPIC Conventions
            ncinstance = nut2nc.CTDbtl_NC(savefile=(args.output + CruiseID + cast.lower().replace('ctd', 'c') + '_nut.nc'))
            ncinstance.file_create()
            ncinstance.sbeglobal_atts(raw_data_file=excelfiles.split('/')[-1]) # 
            ncinstance.dimension_init(depth_len=len(press))
            ncinstance.variable_init(EPIC_VARS_dict)
            ncinstance.add_data(EPIC_VARS_dict,data_dic)
            ncinstance.add_coord_data(depth=press, time1=dtime[0], time2=dtime[1])
            ncinstance.close()

    
            #reinit array
            sil,po4,nh4,no2,no3,press,bottle = [],[],[],[],[],[],[]

            try:
                sil = sil + [round(float(data[val]['Sil (uM)']),3)]
            except:
                sil = sil + [1e35]
            try:
                po4 = po4 + [round(float(data[val]['PO4 (uM)']),3)]
            except:
                po4 = po4 + [1e35]
            try:
                nh4 = nh4 + [round(float(data[val]['NH4 (uM)']),3)]
            except:
                nh4 = nh4 + [1e35]
            try:
                no2 = no2 + [round(float(data[val]['NO2 (uM)']),3)]
            except:
                no2 = no2 + [1e35]
            try:
                no3 = no3 + [round(float(data[val]['NO3 (uM)']),3)]
            except:
                no3 = no3 + [1e35]
            try:
                press = press + [int(data[val]['PrDM Round'])]
            except: #missing depth information from bottle record
                press = press + [1e35]


            btl_num=int(data[val]['nb'])    
            bottle = bottle + [int(data[val]['nb'])]
            cast = data[val]['cast']
            CruiseID = data[val]['CruiseID']
            dtime = nut2nc.DataTimes(xldate_as_datetime(float(data[val]['date'])+float(data[val]['time']),args.datemode),
                                        isdatetime=True).get_EPIC_date()            
            data_saved = True


if args.micromoles_kilogram:
    print "Work in progress.  Need to have a density conversion"

    ############################################
    #                                          #
    # Retrieve initialization paramters from 
    #   various external files
    ### EPIC Dictionary definitions for WPAK data ###
    # If these variables are not defined, no data will be archived into the nc file for that parameter.

    EPIC_VARS_dict = ConfigParserLocal.get_config('nut_umkg_epickeys.json')


#!/usr/bin/env python

"""
DiscreteVars2DB.py

Takes a nutrient data file (from Eric W.) and inputs it into a database

Two database tables will be updated with each record:
    dvars_nutrients will get a sample id (cruise_cast_niskin) and the concentration of each nutrient
    dvars_cruiseid_info will get the niskin_no, cast, and cruise id

    TODO:    There is not a current method for multiple samples taken from the same niskin on the same cast
"""

#System Stack
import datetime
import argparse
import csv
import collections

#DB Stack
import pymysql

#User Packages
import utilities.ConfigParserLocal as ConfigParserLocal


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 05, 10)
__modified__ = datetime.datetime(2016, 05, 10)
__version__  = "0.1.0"
__status__   = "Development"

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB(host, user, password, database, port=3306):
    # Open database connection
    try:
        db = pymysql.connect(host, user, password, database, port)
    except:
        print "db error"
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)
    
def add_nutrients(db, cursor, table, unique_id, data_dic,conv_temp=False):

    if not conv_temp:
      sql = ("INSERT INTO `%s`(cruise_cast_niskin, no3_uml, no2_uml, nh4_uml, po4_uml, sil_uml ) "
              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s'"
              ")" % (table,unique_id,data_dic['NO3 (uM)'],data_dic['NO2 (uM)'],\
                  data_dic['NH4 (uM)'],data_dic['PO4 (uM)'],data_dic['Sil (uM)']))
    else:
      sql = ("INSERT INTO `%s`(cruise_cast_niskin, no3_uml, no2_uml, nh4_uml, po4_uml, sil_uml, uml2umkg_temp ) "
              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s'"
              ")" % (table,unique_id,data_dic['NO3 (uM)'],data_dic['NO2 (uM)'],\
                  data_dic['NH4 (uM)'],data_dic['PO4 (uM)'],data_dic['Sil (uM)'],data_dic['Temp']))
    #print sql
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       print "add failed"
       db.rollback()    

def add_meta_info(db, cursor, table, unique_id, cruiseid, cast_no, niskin_no, press_depth, nominal_depth=False):

    if not nominal_depth:
      sql = ("INSERT INTO `{0}`(cruise_cast_niskin, CruiseID, ConsecutiveCastNo, NiskinBottleNo, NiskinDepth_db ) "
            "VALUES ('{1}', '{2}', '{3}', '{4:d}', '{5:4.3f}')".format(table,unique_id,cruiseid,cast_no,niskin_no,press_depth))
    else:
      sql = ("INSERT INTO `{0}`(cruise_cast_niskin, CruiseID, ConsecutiveCastNo, NiskinBottleNo, NiskinNominalDepth_m ) "
            "VALUES ('{1}', '{2}', '{3}', '{4:d}', '{5:4.3f}')".format(table,unique_id,cruiseid,cast_no,niskin_no,press_depth))


    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       print "add failed"
       db.rollback()    

def add_bottledata(db, cursor, table, unique_id, pritemp, sectemp, prisal, secsal, prioxy, secoxy, chl, turb, trans, attn, par):

    sql = ("INSERT INTO `{0}`(cruise_cast_niskin, pri_salinitiy_psu, sec_salinity_psu, pri_temp_c, sec_temp_c, "
          "pri_oxy_conc, sec_oxy_conc, chl_a, turbidity, transmission, attenuation, PAR ) "
          "VALUES ('{1}', {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12})".format(
            table,unique_id, pritemp, sectemp, prisal, secsal, \
            prioxy, secoxy, chl, turb, trans, attn, par))
    #print sql
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       print "add failed"
       db.rollback()    

def close_DB(db):
    # disconnect from server
    db.close()

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
    
"""-------------------------------- Main ------------------------------------------"""

parser = argparse.ArgumentParser(description='Ingest various text files into database hosted on Pavlof')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('CruiseID', metavar='CruiseID', type=str,
               help='cruiseid, lowercase and no hyphens or spaces (eg dy1508)')
parser.add_argument("-nut",'--nutrients', action="store_true", help='flag to add nutrient files to db')
parser.add_argument("-btl",'--bottle', action="store_true", help='flag to add bottle files to db')
parser.add_argument("-oxy",'--oxygen', action="store_true", help='flag to add oxygen files to db')
parser.add_argument("-salt",'--salinity', action="store_true", help='flag to add salinity files to db')

args = parser.parse_args()

#get database configuration settings
db_config = ConfigParserLocal.get_config('../../db_connection_config_files/db_config_cruises.pyini')

(db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'], db_config['port'])
print db_config

if args.nutrients:
  #open and read selected nutrient file into a dictionary with each row being an entry
  with open(args.DataPath,'rU') as csvfile:
  	reader = csv.DictReader(csvfile, delimiter='\t')

  	count = 0
  	result = {}
  	for row in reader:
  		result[count] = {}
  		for column, value in row.iteritems():
  			result[count].update({column: value})
  		count +=1

  for key in result.keys():
      try:
          unique_id = "_".join((args.CruiseID,result[key]['Cast'],result[key]['Niskin']))
      except KeyError:
          try:
              unique_id = "_".join((args.CruiseID,result[key]['cast'],result[key]['BTL_103']))
          except:
              print "Expecting 'Cast' and/or 'Niskin' as column names.  Please check column names and run again."
      print unique_id
      
      if not 'Temp' in result[key].keys():
        add_nutrients(db, cursor, 'dvars_nutrients', unique_id, result[key],conv_temp=False)
      else:
        add_nutrients(db, cursor, 'dvars_nutrients', unique_id, result[key],conv_temp=True)

if args.bottle:
    # from each line, look for expected values to be archived filling in missing
    # values with 1e35.  Build nc files as each cast cycles
    print "Reading file {0}".format(args.DataPath)
    W = readXlsx(args.DataPath, sheet=1, header=True)
    data = collections.OrderedDict()
    for index, row in enumerate(W):
        if index==0:
            print row
        else:
            try:
              unique_id = "_".join((args.CruiseID,row['cast'].lower().split('ctd')[1], row['nb']))
            except IndexError:
              break
            #cycle through accepted headers to get vars and replace with NULL if not available
            for vname in ['Sal00','Sal11','Sigma-t00','Density11','Sbeox0Mm/Kg','Sbeox0PS','Sbeox1Mm/Kg','Sbeox1PS','T090C','T190C','TurbWETntu0','FlECO-AFL','Par','CStarTr0','CStarAt0']:
              try:
                row[vname] = round(float(row[vname]),4)
              except:
                row[vname] = 'NULL'
            try:
              add_meta_info(db, cursor, 'dvars_btl_meta', unique_id, args.CruiseID, row['cast'].lower().split('ctd')[1], int(row['nb']), float(row['PrDM']), nominal_depth=False)
            except KeyError:
              print "this cruise doesn't have PrDM - add it manually to excel file?"
            add_bottledata(db, cursor, 'dvars_bottle', unique_id, row['T090C'],row['T190C'], row['Sal00'], row['Sal11'], row['Sbeox0Mm/Kg'], row['Sbeox1Mm/Kg'], row['FlECO-AFL'], row['TurbWETntu0'], row['CStarTr0'],row['CStarAt0'], row['Par'] )
close_DB(db)

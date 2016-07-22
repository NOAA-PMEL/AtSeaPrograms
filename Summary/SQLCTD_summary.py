#!/usr/bin/env

"""
 SQL2meta_ctd.py
 
 Retrieve specific characteristics from CTD cruise database (CTD_MetaInformation)

 Using Anaconda packaged Python 
"""

# System Stack
import datetime
import pymysql
import argparse

# Science Stack
import numpy as np

# User Stack
import utilities.ConfigParserLocal as ConfigParserLocal

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2015, 12, 10)
__modified__ = datetime.datetime(2015, 12, 10)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'MetaInformation', 'Cruise', 'MySQL'

"""--------------------------------SQL Init----------------------------------------"""

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB(host, user, password, database):
    # Open database connection
    try:
        db = pymysql.connect(host, user, password, database)
    except:
        print "db error"
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)
    
    
       
def count_cruise(db, cursor, table, year, month, day):
    sql = ("SELECT count(*) from `{0}` as castnum WHERE `GMTYear` = '{1}' AND `GMTMonth` = '{2}' AND `GMTDay` = '{3}'" ).format(table, year, month, day)

    result_dic = {}
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Get column names
        rowid = {}
        counter = 0
        for i in cursor.description:
            rowid[i[0]] = counter
            counter = counter +1 
        #print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic['value'] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
        return (result_dic)
    except:
        print "Error: unable to fecth data"

"""------------------------   Main   Modules   ----------------------------------------"""

parser = argparse.ArgumentParser(description='MySql Cruise Summary')
parser.add_argument('table', metavar='table', type=str, help='database tablename')
parser.add_argument('year', metavar='year', type=int, help='year to run')
parser.add_argument('nyear', metavar='nyear', type=int, help='number of years to run')

args = parser.parse_args()

db_config = ConfigParserLocal.get_config('db_config_cruise_data.pyini')

(db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'])
   
startday = datetime.datetime(args.year,1,1,0,0,0)
num_days = 365 * args.nyear
print "date, castnum\n"
for day in startday + np.arange(num_days) * datetime.timedelta(1):
    
    data = count_cruise(db, cursor, args.table, str(day.year), day.strftime('%b') , str(day.day) )
    print ("{0}, {1}").format(day, int(data.values()[0].values()[0]) )


db.close()


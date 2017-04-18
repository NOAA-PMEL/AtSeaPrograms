#!/usr/bin/env python

"""
PostCruiseMetaDBadd.py

Adds MetaInformation from cruisecastlogs db to netcdf files

Input - CruiseID
Output - png map and kml map

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import sys
import os

#DB Stack
import pymysql

#Science Stack
from netCDF4 import Dataset
import numpy as np

#User Packages
from io_utils import ConfigParserLocal


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'MetaInformation', 'Cruise', 'MySQL'

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB(host, user, password, database, port):
    # Open database connection
    try:
        db = pymysql.connect(host, user, password, database, port)
    except:
        print "db error"
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)    
    

def close_DB(db):
    # disconnect from server
    db.close()
    
def read_data(db, cursor, table, cruiseID, legNO=''):
    """Currently returns all entries from selected table for selected cruise"""
    
    sql = "SELECT * from `%s` WHERE `cruiseID`='%s' and `Project_Leg`='%s'" % (table, cruiseID, legNO)

    print sql
    
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
            result_dic[row['id']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
        return (result_dic)
    except:
        print "Error: unable to fecth data"

"""------------------------------------- Main -----------------------------------------"""

def AddMeta_fromDB(user_in, user_out):
    
    ### hack for three leter healy cruises with 'L' in the label
    if 'HLY' in user_in.lower():
        cruiseID = user_in.split('/')[-3]
        leg = cruiseID.lower().split('Z')
        print "leg is {0}, cruiseid is {0}".format(leg, cruiseID)
    else:
        cruiseID = user_in.split('/')[-3]
        leg = cruiseID.lower().split('l')
    if len(leg) == 1:
        cruiseID = leg[0]
        leg = ''
    else:
        cruiseID = leg[0]
        leg = 'L' + leg[-1]
        
    table='cruisecastlogs'
    db_config = ConfigParserLocal.get_config('config_files/db_config_cruises.yaml')
    print db_config
    if not leg:
        (db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'], db_config['port'])
        data = read_data(db, cursor, table, cruiseID)
        close_DB(db)
    else:
        (db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'], db_config['port'])
        data = read_data(db, cursor, table, cruiseID, legNO=leg)
        cruiseID = cruiseID + leg
        close_DB(db)
    
    print ("Adding Meta Information from {0}").format(cruiseID)
    ## exit if db is empty
    if (len(data.keys()) == 0):
        print ("Sorry, this cruise is either not in the database or was entered "
                "incorrectly.  Please start the program and try again.")
        sys.exit()


    #epic flavored nc files
    nc_path = user_out
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]

    for ncfile in nc_path:
        
        ncfid = Dataset(ncfile,'a')
        if not leg:
            castxxx = ncfile.lower().split(cruiseID.lower())[-1].split('_')[0][1:]
        else:
            castxxx = ncfile.lower().split(cruiseID.lower())[-1].split('_')[0][1:]

        print 'castxxx = ' + castxxx
        castID = 'CTD' + castxxx
        print castID
        
        castmeta = [x for x in data.itervalues() if x['ConsecutiveCastNo'] == castID][0]
        ncfid.setncattr('CAST',castxxx)
        ncfid.setncattr('WATER_MASS',castmeta['WaterMassCode'])
        ncfid.setncattr('BAROMETER',int(castmeta['Pressure']))
        ncfid.setncattr('WIND_DIR',int(castmeta['WindDir']))
        ncfid.setncattr('WIND_SPEED',int(castmeta['WindSpd']))
        ncfid.setncattr('AIR_TEMP',float(castmeta['DryBulb']))
        ncfid.setncattr('WATER_DEPTH',int(castmeta['BottomDepth']))
        ncfid.setncattr('STATION_NAME',castmeta['StationNameID'])

        ### look for existing lat/lon and update if missing
        if (ncfid.variables['lat'][:] == -999.9) or (ncfid.variables['lat'][:] == -999.9) or np.isnan(ncfid.variables['lat'][:]):
            ncfid.variables['lat'][:] = castmeta['LatitudeDeg'] + castmeta['LatitudeMin'] / 60.
            ncfid.variables['lon'][:] = castmeta['LongitudeDeg'] + castmeta['LongitudeMin'] / 60.

        ncfid.close()

    
    processing_complete = True
    return processing_complete
    
if __name__ == '__main__':

    user_in = raw_input("Please enter the abs path to the .nc file: or \n path, file1, file2: ")
    user_out = user_in
    AddMeta_fromDB(user_in, user_out)
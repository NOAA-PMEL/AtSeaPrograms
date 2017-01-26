#!/usr/bin/env

"""
IconicLinesCruiseMapDB.py

Generates a cruise map of CTD locations from CruiseLog Database and 
Mooring Locations for all available information

Output - png map 

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import sys

#DB Stack
import pymysql

#Science Stack
import numpy as np
from netCDF4 import Dataset

#Visual Packages
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid
import brewer2mpl

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Cruise Map', 'Cruise', 'MySQL', 'All data'

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB():
    # Open database connection
    db = pymysql.connect("localhost","pythonuser","e43mqS4fusEaGJLE","EcoFOCI_Data", port=8889 )

    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)
    

def close_DB(db):
    # disconnect from server
    db.close()
    
def read_data(db, cursor, table):
    """Currently returns all entries from selected table for all information"""
    
    sql = "SELECT * from `{0}` ".format(table)
 
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

"""------------------------------------- MAPS -----------------------------------------"""

def etopo5_data(filein='/Users/bell/in_and_outbox/Ongoing_Analysis/MapGrids/etopo5.nc'):
    """ read in etopo5 topography/bathymetry. """

    etopodata = Dataset(filein)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)

def sqldate2GEdate(castdate,casttime):

    try:
        outstr = datetime.datetime.strptime((castdate + ' ' + casttime), '%Y-%b-%d %H:%M').strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        outstr = '0000-00-00T00:00:00Z'
        

    return outstr

def convert_timedelta(duration):
    """converts date.timedelta object into hours and minutes string format HH:MM"""
    seconds = duration.seconds
    hours = seconds // 3600
    if hours < 10:
        hours = '0'+str(hours)
    else:
        hours = str(hours)
    minutes = (seconds % 3600) // 60
    if minutes < 10:
        minutes = '0'+str(minutes)
    else:
        minutes = str(minutes)    
    return hours+':'+minutes
        

"""------------------------------------- Main -----------------------------------------"""

(topoin, elats, elons) = etopo5_data()

   
table='all_iconic_lines'

# ctd db
(db,cursor) = connect_to_DB()
data = read_data(db, cursor, table)
close_DB(db)


## get relevant data for plotting
cast_name = [data[a_ind]['StationName'] for a_ind in data.keys()]
cast_lat = np.array([float(data[a_ind]['LatitudeDegree']) + float(data[a_ind]['LatitudeMinute'])/60.0 for a_ind in data.keys()])
cast_lon = np.array([float(data[a_ind]['LongitudeDegree']) + float(data[a_ind]['LongitudeMinute'])/60.0 for a_ind in data.keys()])


### Basemap Visualization

## plot
fig = plt.figure()
ax = plt.subplot(111)

m = Basemap(resolution='i',projection='merc', llcrnrlat=cast_lat.min()-2.5, \
    urcrnrlat=cast_lat.max()+2.5,llcrnrlon=-1*(cast_lon.max()+5),urcrnrlon=-1*(cast_lon.min()-5),\
    lat_ts=45)
      
elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)


#colorbrewer scheme
bmap = brewer2mpl.get_map('Greys','Sequential',9,reverse=True)

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=[-2000,-1000, -500,-150, -100, -50], linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=[-2000,-1000, -500,-150, -100, -50, ], colors=bmap.hex_colors[:-2], alpha=.75, extend='both') 
plt.clabel(CS_l, inline=1, fontsize=6, fmt='%1.0f')
#plot points
## Cruise Data
x_cast, y_cast = m(-1. * cast_lon,cast_lat)


m.scatter(x_cast,y_cast,10,marker='+',color='r', alpha=.75)

#add station labels
for i,v in enumerate(x_cast):
    plt.text(x_cast[i]+500,y_cast[i]-10000,cast_name[i], fontsize=2 ) 


#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(46,80,4.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(-180,-140,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )

plt.savefig('images/IconicLines_map.png', bbox_inches='tight', dpi = (600))

#!/usr/bin/env python

"""
IBCAO_Maps_stations.py

Topo Maps for Alaska/Arctic from IBCAO


Using Anaconda packaged Python 
"""

#System Stack
import datetime

#Science Stack
import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import griddata

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
__keywords__ = 'CTD', 'Cruise Map', 'Cruise', 'MySQL'


"""------------------------------------- MAPS -----------------------------------------"""


def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = 'data/etopo5.nc'
    etopodata = Dataset(file)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)
    
def IBCAO_data():
    """ read in IBCAO topography/bathymetry. """
    file_in = '/Users/bell/Data_Local/MapGrids/ARDEMv2.0.nc'
    IBCAOtopodata = Dataset(file_in)
    
    topoin = IBCAOtopodata.variables['z'][:]
    lons = IBCAOtopodata.variables['lon'][:] #degrees east
    lats = IBCAOtopodata.variables['lat'][:]
    IBCAOtopodata.close()
    
    #topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx
    
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

"""------------------------------------------------------------------------------------"""

# get excel file
W = readXlsx('/Users/bell/in_and_outbox/2016/stabeno/mar/arctic_maps/Arctic Mooring Locations_2016-7.xlsx', sheet=2, header=True)

no_ice = True
# read csv files with ice extent
if not no_ice:
    my_data = np.genfromtxt('/Users/bell/Data_Local/from_sigrid/Sep01_y2008to2013.asc', delimiter='')            


#IBCAO contour data 

(topoin, elats, elons) = IBCAO_data()

fig = plt.figure()
ax = plt.subplot(111)
#m = Basemap(resolution='i',projection='merc', llcrnrlat=64, \
#    urcrnrlat=77,llcrnrlon=180,urcrnrlon=215,lat_ts=45)
m = Basemap(resolution='i',projection='stere',width=1500000, height=1710000, lat_0=68,lon_0=191)
            
elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)

#colorbrewer scheme
bmap = brewer2mpl.get_map('Greys','Sequential',9,reverse=True)

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=[-2000,-1000, -600, -500,-200, -100, -50], linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=[-2000,-1000,-600, -500,-200, -100, -50, ], colors=bmap.hex_colors[2:], extend='both', alpha=.75) 
plt.clabel(CS_l, inline=1, fontsize=6, fmt='%1.0f')

#ice extent
if not no_ice:
    bmap = brewer2mpl.get_map('Blues','Sequential',7,reverse=True)
    zi = griddata((my_data[:,1],my_data[:,0]),my_data[:,2],(elons, elats), method='cubic')
    CS_ice = m.contour(ex,ey,zi, levels=[25,50,75,90,100], linestyle='--', linewidths=2, colors=bmap.hex_colors, alpha=.75) 
    plt.clabel(CS_ice, inline=1, fontsize=10, fmt='%1.0f')


#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(56,80,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(100,300,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

### data plot
# only lines with two lats/lons are transects, others are station points
for index, row in enumerate(W):
    if index <=1:
        continue

    try:
        if 'Berchok' == row['POC']:
            lon_s = float(row['Longitude'])
            lat_s = float(row['Latitude'])
            print ("Mooring Site: {0}").format(row['Mooring Name'])
            x, y = m(lon_s * -1., lat_s)
            m.plot(x, y, 'o', markersize=6, color='k', alpha=0.75)
        elif 'Melling' == row['POC']:
            lon_s = float(row['Longitude'])
            lat_s = float(row['Latitude'])
            print ("Mooring Site: {0}").format(row['Mooring Name'])
            x, y = m(lon_s * -1., lat_s)
            m.plot(x, y, 'o', markersize=6, color='b', alpha=0.75)
        else:
            lon_s = float(row['Longitude'])
            lat_s = float(row['Latitude'])
            print ("Mooring Site: {0}").format(row['Mooring Name'])
            x, y = m(lon_s * -1., lat_s)
            m.plot(x, y, 'o', markersize=6, color='r', alpha=0.75)
    except:
        print ("Skipping Mooring Site: {0}").format(row['Mooring Name'])


DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )

plt.savefig('IBCAO_Chuckchi_2016_2017.png', bbox_inches='tight', dpi = (300))
plt.close()


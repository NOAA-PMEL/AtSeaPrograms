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
        

"""------------------------------------------------------------------------------------"""

#IBCAO contour data 

(topoin, elats, elons) = IBCAO_data()

fig = plt.figure()
ax = plt.subplot(111)
#m = Basemap(resolution='i',projection='merc', llcrnrlat=64, \
#    urcrnrlat=77,llcrnrlon=180,urcrnrlon=215,lat_ts=45)
m = Basemap(resolution='i',projection='stere',width=1000000, height=1210000, lat_0=70,lon_0=191)
            
elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)

#colorbrewer scheme
bmap = brewer2mpl.get_map('Greys','Sequential',9,reverse=True)

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=[-2000,-1000, -600, -500,-150, -100, -50], linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=[-2000,-1000,-600, -500,-150, -100, -50, ], colors=bmap.hex_colors[2:], extend='both', alpha=.75) 
plt.clabel(CS_l, inline=1, fontsize=6, fmt='%1.0f')

###Mooring Locations

Chukchi_Moorings_lats = [70.8307,71.2293,71.8248,71.0464,\
                         71.2107,71.7767,72.4246,72.5830,72.4579]
Chukchi_Moorings_lons = [-163.1223,-164.2135,-165.9752,-160.5149,\
                         -158.0022,-161.8790,-161.6207,-161.2052,-156.5654]

Trans15 = {'u': 1, 'v':1 }
###

#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(62,85,4.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(150,235,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

x, y = m(Chukchi_Moorings_lons, Chukchi_Moorings_lats)
m.plot(x, y, '.', markersize=8, linewidth=10, color='r')


DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )

plt.savefig('IBCAO_Chuckchi_ALL_zoom.png', bbox_inches='tight', dpi = (300))
plt.close()


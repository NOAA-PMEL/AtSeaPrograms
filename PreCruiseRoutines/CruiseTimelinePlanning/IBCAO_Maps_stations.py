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
m = Basemap(resolution='i',projection='stere',width=2000000, height=2420000, lat_0=70,lon_0=191)
            
elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)

#colorbrewer scheme
bmap = brewer2mpl.get_map('Greys','Sequential',9,reverse=True)

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=[-2000,-1000, -600, -500,-150, -100, -50], linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=[-2000,-1000,-600, -500,-150, -100, -50, ], colors=bmap.hex_colors[2:], extend='both', alpha=.75) 
plt.clabel(CS_l, inline=1, fontsize=6, fmt='%1.0f')

###Mooring Locations
AQ1401_lats = [70.8352,70.84,70.83068333,71.22,71.22963333,71.22925,71.04066667,\
                71.04023333,71.04348333,71.21066667,71.20661667,71.77416667,71.77666667,\
                72.42098333,72.42458333,72.58633333,72.583,72.583,72.45788333,72.44955]
AQ1401_lons = [163.1152667,163.1223333,163.1189833,164.2396333,164.2134833,164.24565,\
                160.5166333,160.4954167,160.5050167,158.0021667,158.0016333,161.8643333,\
                161.879,161.6305833,161.6206667,161.2148333,161.226,161.2051667,156.5653667,\
                156.6018333]
AQ1401_lons = np.array(AQ1401_lons) * -1.
Other_lats = [75,71.6,68.0316667,71.395,62.1928333,78,75,77,74.5]
Other_lons = [168,161.5,168.838333,152.05,174.67566667,150,150,140,140]
Other_lons = np.array(Other_lons) * -1.
Mid_lats = [65.9005,65.7796667,66.3256667]
Mid_lons = [169.4288333,168.575,168.967]
Mid_lons = np.array(Mid_lons) * -1.

PAM_Moorings_lats = [54.42828,56.87112,57.67140,57.88235,59.24293,59.91315,62.18987,\
                    61.58618,63.39978,72.44955,71.03725,71.78167,72.58005,72.42793,\
                    71.68828,71.75083,71.55313,71.20668,71.83128,71.21453,70.82272,\
                    69.31735,67.12355,64.84863,67.90793,65.78167,66.32667,65.78000]
PAM_Moorings_lons = [-165.26960,-164.05475,-164.71933,-168.87902,-169.41373,-171.70895,\
                -174.68893,-171.32697,-166.24072,-156.60183,-160.50607,-161.85838,-161.21792,-161.62877,\
                -153.17793,-154.46520,-155.53155,-158.01407,-166.07838,-164.23825,-163.13928,-167.62985,\
                -168.60443,-168.39007,-168.20217,-168.56667,-168.95167,-168.26333]
###

#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(62,85,4.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(150,235,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

x, y = m(PAM_Moorings_lons, PAM_Moorings_lats)
m.plot(x, y, '.', markersize=8, linewidth=10, color='r')

"""
x, y = m(AQ1401_lons, AQ1401_lats)
m.plot(x, y, '.', markersize=8, linewidth=10, color='b')
x, y = m(Other_lons, Other_lats)
m.plot(x, y, '.', markersize=8, linewidth=10, color='b')
x, y = m(Mid_lons, Mid_lats)
m.plot(x, y, '.', markersize=8, linewidth=10, color='b')
"""
DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )

plt.savefig('IBCAO_Chuckchi_AW14.png', bbox_inches='tight', dpi = (300))
plt.close()


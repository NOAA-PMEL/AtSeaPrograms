#!/usr/bin/env python

"""
plot_latlon_csv.py

plot a csv file of latitude and longitudes

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import argparse

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

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = '/Users/bell/Programs/Python/AtSeaPrograms/data/etopo5.nc'
    etopodata = Dataset(file)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)

"""------------------------------------------------------------------------------------"""

parser = argparse.ArgumentParser(description='Plot Arctic/Bering CSV lat/lons')
parser.add_argument('DataPath', metavar='DataPath', type=str,help='full path to .csv file')
parser.add_argument('OutPath', metavar='OutPath', type=str,help='full path to save location')
          
args = parser.parse_args()

###
#read in csv data

fh = open(args.DataPath, 'r')
csv_lats, csv_lons = [], []
for line in fh:
    csv_lats.append(float(line.strip().split(',')[0].strip()))
    csv_lons.append(float(line.strip().split(',')[1].strip()))
###
(topoin, elats, elons) = etopo5_data()
#(topoin, elats, elons) = IBCAO_data()

fig = plt.figure()
ax = plt.subplot(111)
#m = Basemap(resolution='i',projection='merc', llcrnrlat=64, \
#    urcrnrlat=77,llcrnrlon=180,urcrnrlon=215,lat_ts=45)
m = Basemap(resolution='i',projection='stere',width=2000000, height=2000000, lat_0=70,lon_0=191)
            
elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)

#colorbrewer scheme
bmap = brewer2mpl.get_map('Greys','Sequential',9,reverse=True)

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=[-2000,-1000, -600, -500,-150, -100, -50], linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=[-2000,-1000,-600, -500,-150, -100, -50, ], colors=bmap.hex_colors[2:], extend='both', alpha=.75) 
plt.clabel(CS_l, inline=1, fontsize=6, fmt='%1.0f')

###Locations
csv_lons = np.array(csv_lons) * -1.

###

#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(40,85,4.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(150,235,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

x, y = m(csv_lons, csv_lats)
m.plot(x, y, '.', markersize=8, linewidth=10, color='r')


DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )

plt.savefig(args.OutPath, bbox_inches='tight', dpi = (300))
plt.close()


#!/usr/bin/env

"""
 Background:
 --------
 
 
 Purpose:
 --------
 create csv of information for 70m isobar casts for each cruise
 
 
 
 Usage:
 ------
 Assumes data is in NetCDF format with a 'Water_Depth' global attribute
 
 Original code reference:
 ------------------------

 Built using Anaconda packaged Python:


"""
# System Packages
import datetime, os, sys
import math

# Scientific Packages
from netCDF4 import Dataset
import numpy as np

# Plotting Stack
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib.pyplot as plt


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.1.0"
__status__   = "Development"

"""----------------------Pandas Data Frame---------------------------------------------"""

class SeventyMeterIso(object):
    def __init__(self):
        self.cruiseID = {}
        
        
    def add_info(self, castID, btm_depth=None, latitude=None, longitude=None, file_in=None, depth_data=None, data=None):
        self.cruiseID[castID] = {}
        self.cruiseID[castID]['btm_depth'] = btm_depth
        self.cruiseID[castID]['latitude'] = latitude
        self.cruiseID[castID]['longitude'] = longitude
        self.cruiseID[castID]['file'] = file_in
        self.cruiseID[castID]['depth_data'] = depth_data
        self.cruiseID[castID]['data'] = data

    def map2btm(self, castID):
        """
        extend depth_data to btm_depth linearly
        extend datato btm_depth as -42
        """
        number_added = len(np.arange(self.cruiseID[castID]['depth_data'][-1]+1,self.cruiseID[castID]['btm_depth'],1))
        self.cruiseID[castID]['depth_data'] = np.hstack((self.cruiseID[castID]['depth_data'],
                   np.arange(self.cruiseID[castID]['depth_data'][-1]+1,self.cruiseID[castID]['btm_depth'],1)))
        self.cruiseID[castID]['data'] = np.hstack((self.cruiseID[castID]['data'], np.zeros(number_added)-42.))
           
    def cruise_stats(self):
        
        self.cast70m_keys = []
        for i,j in enumerate(self.cruiseID.keys()):
            if self.cruiseID[j]['btm_depth'] > 60 and self.cruiseID[j]['btm_depth'] < 80:
                if not (self.cruiseID[j]['depth_data'][-1] > self.cruiseID[j]['btm_depth']):
                    self.cast70m_keys.append(j) #list of casts
        
        return( self.cast70m_keys, len(self.cast70m_keys) )
        
    def deepest_cast(self):
        self.deepest_water = 0
        for i,j in enumerate(self.cruiseID.keys()):
            #cruise stats provides a list of potential casts at the 70m isobath
            #try to determine the deepest point from metatag, qc for depths being greater than
            #posted
            if j in self.cast70m_keys and (self.cruiseID[j]['btm_depth'] > self.deepest_water):
                self.deepest_water = self.cruiseID[j]['btm_depth'] 
                
    def pad2deepest(self, castID):
        """extend all casts to the same length, maked sub_btm values = -999."""
        number_added = len(np.arange(self.cruiseID[castID]['depth_data'][-1]+1,self.deepest_water,1))
        self.cruiseID[castID]['depth_data'] = np.hstack((self.cruiseID[castID]['depth_data'],
                   np.arange(self.cruiseID[castID]['depth_data'][-1]+1,self.deepest_water,1)))
        self.cruiseID[castID]['data'] = np.hstack((self.cruiseID[castID]['data'], np.zeros(number_added) - 999.))   
        
    def distbtwncast(self):
        """Using haversine formula"""
        pass

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c

    return d                  
"""------------------------------Plotting----------------------------------------------"""

def plotsetup():
    ### PARAMETERS FOR MATPLOTLIB :
    """
    Parameters
    ----------
    TODO
    
    Returns
    -------
    TODO
              
    """
    mpl.rcParams['font.size'] = 12.
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['axes.labelsize'] = 12.
    mpl.rcParams['xtick.labelsize'] = 12.
    mpl.rcParams['ytick.labelsize'] = 12.    

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = '../data/etopo5.nc'
    etopodata = Dataset(file)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)
        
    
def grid_plot(lon,lat, topoin, etlats, etlons, llimx=-180.,\
                    ulimx=-130.,llimy=50.,ulimy=75.):
    """"
    Parameters
    ----------
            lat: array_like
                0->360 Prime to Prime or -180 -> 180 IDL -> IDL
    
    Returns
    -------
            figure and plot instances
              
    """
    
    fig1 = plt.figure(1)
    #Custom adjust of the subplots
    ax = plt.subplot(1,1,1)
    #Let's create a basemap of Alaska
    x1 = llimx
    x2 = ulimx
    y1 = llimy
    y2 = ulimy
 
    m = Basemap(resolution='i',projection='merc', llcrnrlat=y1,urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,lat_ts=((y1+y2)/2))
    x, y = m(lon,lat)
    ex, ey = m(etlons, etlats)
    #lonpt, latpt = m(x,y,inverse=True)

    m.drawcountries(linewidth=0.5)
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(y1,y2,5.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
    m.drawmeridians(np.arange(x1-20,x2,5.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
    m.fillcontinents(color='black')

    
    m.contour(ex,ey,topoin, levels=[ -70, -100, -200, -1000], linewidths=0.2)
    m.scatter(x,y,20,marker='+')

    
 
    f = plt.gcf()
    DefaultSize = f.get_size_inches()
    f.set_size_inches( (DefaultSize[0]*4, DefaultSize[1]*2) )

    return (fig1, plt)
    
    
def contour_plot( cruise_inst, levels='empty' ):
    ygrid = np.arange( 0,cruises[cruiseID_in].deepest_water,1 )
    xgrid, data = [], np.zeros( cruises[cruiseID_in].deepest_water )
    for cast_s in sorted(castIDon70):
        xgrid = np.hstack( (xgrid, np.int(cast_s.split('c')[-1]) ) )
        data  = np.vstack( (data, cruises[cruiseID_in].cruiseID[cast_s]['data']) )
    data = data[1:,:]

    #-999.represents below btm and -42 represents btwn btm and last cast depth
    if levels is 'empty':
        levels = np.hstack(([-1000,-990.,-40], np.arange(-4,10,1))) 
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    CS1 = plt.contourf(xgrid,ygrid,data.T, levels=levels[:3],colors=['k','r'])
    CS2 = plt.contour(xgrid,ygrid,data.T, levels=levels[3:])    
    ax.set_ylim(ax.get_ylim()[::-1]) #this reverses the yaxis (i.e. deep at the bottom)
    plt.xlabel('Cast Number')
    
    cbar = plt.colorbar(CS2)
    return(fig, ax)

def contour_plot_alongtrack( cruise_inst, distance, levels='empty' ):
    ygrid = np.arange( 0,cruises[cruiseID_in].deepest_water,1 )
    xgrid, data = distance, np.zeros( cruises[cruiseID_in].deepest_water )
    for cast_s in sorted(castIDon70):
        data  = np.vstack( (data, cruises[cruiseID_in].cruiseID[cast_s]['data']) )
    data = data[1:,:]

    #-999.represents below btm and -42 represents btwn btm and last cast depth
    if levels is 'empty':
        levels = np.hstack(([-1000,-990.,-40], np.arange(-4,10,1))) 
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    CS1 = plt.contourf(xgrid,ygrid,data.T, levels=levels[:3],colors=['k','r'])
    CS2 = plt.contour(xgrid,ygrid,data.T, levels=levels[3:])    
    ax.set_ylim(ax.get_ylim()[::-1]) #this reverses the yaxis (i.e. deep at the bottom)
    plt.xlabel('Along Track Km travelled')
    
    cbar = plt.colorbar(CS2)
    return(fig, ax)    
"""-----------------------------From Netcdf--------------------------------------------"""
def get_nc_data(fname):
    """ using netcdf4 to import data
    Usage
    -----
    >>>fname = ../data/test_ctd.nc
    >>> get_nc_data(fname)
    """
    f = Dataset(fname,'r')

    global_attrs = {}
    for i, v in enumerate(f.ncattrs()):
        global_attrs[v] = f.getncattr(v)
    

        
    #index may be 'dep', 'depth', or 'pres'
    try:
        cast = np.zeros( ( f.variables['dep'][:].shape[0],len(f.variables.keys()) ) ) 
    except KeyError:
        try: 
            cast = np.zeros( ( f.variables['depth'][:].shape[0],len(f.variables.keys()) ) )
        except KeyError:
            try:
                cast = np.zeros( ( f.variables['pres'][:].shape[0],len(f.variables.keys()) ) )
            except:
                print " ERROR: NetCDF vertical coordinate not recognized.  No dep, depth, or pres key in file \n"
                sys.exit(1)

    variable_names = {}            
    for j, v in enumerate( f.variables.keys() ): 
        try: #non coord dims have 4 axis
            cast[:,j] = f.variables[v][0,:,0,0]
            variable_names[v] = j
        except ValueError: #coord dims have only one axis
            cast[:,j] = f.variables[v][:]
            variable_names[v] = j
            
    return (global_attrs, variable_names, cast)

"""------------------------------------------------------------------------------------"""
def main():
    pass
    
cruise_in = raw_input("Please enter the abs path to the cruise of interest: ")
cruiseID_in = raw_input("Please enter ID of the cruise of interest: ")

cruises = {}
cruises[cruiseID_in] = SeventyMeterIso()

for files in os.listdir(cruise_in):
    
    if files.endswith('nc'):
        
        #print "Getting data from %s \n" % files
        (global_attrs, variable_names, cast) = get_nc_data(cruise_in + files)
 
        cruises[cruiseID_in].add_info(castID=files.strip('.nc'), file_in=(cruise_in + files),
                btm_depth=global_attrs['WATER_DEPTH'], data=cast[:,variable_names['T_28']],
                depth_data=cast[:,variable_names['dep']], latitude=cast[:,variable_names['lat']][0],
                longitude=cast[:,variable_names['lon']][0])

        #print "Calculaing cruise statistics \n"
        (castIDon70, numCasts) = cruises[cruiseID_in].cruise_stats()

        #print "Mapping to bottom depth \n"
        cruises[cruiseID_in].map2btm(castID=files.strip('.nc'))

""" determine distance between casts"""
all_lats = [-90]
all_lons = [0]
along_cruise_distance = []
for kid in castIDon70:
    all_lats = np.append(all_lats, cruises[cruiseID_in].cruiseID[kid]['latitude'])
    all_lons = np.append(all_lons, cruises[cruiseID_in].cruiseID[kid]['longitude'])
    along_cruise_distance = np.append(along_cruise_distance, 
        distance((all_lats[-2],all_lons[-2]),(all_lats[-1],all_lons[-1])))

#no value for first point 
along_cruise_distance[0] = 0. 

cruises[cruiseID_in].deepest_cast()
print "Mapping to deepest cast \n"
[cruises[cruiseID_in].pad2deepest(castID=ID) for ID in castIDon70]

clevels = np.hstack(([-1000.,-500, -40], np.arange(24,26,.1)))
fig1, ax = contour_plot_alongtrack(cruises[cruiseID_in], np.cumsum(along_cruise_distance))
plt.show(fig1)

#print map of casts used
print "Mapping to CTD locations \n"
(topoin, etlats, etlons) = etopo5_data()

fig2, plt = grid_plot(-1.*all_lons,all_lats, topoin, etlats, etlons)
plt.show(fig2)
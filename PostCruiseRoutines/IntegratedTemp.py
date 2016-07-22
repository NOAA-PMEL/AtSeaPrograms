#!/usr/bin/env python

"""
IntegratedTemp.py


Visually adjust Temp/Sal => DO and sigmaT
"""
#System Stack
import datetime
import os
import argparse

#Science Stack
from netCDF4 import Dataset
from netCDF4 import date2num
import seawater as sw
import numpy as np

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 9, 11)
__modified__ = datetime.datetime(2014, 9, 11)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'SeaWater', 'Cruise', 'derivations'

"""--------------------------------netcdf Routines---------------------------------------"""

def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def get_var_atts(nchandle, var_name):
    return nchandle.variables[var_name]

def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)

def repl_var(nchandle, var_name, val=1e35):
    if len(val) == 1:
        nchandle.variables[var_name][:] = np.ones_like(nchandle.variables[var_name][:]) * val
    else:
        nchandle.variables[var_name][:] = val
    return
    
"""--------------------------------EPIC Routines---------------------------------------"""

def EPICdate2udunits(time1, time2):
    """
    Inputs
    ------
          time1: array_like
                 True Julian day
          time2: array_like
                 Milliseconds from 0000 GMT
    Returns
    -------
          dictionary:
            'timeint': python serial time
            'interval_min': data interval in minutes
    
    Example
    -------
    Python uses days since 0001-01-01 and a gregorian calendar

      
    Reference
    ---------
    PMEL-EPIC Conventions (misprint) says 2400000
    http://www.epic.noaa.gov/epic/eps-manual/epslib_ch5.html#SEC57 says:
    May 23 1968 is 2440000 and July4, 1994 is 2449538
              
    """
    ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
    ref_time_epic = 2440000
    
    offset = ref_time_epic - ref_time_py
    
    try:
        pytime = [None] * len(time1)

        for i, val in enumerate(time1):
            pyday = time1[i] - offset 
            pyfrac = time2[i] / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
            pytime[i] = (pyday + pyfrac)
            
    except:
        pytime = []
    
        pyday = time1 - offset 
        pyfrac = time2 / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
        pytime = (pyday + pyfrac)
    
    return pytime

def pythondate2str(pdate):
    (year,month,day) = datetime.datetime.fromordinal(int(pdate)).strftime('%Y-%b-%d').split('-')
    delta_t = pdate - int(pdate)
    dhour = str(int(np.floor(24 * (delta_t))))
    dmin = str(int(np.floor(60 * ((24 * (delta_t)) - np.floor(24 * (delta_t))))))
    dsec = str(int(np.floor(60 * ((60 * ((24 * (delta_t)) - np.floor(24 * (delta_t)))) - \
                    np.floor(60 * ((24 * (delta_t)) - np.floor(24 * (delta_t))))))))
                    
    #add zeros to time
    if len(dhour) == 1:
        dhour = '0' + dhour
    if len(dmin) == 1:
        dmin = '0' + dmin
    if len(dsec) == 1:
        dsec = '0' + dsec
                
    return(year,month,day,dhour+':'+dmin+':00')  


"""------------------------------------- Main -----------------------------------------"""


parser = argparse.ArgumentParser(description='seawater recalculation of sigmat or oxygen')
parser.add_argument('DataPath', metavar='DataPath', type=str, help='path to .nc file')

args = parser.parse_args()

nc_path = args.DataPath

if not '.nc' in nc_path:
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]
else:
    nc_path = [nc_path,]

#print header
print"Cast,Cruise,StationNum,time,lat (N),lon (W),StationDepth,CastDepth,IntegratedTemp_top15m,IntegratedTemp_top15m_std,IntegratedTemp_gt25m,IntegratedTemp_gt25m_std,IntegratedTemp_gt25m_numsamples"
varname = 'T_28'

for ncfile in nc_path:
    #print ("Working on {0}...").format(ncfile)

    nchandle = Dataset(ncfile,'a')
    
    global_atts = get_global_atts(nchandle)
    vars_dic = get_vars(nchandle)
    data = ncreadfile_dic(nchandle,vars_dic.keys())
    nchandle.close()
    
    #top 15m including sfc
    missing = 1e35 / 10
    try:
        temp_profile = data[varname][0,:,0,0]
    except KeyError:
        print "No {0} for {1}".format(varname, ncfile)
        continue
        
    intTemptop = temp_profile[0:16][temp_profile[0:16] < missing].mean()
    intTemptop_std = temp_profile[0:16][temp_profile[0:16] < missing].std()
    
    #integrated temp from 25m down to bottom of cast
    #look for really shallow casts and provide sample number for deeper casts
    if temp_profile[25:][temp_profile[25:] < missing].size == 0:
        btmTemptop = ''
        btmTemptop_std = ''
        btmTemptop_samplenum = temp_profile[25:][temp_profile[25:] < missing].size
    else:
        btmTemptop = temp_profile[25:][temp_profile[25:] < missing].mean()
        btmTemptop_std = temp_profile[25:][temp_profile[25:] < missing].std()
        btmTemptop_samplenum = temp_profile[25:][temp_profile[25:] < missing].size

    #time conversion (for CTD profiles the time is a single value)
    mintime = pythondate2str( EPICdate2udunits(data['time'][0], data['time2'][0]) )

    #determine max cast depth from last valid data point
    try:
        castdepth = data['dep'].max()
    except:
        castdepth = data['depth'].max()
    #determine station depth if available
    try:
        stationdepth = global_atts['WATER_DEPTH']
    except:
        stationdepth = ''
        
    #print "m <- addCircles(m, lng=-{0}, lat={1})".format(data['lon'][0],data['lat'][0])
    print "{0},{1},{2},{3}-{4}-{5} {6},{7},{8},{9},{10},{11},{12},{13},{14},{15}".format(global_atts['CAST'],global_atts['CRUISE'],global_atts['STATION_NAME'],\
                mintime[0], mintime[1], mintime[2], mintime[3], data['lat'][0],data['lon'][0],\
                stationdepth, castdepth, intTemptop, intTemptop_std, btmTemptop, btmTemptop_std, btmTemptop_samplenum)
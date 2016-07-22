#!/usr/bin/env

"""
 SQL2meta_ctd.py
 
 Retrieve specific characteristics from CTD cruise database (CTD_MetaInformation)

 Using Anaconda packaged Python 
"""

# System Stack
import datetime
import os
import argparse

# Science Stack
from netCDF4 import Dataset


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2015, 12, 10)
__modified__ = datetime.datetime(2015, 12, 10)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'MetaInformation', 'Cruise', 'MySQL'

"""--------------------------------netcdf Routines---------------------------------------"""


def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)
    
def repl_var(nchandle, var_name, val):
    nchandle.variables[var_name][:] = val[:]
    return
    


"""------------------------   Main   Modules   ----------------------------------------"""

parser = argparse.ArgumentParser(description='Epic Key Variable Cruise Summary')
parser.add_argument('DataPath', metavar='DataPath', type=str, help='Full DataPath to CTD files to be analyzed')
parser.add_argument('CruiseID', metavar='CruiseID', type=str, help='CruiseID')

args = parser.parse_args()

### get all .nc files from chosen directory
full_path = [args.DataPath + x for x in os.listdir(args.DataPath) if x.endswith('.nc')]

#cumulative dictionary - epickey:count
sum_dic = {}

for ncfile in full_path:
    nchandle = Dataset(ncfile,'a')
    vars_dic = get_vars(nchandle)
    nchandle.close()
    
    for keys,vals in enumerate(vars_dic):
        if vals not in sum_dic:
            sum_dic[vals] = 1
        else:
            sum_dic[vals] = sum_dic[vals]+1
            
for keys,vals in enumerate(sum_dic):
    print "{0}, {1}, {2}".format(args.CruiseID, vals, sum_dic[vals])
#!/usr/bin/env python

"""
 Background:
 ===========
 NetCDF_MissingVar.py
 
 
 Purpose:
 ========
 Replaces designated variable (currently in EPIC Format .nc files) with 1e+35 but
    only requires name of variable to work so can be run on non-epic vars as well
 
 Adds additional PROG_CMNT# and EDIT_COMMENT# and History:
 
 Usage:
 ======
 NetCDF_MissingVar.py -> /path/to/data/, {optional file1}, {file 2}, {file n}
 
 History:
 ========

 Compatibility:
 ==============
 python >=3.6? - untested
 python 2.7


"""

#System Stack
import datetime
import os
import sys
import argparse

#Science Stack
from netCDF4 import Dataset
import numpy as np

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 1, 29)
__modified__ = datetime.datetime(2018, 7, 24)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC'

"""--------------------------------netcdf Routines---------------------------------------"""


def get_global_atts(nchandle):

    g_atts = {}
    att_names = nchandle.ncattrs()
    
    for name in att_names:
        g_atts[name] = nchandle.getncattr(name)
        
    return g_atts

def get_vars(nchandle):
    return nchandle.variables

def repl_var(nchandle, var_name, val=1e35):
    nchandle.variables[var_name][:] = np.ones_like(nchandle.variables[var_name][:]) * val
    return
    

    
"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='Replace EPIC Variable with 1e35 for all depths')
parser.add_argument('inputdir', metavar='inputdir', type=str, help='full path to file')
parser.add_argument('EPIC_Key', metavar='EPIC_Key', type=str, help='EPIC Key Code')

args = parser.parse_args()

user_var = args.EPIC_Key

#nc_path = [args.inputdir + fi for fi in os.listdir(args.inputdir) if fi.endswith('.nc')]

#for filein in nc_path:

filein = args.inputdir

print "Working on file %s \n" % filein
###nc readin
nchandle = Dataset(filein,'a')
global_atts = get_global_atts(nchandle)
vars_dic = get_vars(nchandle)

if not user_var in vars_dic.keys():
    print "Variable not in EPIC file: %s      Exiting" % filein
    nchandle.close()
    sys.exit()
else:
    repl_var(nchandle, user_var, val=1e35)
    ### Look for existing program and edit comments / scoot down one level and add new
    for i in range(1,10):
        if ('PROG_CMNT0'+str(i)) in global_atts.keys():
            nchandle.setncattr('PROG_CMNT0'+str(i+1),global_atts['PROG_CMNT0'+str(i)])
        else:
            nchandle.setncattr('PROG_CMNT01',__file__.split('/')[-1] + ' v' + __version__)
        if ('EDIT_CMNT0'+str(i)) in global_atts.keys():
            nchandle.setncattr('EDIT_CMNT0'+str(i+1),global_atts['EDIT_CMNT0'+str(i)])
        else:
            nchandle.setncattr('EDIT_CMNT01','Variable ' + user_var + ' removed')


    nchandle.close()



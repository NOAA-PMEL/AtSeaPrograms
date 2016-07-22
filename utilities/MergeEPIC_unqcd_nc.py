#!/usr/bin/env python

"""
 Background:
 --------
 MergeEPIC_unqcd_nc.py
 
 
 Purpose:
 --------
 Replaces values in 'orig' file with qc'ed EPIC only nc files
  
 
 Usage:
 ------
 nc2nc_2files.py {source_file} {destination_file}


 Built using Anaconda packaged Python:


"""

#System Stack
import datetime
import argparse
import os

#Science Stack
from netCDF4 import Dataset

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
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

def ncreadfile_dic(nchandle, params):
    data = {}
    for j, v in enumerate(params): 
        if v in nchandle.variables.keys(): #check for nc variable
                data[v] = nchandle.variables[v][:]

        else: #if parameter doesn't exist fill the array with zeros
            data[v] = None
    return (data)

def repl_var(nchandle, var_name, user_val ):
    nchandle.variables[var_name][0,:,0,0] = user_val[0,:,0,0]
    return
"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='Copy Data from one netcdf file to another existing file')
parser.add_argument('sourcefile_path', metavar='sourcefile_path', type=str, help='complete path to epic files')
parser.add_argument('origfile_path', metavar='origfile_path', type=str, help='complete path to orig file')
parser.add_argument('--EPIC_Keys', nargs='+', type=str, help='EPIC Keys to keep seperated by spaces')


args = parser.parse_args()


# Get all netcdf files from mooring directory
sourcefile_full = [f for f in os.listdir(args.sourcefile_path) if f.endswith('.nc')]


for counter, input_file in enumerate(sourcefile_full):
    output_file = args.origfile_path + input_file
    input_file = args.sourcefile_path + input_file
    print "Grabin information from file {0}".format(input_file)
    print "Placing it in file {0}".format(output_file)

    ###nc readin
    nchandle_out = Dataset(output_file,'a')
    vars_dic_out = get_vars(nchandle_out)

    nchandle_read = Dataset(input_file,'r')
    vars_dic_read = get_vars(nchandle_read)
    data = ncreadfile_dic(nchandle_read, vars_dic_read)

    if args.EPIC_Keys:
        for var in args.EPIC_Keys:
            if not var in ['time','time2','lat','lon','depth', 'dep']:
                try:
                    print "Replacing {0}".format(var)
                    repl_var(nchandle_out, var, data[var])
                except KeyError:
                    print "Variable {0} not in EPIC file - skipping".format(var)
    else:
        for var in vars_dic_out.keys():
            if not var in ['time','time2','lat','lon','depth', 'dep']:
                try:
                    print "Replacing {0}".format(var)
                    repl_var(nchandle_out, var, data[var])
                except KeyError:
                    print "Variable {0} not in EPIC file - skipping".format(var)
    
    nchandle_read.close()
    nchandle_out.close()






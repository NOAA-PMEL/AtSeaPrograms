#!/usr/bin/env python

"""
 Background:
 --------
 SwitchPriSec_nc.py
 
 
 Purpose:
 --------
 Switch specified parameters from primary to secondary and vice versa
 

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
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header'

    
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
    nchandle.variables[var_name][0,:,0,0] = val
    return
        
"""------------------------------- MAIN------------------------------------------------"""

parser = argparse.ArgumentParser(description='swap primary and secondary sensors')
parser.add_argument('inputpath', metavar='inputpath', type=str,
               help='path to .nc file')
parser.add_argument('-t','--temperature', action="store_true", help='switch primary and secondary temperature')
parser.add_argument('-s','--salinity', action="store_true", help='switch primary and secondary salinity')
parser.add_argument('-o','--oxygen', action="store_true", help='switch primary and secondary oxygen')
parser.add_argument('-ts','--temp_sal', action="store_true", help='switch primary and secondary temperature/salinity')
parser.add_argument('-tso','--temp_sal_oxy', action="store_true", help='switch primary and secondary temperature/salinity/oxygen')

args = parser.parse_args()


#read in netcdf data file
nc_path = [args.inputpath + fi for fi in os.listdir(args.inputpath) if fi.endswith('.nc')]

for filein in nc_path:

    ###nc readin
    nchandle = Dataset(filein,'a')
    global_atts = get_global_atts(nchandle)
    vars_dic = get_vars(nchandle)
    data = ncreadfile_dic(nchandle, vars_dic.keys())

    if args.temp_sal_oxy:
        pri_temp = data['T_28']
        sec_temp = data['T2_35']
        pri_sal = data['S_41']
        sec_sal = data['S_42']
        pri_oxy = data['O_65']
        sec_oxy = data['CTDOXY_4221']  

        repl_var(nchandle, 'T_28', sec_temp)
        repl_var(nchandle, 'T2_35', pri_temp)
        repl_var(nchandle, 'S_41', sec_sal)
        repl_var(nchandle, 'S_42', pri_sal)
        repl_var(nchandle, 'O_65', sec_oxy)
        repl_var(nchandle, 'CTDOXY_4221', pri_oxy)
    
        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1,10):
            if ('PROG_CMNT0'+str(i)) in global_atts.keys():
                nchandle.setncattr('PROG_CMNT0'+str(i+1),global_atts['PROG_CMNT0'+str(i)])
            else:
                nchandle.setncattr('PROG_CMNT01',__file__.split('/')[-1] + ' v' + __version__)
            if ('EDIT_CMNT0'+str(i)) in global_atts.keys():
                nchandle.setncattr('EDIT_CMNT0'+str(i+1),global_atts['EDIT_CMNT0'+str(i)])
            else:
                nchandle.setncattr('EDIT_CMNT01','Primary and Secondary Instruments Switched')

        nchandle.close()
        print "Temperature,Salinity and Oxygen Conc have been swapped, you still need to recalculate sigma-T and Oxy Sat."
    
    if args.temp_sal:
        pri_temp = data['T_28']
        sec_temp = data['T2_35']
        pri_sal = data['S_41']
        sec_sal = data['S_42']
    
        repl_var(nchandle, 'T_28', sec_temp)
        repl_var(nchandle, 'T2_35', pri_temp)
        repl_var(nchandle, 'S_41', sec_sal)
        repl_var(nchandle, 'S_42', pri_sal)

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1,10):
            if ('PROG_CMNT0'+str(i)) in global_atts.keys():
                nchandle.setncattr('PROG_CMNT0'+str(i+1),global_atts['PROG_CMNT0'+str(i)])
            else:
                nchandle.setncattr('PROG_CMNT01',__file__.split('/')[-1] + ' v' + __version__)
            if ('EDIT_CMNT0'+str(i)) in global_atts.keys():
                nchandle.setncattr('EDIT_CMNT0'+str(i+1),global_atts['EDIT_CMNT0'+str(i)])
            else:
                nchandle.setncattr('EDIT_CMNT01','Primary and Secondary Instruments Switched')
            
        nchandle.close()
    
        print "Temperature and Salinity have been swapped, you still need to recalculate sigma-T"
    
    if args.oxygen:
        pri_oxy = data['O_65']
        sec_oxy = data['CTDOXY_4221']  
        pri_oxy_sat = data['OST_62']
        sec_oxy_sat = data['CTDOST_4220']  

        repl_var(nchandle, 'O_65', sec_oxy)
        repl_var(nchandle, 'CTDOXY_4221', pri_oxy)
        repl_var(nchandle, 'OST_62', sec_oxy_sat)
        repl_var(nchandle, 'CTDOST_4220', pri_oxy_sat)    

        ### Look for existing program and edit comments / scoot down one level and add new
        for i in range(1,10):
            if ('PROG_CMNT0'+str(i)) in global_atts.keys():
                nchandle.setncattr('PROG_CMNT0'+str(i+1),global_atts['PROG_CMNT0'+str(i)])
            else:
                nchandle.setncattr('PROG_CMNT01',__file__.split('/')[-1] + ' v' + __version__)
            if ('EDIT_CMNT0'+str(i)) in global_atts.keys():
                nchandle.setncattr('EDIT_CMNT0'+str(i+1),global_atts['EDIT_CMNT0'+str(i)])
            else:
                nchandle.setncattr('EDIT_CMNT01','Primary and Secondary Oxygen EPIC Keys Switched')
            
        nchandle.close()
    
        print "Oxygen sensors have been switched"
        
    if args.salinity:
        pass
    
    if args.temperature:
        pass
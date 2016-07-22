#!/usr/bin/env python

"""
StripEPICvars.py

Removes some variables from .nc files that are not recognized by EPIC edit_look routine
via the shell netcdf utilities

Input - CruiseID

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import shutil
import os


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'MetaInformation', 'Cruise', 'MySQL'

    
"""------------------------------------- System -----------------------------------------"""

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)    
    
"""------------------------------------- Main Routine -----------------------------------------"""

def StripEPIC(user_in, user_out):

    cruiseID = user_in.split('/')[-2]
    leg = cruiseID.lower().split('L')
    if len(leg) == 1:
        cruiseID = leg[0]
        leg = ''
    else:
        cruiseID = leg[0] + 'L' + leg[-1]

    keep_vars = ['time','time2','dep','lat','lon','T_28','T2_35','S_41','S_42','ST_70','OST_62','O_65','Trb_980','PAR_905'] #'CTDOXY_4221','CTDOST_4220','F_903'

    #epic flavored nc files
    nc_path = user_out
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]

    nocopy_flag = 0
    if os.path.exists("/".join(nc_path[0].split('/')[:-1])+'/allparameters/'):
        print "Originals have already been copied... not adding current dir to orig directory"
        nocopy_flag = 1
    
    createDir("/".join(nc_path[0].split('/')[:-1])+'/allparameters/')

    for ncfile in nc_path:
    
        if nocopy_flag == 0:
            shutil.copy (ncfile, "/".join(ncfile.split('/')[:-1])+'/allparameters/'+ncfile.split('/')[-1])

        os.system("nccopy -V "+ ",".join(keep_vars) + " " + "/".join(ncfile.split('/')[:-1])+'/allparameters/'+ncfile.split('/')[-1] + " " + ncfile)
    
    processing_complete = True
    return processing_complete

if __name__ == '__main__':

    user_in = raw_input("Please enter the abs path to the .nc file: or \n path, file1, file2: ")
    user_out = user_in
    StripEPIC(user_in, user_out)
#!/usr/bin/env python

"""
 Background:
 --------
 NCbtl_create.py
 
 
 Purpose:
 --------
 Creates EPIC flavored .nc files for bottle (nutrient) data
 
 File Format:
 ------------
 Assumes .xlsx file with following headers:
 (first 7 columns are nutrient processed, next 5 come from btl files, last two are user created
 Cast	Niskin	PO4 (uM)	Sil (uM)	NO3 (uM)	NO2 (uM)	NH4 (uM)		cast	date	time	nb	PrDM	nisken match	PrDM Round
 
 must specify the units (micromoles/kg or micromoles/l)

 History:
 --------
 2017-07-20: Bell - update excel read to use pandas

"""

#System Stack
import datetime
import argparse
import sys

#Science Stack
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# User Packages
import io_utils.ConfigParserLocal as ConfigParserLocal
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS
import nut2nc

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet'

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='xlsx btl to nc')
parser.add_argument('CruiseID', metavar='CruiseID', type=str, help='provide the cruiseid')
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .xlsx nutrient file')
parser.add_argument('sheet', metavar='sheet', type=int, help='sheet number in .xlsx file')
parser.add_argument('output', metavar='output', type=str, help='output path')
parser.add_argument("-um_l",'--micromoles_liter', action="store_true", help='units of micromoles per liter')
parser.add_argument("-um_kg",'--micromoles_kilogram', action="store_true", help='units of micromoles per kg')

args = parser.parse_args()

if args.micromoles_liter:

    """------------"""
    #pandas reimplimentatioin
    data = pd.read_excel(args.inputpath,sheetname=args.sheet,
            parse_dates={'datetime':['date','time']},
            index_col=False)
    data.fillna(1e35,inplace=True)
    data.set_index(pd.DatetimeIndex(data['datetime']),inplace=True)
    data_gb = data.groupby(by='cast')
    var_list = data.columns

    EPIC_VARS_dict = ConfigParserLocal.get_config('nut_uml_epickeys.json')

    for ind_cast in sorted(data_gb.groups.keys()):
        #print ind_cast
        data_dic = {}
        for var in var_list:
            print "Working on one bottle Cast {0}-{1}".format(ind_cast, args.CruiseID)
            #cycle through and build data arrays
            #create a "data_dic" and associate the data with an epic key
            #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
            # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
            # if it is below but not the epic dic, it will not make it to the nc file
            if var in ['Sil (uM)']: 
                data_dic['SI_188'] = data.loc[data['cast'] == ind_cast][var].values
            elif var in ['PO4 (uM)']: 
                data_dic['PO4_186'] = data.loc[data['cast'] == ind_cast][var].values
            elif var in ['NH4 (uM)']:
                data_dic['NH4_189'] = data.loc[data['cast'] == ind_cast][var].values
            elif var in ['NO2 (uM)']:
                data_dic['NO2_184'] = data.loc[data['cast'] == ind_cast][var].values
            elif var in ['NO3 (uM)']:
                data_dic['NO3_182'] = data.loc[data['cast'] == ind_cast][var].values
            elif var in ['PrDM Round']:
                data_dic['P_1'] = data.loc[data['cast'] == ind_cast][var].values
            elif var in ['nb']:
                data_dic['BTL_103'] = data.loc[data['cast'] == ind_cast][var].values
            else:
                print "Var: {0} not saved to NetCDF".format(var)


        cast = ind_cast
        pydatetime = data.loc[data['cast'] == ind_cast]['datetime'].min().to_pydatetime()
        dtime = Datetime2EPIC(pydatetime)
    
        #PMEL EPIC Conventions
        ncinstance = nut2nc.CTDbtl_NC(savefile=(args.output + args.CruiseID + cast.lower().replace('ctd', 'c') + '_nut.nc'))
        ncinstance.file_create()
        ncinstance.sbeglobal_atts(raw_data_file=args.inputpath.split('/')[-1]) # 
        ncinstance.dimension_init(depth_len=len(data_dic['P_1']))
        ncinstance.variable_init(EPIC_VARS_dict)
        ncinstance.add_data(EPIC_VARS_dict,data_dic)
        ncinstance.add_coord_data(depth=data_dic['P_1'], time1=dtime[0], time2=dtime[1])
        ncinstance.close()

 

if args.micromoles_kilogram:
    print "Work in progress.  Need to have a density conversion"

    ############################################
    #                                          #
    # Retrieve initialization paramters from 
    #   various external files
    ### EPIC Dictionary definitions for WPAK data ###
    # If these variables are not defined, no data will be archived into the nc file for that parameter.

    EPIC_VARS_dict = ConfigParserLocal.get_config('nut_umkg_epickeys.json')


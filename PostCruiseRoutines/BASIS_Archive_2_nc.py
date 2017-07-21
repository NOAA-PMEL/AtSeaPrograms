#!/usr/bin/env python

"""
 Background:
 --------
 BASIS_Archive_2_nc.py
 
 
 Purpose:
 --------
 Creates EPIC flavored .nc files for BASIS data from L.Eisner
 

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
import basis2nc

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 01, 29)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet'

"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='xlsx btl to nc')
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .xlsx nutrient file')
parser.add_argument('sheet', metavar='sheet', type=int, help='sheet number in .xlsx file')
parser.add_argument('output', metavar='output', type=str, help='output path')

args = parser.parse_args()


"""------------"""
#pandas reimplimentatioin
data = pd.read_excel(args.inputpath,sheetname=args.sheet,
        parse_dates={'datetime':['GearinDate','GearinTime']},
        dtype={'SecondarySalinity':float,
                'PrimaryOxygenSat': float,
                'SecondaryOxygenUmol': float,
                'SigmaTheta': float,
                'NTUTurbidity': float},
        index_col=False)
data.fillna(1e35,inplace=True)
data.set_index(pd.DatetimeIndex(data['datetime']),inplace=True)
data_gb = data.groupby(by='StationID')
var_list = data.columns

EPIC_VARS_dict = ConfigParserLocal.get_config('basis_epickeys.json')

for ind_cast in sorted(data_gb.groups.keys()):
    #print ind_cast
    data_dic = {}
    for var in var_list:
        print "Working on Cast {0}-{1}".format(ind_cast, 'BASIS')
        #cycle through and build data arrays
        #create a "data_dic" and associate the data with an epic key
        #this key needs to be defined in the EPIC_VARS dictionary in order to be in the nc file
        # if it is defined in the EPIC_VARS dic but not below, it will be filled with missing values
        # if it is below but not the epic dic, it will not make it to the nc file
        if var in ['PrimaryTemperature']: 
            data_dic['T_28'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['SecondaryTemperature']: 
            data_dic['T2_35'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['PrimarySalinity']:
            data_dic['S_41'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['SecondarySalinity']:
            data_dic['S_42'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['ChlorophyllA']:
            data_dic['F_903'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['BeamAttenuation']:
            data_dic['ATTN_55'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['BeamTransmission_percent']:
            data_dic['Tr_904'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['PARIrradiance']:
            data_dic['PAR_905'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['PrimaryOxygenSat']:
            data_dic['OST_62'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['SecondaryOxygenSat']:
            data_dic['CTDOST_4220'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['PrimaryOxygenumol']:
            data_dic['O_65'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['SecondaryOxygenUmol']:
            data_dic['CTDOXY_4221'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['SigmaTheta']:
            data_dic['STH_71'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['NTUTurbidity']:
            data_dic['Trb_980'] = data.loc[data['StationID'] == ind_cast][var].values


        elif var in ['Pressure']:
            data_dic['P_1'] = data.loc[data['StationID'] == ind_cast][var].values
        elif var in ['Depth']:
            data_dic['Depth'] = data.loc[data['StationID'] == ind_cast][var].values
        else:
            print "Var: {0} not saved to NetCDF".format(var)


    cast = ind_cast
    pydatetime = data.loc[data['StationID'] == ind_cast]['datetime'].min().to_pydatetime()
    dtime = Datetime2EPIC(pydatetime)
    latitude = data.loc[data['StationID'] == ind_cast]['GearInLatitude'].min()
    longitude = data.loc[data['StationID'] == ind_cast]['GearInLongitude'].min() * -1.0

    #PMEL EPIC Conventions
    ncinstance = basis2nc.CTDbtl_NC(savefile=(args.output + 'BASIS_' + str(cast) + '.nc'))
    ncinstance.file_create()
    ncinstance.sbeglobal_atts(raw_data_file=args.inputpath.split('/')[-1],
                                Water_Depth=data.loc[data['StationID'] == ind_cast]['BottomDepth'].min()) # 
    ncinstance.dimension_init(depth_len=len(data_dic['P_1']))
    ncinstance.variable_init(EPIC_VARS_dict)
    ncinstance.add_data(EPIC_VARS_dict,data_dic)
    ncinstance.add_coord_data(depth=data_dic['Depth'], time1=dtime[0], time2=dtime[1], latitude=latitude, longitude=longitude)
    ncinstance.close()




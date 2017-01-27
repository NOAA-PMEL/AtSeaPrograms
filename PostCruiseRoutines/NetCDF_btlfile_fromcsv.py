#!/usr/bin/env python

"""
 Background:
 --------
 NCbtl_create.py
 
 
 Purpose:
 --------
 Creates EPIC flavored .nc files for bottle (upcast) data
 
 File Format:
 ------------
 Assumes .xlsx file with following headers:
 cast	date	time	nb	Sal00	Sal11	Sbeox0Mm/Kg	Sbeox0PS	Sbeox1Mm/Kg	Sbeox1PS	Sigma-t00	PrDM	DepSM	T090C	T190C	Par	V0	V6	WetStar

 cast, date, time, nb are essential - all others will be filled in with missing values if they are not available

 02/03/2016 - modified btl2nc.py and NCbtl_create.py - EPIC variables (and any netcdf variables) are now defined in a *_epickeys.json file

 History:
 --------

 2017-01-25: SBELL - migrate functions/classes to subdirectiories.  Eliminate need for excel read
	and convert to pandas. 

"""

#System Stack
import datetime
import argparse
import collections
import sys

#Science Stack
import numpy as np
import pandas as pd

# User Packages
from io_utils import ConfigParserLocal
from calc.EPIC2Datetime import Datetime2EPIC, get_UDUNITS
from io_utils.EcoFOCI_netCDF_write import CTDbtl_NC

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2015, 10, 02)
__modified__ = datetime.datetime(2015, 10, 02)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'QC', 'bottle', 'discreet','report'

	
"""------------------------------- MAIN--------------------------------------------"""

parser = argparse.ArgumentParser(description='csv btl to nc')
parser.add_argument('inputpath', metavar='inputpath', type=str, help='path to .report_btl summary file')
parser.add_argument('output', metavar='output', type=str, help='output path')
parser.add_argument('CruiseID', metavar='CruiseID', type=str, help='CruiseID')

args = parser.parse_args()

############################################
#                                          #
# Retrieve initialization paramters from 
#   various external files
### EPIC Dictionary definitions for WPAK data ###
# If these variables are not defined, no data will be archived into the nc file for that parameter.
EPIC_VARS_dict = ConfigParserLocal.get_config('bottle_epickeys.json')

"""------------"""
#pandas reimplimentatioin
data = pd.read_csv(args.inputpath,delimiter='\t',
		parse_dates={'datetime':['date','time']},
		index_col=False)
data.fillna(1e35)
data.set_index(pd.DatetimeIndex(data['datetime']))
data_gb = data.groupby(by='cast')
var_list = data.columns


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
		if var in ['CStarTr0']: 
			data_dic['Tr_904'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['CStarAt0']: 
			data_dic['ATTN_55'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sal00']:
			data_dic['S_41'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sal11']:
			data_dic['S_42'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['TurbWETntu0','turbWETntu0', 'Obs']:
			data_dic['Trb_980'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['DepSM']:
			data_dic['D_3'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['WetStar']:
			data_dic['fWS_973'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['FlECO-AFL']:
			data_dic['F_903'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sbeox0Mm/Kg']:
			data_dic['O_65'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sbeox0ps','Sbeox0PS']:
			data_dic['OST_62'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sbeox1Mm/Kg']:
			data_dic['CTDOXY_4221'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sbeox1ps','Sbeox1PS']:
			data_dic['CTDOST_4220'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['T090C']:
			data_dic['T_28'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['T190C']:
			data_dic['T2_35'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['nb']:
			data_dic['BTL_103'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Par']:
			data_dic['PAR_905'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['Sigma-t00']:
			data_dic['ST_70'] = data.loc[data['cast'] == ind_cast][var].values
		elif var in ['PrDM','PrSM']:
			data_dic['P_1'] = data.loc[data['cast'] == ind_cast][var].values
		else:
			print "Var: {0} not saved to NetCDF".format(var)


		cast = ind_cast
		pydatetime = data.loc[data['cast'] == ind_cast]['datetime'].min().to_pydatetime()
		dtime = Datetime2EPIC(pydatetime)

	#PMEL EPIC Conventions
	ncinstance = CTDbtl_NC(savefile=(args.output + args.CruiseID + ind_cast.lower().replace('ctd', 'c') + '_btl.nc'))
	ncinstance.file_create()
	ncinstance.sbeglobal_atts(raw_data_file=args.inputpath.split('/')[-1])  
	ncinstance.dimension_init(depth_len=len(data_dic['P_1']))
	ncinstance.variable_init(EPIC_VARS_dict)
	ncinstance.add_data(EPIC_VARS_dict,data_dic)
	ncinstance.add_coord_data(depth=data_dic['P_1'], time1=dtime[0], time2=dtime[1])
	ncinstance.close()

#!/usr/bin/env python

"""
SCS2CTDdb.py

Takes SCS *.elg file and outputs parameters relevant to FOCI CTD database.


"""

#System Stack
import datetime
import argparse
import csv

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'scs','elg','ctd','FOCI'


"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='SCS *.elg file ')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('-r','--rows', action="store_true", 
	help='organize by entries')
parser.add_argument('-a','--all', action="store_true", 
	help='output all columns')
parser.add_argument('-k','--keys', action="store_true", 
	help='output column names')
parser.add_argument('-ctd','--ctd', action="store_true", 
	help='output basic ctd database columns names')
parser.add_argument('-kn','--key_names', nargs='+', type=str, 
	help='output from selected column names seperate names by spaces')



args = parser.parse_args()

if not args.rows:
	with open(args.DataPath) as csvfile:
		reader = csv.DictReader(csvfile)

		result = {}
		for row in reader:
		    for column, value in row.iteritems():
		        result.setdefault(column, []).append(value)
else:
	with open(args.DataPath) as csvfile:
		reader = csv.DictReader(csvfile)

		count = 0
		result = {}
		for row in reader:
			result[count] = {}
			for column, value in row.iteritems():
				result[count].update({column: value})
			count +=1

if args.all:

	for k in result.keys():
		print "{0}, {1}".format(k, result[k])


if args.keys:
	if args.rows:
		print result[0].keys()
	else:
		for k in result.keys():
			print k

if args.key_names:
	if args.rows:
		for j in result.keys():
			for k in result[j].keys():
				if k in args.key_names:
					print "{0}, {1}".format(k, result[j][k])
	else:
		for k in result.keys():
				if k in args.key_names:
					print "{0}, {1}".format(k, result[k])

if args.ctd:
	ctd_params = ['Date', 'Time','Button','Cast No.',
				  'Station', 'CTD Depth', 'EK60-Depth-m',
				  'AirTemp','RelHumidity','BaroPressure-Cal-VALUE',
				  'TrueWind-RAW-DIRECTION','TrueWind-RAW-SPEED', 'MX420-Lat', 'MX420-Lon']
	if args.rows:
		for j in result.keys():
			for k in result[j].keys():
				if k in ctd_params:
					print "{0}, {1}".format(k, result[j][k])
			print "------------------"
	else:
		for k in result.keys():
				if k in ctd_params:
					print "{0}, {1}".format(k, result[k])
				print "------------------"



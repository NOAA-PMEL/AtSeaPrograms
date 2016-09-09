#!/usr/bin/env python

"""
 Background:
 --------
 mooring_data.py
 
 
 Purpose:
 --------
 Various Routines and Classes to read data from the many numbers of EcoFOCI instruments
 
 History:
 --------


"""
import datetime
import numpy as np
from io import BytesIO

def available_data_sources():
	r"""List of acronyms and options for names for instruments"""
	sources = {
			   'seacat':'sbe16', 'sbe16':'sbe16', 'sbe-16':'sbe16', 'SBE-16':'sbe16',
			   'microcat':'sbe37', 'sbe37':'sbe37', 'sbe-37':'sbe37', 'SBE-37':'sbe37',
			   'sbe39':'sbe39', 'sbe-39':'sbe39', 'SBE-39':'sbe39',
			   'sbe56':'sbe56', 'sbe-56':'sbe56', 'SBE-56':'sbe56',
			   'rcm7':'rcm','rcm9':'rcm', 'rcm11':'rcm',
			   'wpak':'wpak','met':'wpak',
			   'par':'par',
			   'isus':'isus','ISUS':'isus','SUNA':'suna','suna':'suna',
			   'adcp':'adcp','lwrcp':'adcp','wcp':'adcp',
			   'mtr':mtr,'MTR':mtr,
			   'wetstar':'fluor','eco':'fluor','ecofluor':'fluor'
			   }
	return sources

def data_source_instrumentconfig():
	r"""List of acronyms and options for names for instruments"""
	sources = {
			   'seacat':'sbe16', 'sbe16':'sbe16', 'sbe-16':'sbe16', 'SBE-16':'sbe16',
			   'microcat':'sbe37', 'sbe37':'sbe37', 'sbe-37':'sbe37', 'SBE-37':'sbe37',
			   'sbe39':'sbe39', 'sbe-39':'sbe39', 'SBE-39':'sbe39',
			   'sbe56':'sbe56', 'sbe-56':'sbe56', 'SBE-56':'sbe56',
			   'rcm7':'rcm','rcm9':'rcm', 'rcm11':'rcm',
			   'wpak':'wpak','met':'wpak',
			   'par':'par',
			   'isus':'isus','ISUS':'isus','SUNA':'suna','suna':'suna',
			   'adcp':'adcp','lwrcp':'adcp','wcp':'adcp',
			   'mtr':'mtr_epickeys.json','MTR':'mtr_epickeys.json',
			   'wetstar':'fluor','eco':'fluor','ecofluor':'fluor'
			   }
	return sources

def get_inst_data(filename, MooringID=None, source='seacat', **kwargs):
    r"""

    Parameters
    ----------
	filename : string
		complete path to file to be ingested

	MooringID : string
		Unique MooringID (EcoFOCI format for cross referencing with meta database)

	source : string
		Matches available data sources to determine class instantiation
	kwargs
     	Arbitrary keyword arguments to use to initialize source

    Returns
    -------
	Dataset : dictionary of dictionaries
		time : dictionary
			key: 	dataindex
			value:	datetime type
		variables : dictionary of dictionaries
			key: 	dataindex
			value:	float, int, string (depending on instrument)

    """
    
    src = available_data_sources().get(source)
    if src is None:
        raise ValueError('Unknown source for data: {0}'.format(str(source)))

    fobj = src.get_data(filename, MooringID)
    Dataset = src.parse(fobj, **kwargs)


    return Dataset

class mtr(object):
	r""" MicroTemperature Recorders (MTR)
	Collection of static methods to define MTR processing and conversion"""

	@staticmethod
	def parse(fobj, **kwargs):
		r"""Parse MTR Data

	    	kwargs
	        mtr_coef : list
	        [CoefA, CoefB, CoefC]

		"""

		skiprows = ''
		lines = {}

		for k, line in enumerate(fobj.readlines()):
		    line = line.strip()
		    
		    if ('READ' in line):  # Get end of header.
		        skiprows = k
		        print "skipping {0} header rows".format(k)

		    if ('CMD' in line) and k > skiprows:  # Get end of file.
		        break

		    if (k > skiprows) and (skiprows != ''):
		        lines[k] = line
		hexlines = lines
		declines = mtr.MTRhex2dec(hexlines)
		
		if not 'mtr_coef' in kwargs.keys():
			raise UnboundLocalError('No MTR Coefficients where passed as kwargs')

		for sam_num in declines:
		    for k,v in declines[sam_num].items():
		        if not k == 'time':
		            declines[sam_num][k] = [mtr.steinhart_hart(x,kwargs['mtr_coef']) for x in declines[sam_num][k] ]

		### create time and data streams
		count = 0
		time = {}
		temp = {}
		deltat = 0 #10 min usually
		for sam_num in declines:
		    time[count] = declines[sam_num]['time']
		    try:
		        deltat = (declines[count]['time'] - declines[count]['time']) # in seconds
		        deltat = deltat / 120  # number of samples per record and convert 
		    except:
		        datetime.timedelta(0)
		    #loop through dictionary rows
		    for i_row in range(0,10,1): #loop through rows
		        for i_col in range(0,12,1):
		            temp[count] = declines[sam_num]['resistance_'+str(i_row)][i_col]        
		            count +=1
		            time[count] = time[count -1] + deltat
		time.pop(time.keys()[-1]) #delta function adds an extra step so remove last entry
	
		return ({'time':time, 'temperature':temp})

	@staticmethod
	def get_data(filename=None, MooringID=None, **kwargs):
		r"""
		Basic Method to open files.  Specific actions can be passes as kwargs for instruments
		"""

		fobj = open(filename)
		data = fobj.read()


		buf = data
		return BytesIO(buf.strip())

	@staticmethod
	def MTRhex2dec(data_dic, model_factor=4.0e+08):
		'''
		model factor parameter is based on serial number range 
		for counts to resistance conversion
		if (args.SerialNo / 1000 == 3) or (args.SerialNo / 1000 == 4):
		    model_factor = 4.0e+08
		'''
		sample_num = 0
		data = {}
		for k,v in data_dic.items():

		    if len(v) == 16: #timeword mmddyyhhmmssxxxx
		        data[sample_num] = {'time':datetime.datetime.strptime(v[:-4],'%m%d%y%H%M%S')}
		        sample_num += 1
		        start_data = 0
		    elif len(v) == 4: #checksum
		        continue
		    elif len(v) == 48: 
		        #resistance values - 4char hex, 12 measurements, 10 consecutive lines
		        #break string into chunks with 4char 
		        count = 4
		        row = [''.join(x) for x in zip(*[list(v[z::count]) for z in range(count)])]
		        #convert to decimal
		        row = [int(x, 16) for x in row]
		        data[sample_num -1]['resistance_'+str(start_data)] = [(model_factor / x) if x != 0 else 0 for x in row ]
		        start_data += 1
		    else: 
		        print "This line {0} hasn't enough values".format(v)
		        #periodically, it is known that a measurement gets dropped and the line needs
		        # to be filled to 48 characters
		    
		return data

	@staticmethod   
	def steinhart_hart(resistance, mtr_coef):
		'''mtr_coef - 3 parameters pass as a list in kwargs'''

		if resistance <= 0:
		    shhh = 0
		else:
		    shhh = 1.0 / (mtr_coef[0] + (mtr_coef[1] * np.log10(resistance)) + (mtr_coef[2] * np.log10(resistance)**3)) - 273.15

		return shhh


class sbe16(object):
	r"""Seacat / SBE-16 files"""

class sbe37(object):
	r"""Microcat / SBE-37"""

class sbe39(object):
	r""" Temperature (pressure) probe"""

class sbe56(object):
	r""" Temperature probe"""

class rcm(object):
	r""" Anderaa instruments"""

class wpak(object):
	r""" Coastal """

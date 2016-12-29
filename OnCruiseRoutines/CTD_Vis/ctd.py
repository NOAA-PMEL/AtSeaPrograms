#!/usr/bin/env

"""
 ctd.py
 
 Seabird CNV only
 
 Built using Anaconda packaged Python:
 
 Original code reference:
 --------------

 purpose:  Some classes and functions to work with CTD data.
 author:   Filipe P. A. Fernandes
 e-mail:   ocefpaf@gmail
 web:      http://ocefpaf.tiddlyspot.com/
 created:  22-Jun-2012
 modified: Fri 19 Jul 2013 06:24:21 PM BRT

 Todo
 ----
 
 Read <xml> information too (sensor and cal information)
 
 History
 -------
 Found bug in interp2sfc that wasn't allowing pandas frame to be indexed properly
 Initially pressure field was hardcoded to prDM, now prSM is also available
 
"""
from __future__ import absolute_import

# Standard library.
import warnings, datetime, os, sys

# Scientific stack.
import numpy as np
from pandas import Series, DataFrame
from pandas import read_table, concat
from netCDF4 import Dataset

__all__ = ['CTD',
            'interp2sfc',
           'from_cnv',
           'from_netCDF',
           'rosette_summary']

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 13)
__modified__ = datetime.datetime(2014, 01, 13)
__version__  = "0.4.0"
__status__   = "Development"


class CTD(DataFrame):
    def __init__(self, data=None, index=None, columns=None, name=None,
                 longitude=None, latitude=None, header=None, SFC_EXTEND=None, 
                 time_str=None, serial=None, config=None, dtype=None, copy=False):
        super(CTD, self).__init__(data=data, index=index,
                                  columns=columns, dtype=dtype,
                                  copy=copy)
        self.longitude = longitude
        self.latitude = latitude
        self.header = header
        self.SFC_EXTEND = SFC_EXTEND
        self.time_str = time_str
        self.serial = serial
        self.config = config
        self.name = name

    def __reduce__(self):
        return self.__class__, (
            DataFrame(self), # NOTE Using that type(data)==DataFrame and the
                              # the rest of the arguments of DataFrame.__init__
                              # to defaults, the constructors acts as a
                              # copy constructor.
            None,
            None,
            self.longitude,
            self.latitude,
            self.header,
            self.SFC_EXTEND,
            self.time_str,
            self.serial,
            self.config,
            self.name,
            None,
            False,
        )


def remove_above_water(cast):
    return cast[cast.index >= 0]

def interp2sfc(cast, pressure_key='prDM'):
    """ Horribly inefficient for large arrays """
    try:
        min_val_report = cast[pressure_key].values.min()
    except:
        min_val_report = 0.0
        
    min_val = min_val_report
    while min_val > 0.0:
        print 'Extrapolating to surface %s' % min_val
        cast = concat([cast.head(n=1), cast], ignore_index=True)
        min_val = min_val - 1.
        cast[pressure_key][0] = min_val #revalue at each copy
                    
    return (cast, min_val_report)

def from_cnv(fname, compression=None, below_water=False, lon=None,
             lat=None, pressure_varname='prDM'):
    """
    DataFrame constructor to open Seabird CTD CNV-ASCII format.

    Examples
    --------
    >>> from ctd import DataFrame
    >>> cast = DataFrame.from_cnv('../test/data/CTD_big.cnv.bz2',
    ...                           compression='bz2')
    >>> downcast, upcast = cast.split()
    >>> fig, ax = downcast['t090c'].plot()
    >>> ax.grid(True)
    """

    f = open(fname)
    header, config, names, PMELheader = [], [], [], []
    has_NMEA = False
    for k, line in enumerate(f.readlines()):
        line = line.strip()
        if '# name' in line:  # Get columns names.
            name, unit = line.split('=')[1].split(':')
            name, unit = map(normalize_names, (name, unit))
            names.append(name)
        if line.startswith('*'):  # Get header.
            header.append(line)
        if line.startswith('#'):  # Get configuration file.
            config.append(line)
        if line.startswith('@'):  # Get PMEL Header.
            PMELheader.append(line)
        if 'NMEA Latitude' in line:
            hemisphere = line[-1]
            lat = line.strip(hemisphere).split('=')[1].strip()
            lat = np.float_(lat.split())
            if hemisphere == 'S':
                lat = -(lat[0] + lat[1] / 60.)
            elif hemisphere == 'N':
                lat = lat[0] + lat[1] / 60.
            else:
                raise ValueError("Latitude not recognized.")
        if 'NMEA Longitude' in line:
            hemisphere = line[-1]
            lon = line.strip(hemisphere).split('=')[1].strip()
            lon = np.float_(lon.split())
            if hemisphere == 'W':
                lon = -(lon[0] + lon[1] / 60.)
            elif hemisphere == 'E':
                lon = lon[0] + lon[1] / 60.
            else:
                raise ValueError("Latitude not recognized.")
        if 'NMEA UTC' in line:
            time_str = line.strip(hemisphere).split('=')[-1].strip()
            has_NMEA = True
        if '* System UTC' in line:
            systime_str = line.split('=')[-1].strip()
        elif '* System UpLoad Time' in line:
            systime_str = line.split('=')[-1].strip()
        if line == '*END*':  # Get end of header.
            skiprows = k + 1
            if has_NMEA == False: # set time if NMEA not available
                time_str = systime_str
                lon = -999.9
                lat = -999.9
            break

    f.seek(0)
    cast = read_table(f, header=None, index_col=None, names=names,
                      skiprows=skiprows, delim_whitespace=True)
    f.close()
    
    (cast, min_value) = interp2sfc(cast, pressure_key = pressure_varname) 
    cast.set_index(pressure_varname, drop=False, inplace=True)
    cast.index.name = 'Pressure [dbar]'
                    
    name = basename(fname)[0].split('/')[-2] + '_' + basename(fname)[1]
    print name

    dtypes = dict(bpos=int, pumps=bool, flag=bool)
    for column in cast.columns:
        if column in dtypes:
            cast[column] = cast[column].astype(dtypes[column])
        else:
            try:
                cast[column] = cast[column].astype(float)
            except ValueError:
                warnings.warn('Could not convert %s to float.' % column)
    if below_water:
        cast = remove_above_water(cast)
    
    #TODO: Return interp2sfc min_value as "SFC_EXTEND" attribute
    return CTD(cast, longitude=lon, latitude=lat, name=name, header=header,
               config=config, SFC_EXTEND=min_value, time_str=time_str)

def rosette_summary(fname):
    """
    Make a BTL (bottle) file from a ROS (bottle log) file.

    More control for the averaging process and at which step we want to
    perform this averaging eliminating the need to read the data into SBE
    Software again after pre-processing.
    NOTE: Do not run LoopEdit on the upcast!

    Examples
    --------
    >>> fname = '../test/data/CTD/g01l01s01.ros'
    >>> ros = rosette_summary(fname)
    >>> ros = ros.groupby(ros.index).mean()
    >>> np.int_(ros.pressure.values)
    array([835, 806, 705, 604, 503, 404, 303, 201, 151, 100,  51,   1])
    """
    ros = from_cnv(fname)
    ros['pressure'] = ros.index.values.astype(float)
    ros['nbf'] = ros['nbf'].astype(int)
    ros.set_index('nbf', drop=True, inplace=True, verify_integrity=False)
    return ros

def archive_btl(fname):
    """Todo: ingest companion .btl file for nc archiving"""
    pass

"""------------------------- Routines (from utilites) --------------------------------"""
class DataTimes(object):
    """
    Purpose
    -------
    
    Convert a string time of the form 'mmm dd yyyy hh:mm:ss' to python ordinal date or 
    EPIC time (two time keys)

    Example
    -------
    >>>import ctd
    >>>timeinstance = ctd.DataTimes(time_str='jan 01 2013 12:00:00')
    >>> EPIC_Day, EPIC_time = timeinstance.get_EPIC_date()
      
    Reference
    ---------
    PMEL-EPIC Conventions (misprint) says 2400000
    http://www.epic.noaa.gov/epic/eps-manual/epslib_ch5.html#SEC57 says:
    May 23 1968 is 2440000 and July4, 1994 is 2449538
              
    """
    ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
    ref_time_epic = 2440000
    offset = ref_time_epic - ref_time_py
    
    def __init__(self, time_str='jan 01 0001 00:00:00'):
        self.time_str = time_str
        self.date_time = datetime.datetime.strptime(time_str, '%b %d %Y %H:%M:%S')
        
    def get_python_date(self):
        intday = self.date_time.toordinal()
        fracday = (self.date_time.hour / (24.)) + (self.date_time.minute / (24. * 60.)) +\
                    (self.date_time.second / (24. * 60. * 60.))
        return(intday + fracday)
        
    def get_EPIC_date(self):
        time1 = self.date_time.toordinal() + DataTimes.offset
        fracday = (self.date_time.hour / (24.)) + (self.date_time.minute / (24. * 60.)) +\
                    (self.date_time.second / (24. * 60. * 60.))
        time2 = fracday * (24. * 60. * 60. * 1000.)
        
        return(time1, int(time2))

def normalize_names(name):
    name = name.strip()
    name = name.strip('*')
    return name
    
def basename(fname):
    """Return filename without path.

    Examples
    --------
    >>> fname = '../data/tn265/ctd001.cnv' #unix
    >>> fname = 'c:\data\tn265\ctd001.cnv' #windows
    >>> basename(fname)

    """
    fname = fname.replace('\\','/') #convert slashes to unix format
    path, name = os.path.split(fname)
    name, ext = os.path.splitext(name)
    return path, name, ext
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()

#!/usr/bin/env

"""
 Background:
 --------
 CruiseTimeline.py
 
 
 Purpose:
 --------
 Reads csv/google earth file with lat/lon and operations and determines distance and time for cruise
     planning purposes
 
 From given locations and operations, depth is retrieved from ETOPO5 dataset.  Great circle distance is
 calculated from each successive station.  
 Usage:
 ------
Follow the format of the CruiseTimelinePlanning_template.csv

 Original code reference:
 ------------------------

 Built using Anaconda packaged Python:


"""
#System Stack
import datetime
import csv
import collections

#Science Stack
import numpy as np
from netCDF4 import Dataset

# User Stack
import general_utilities.haversine as sphered

# Visual Stack
from mpl_toolkits.basemap import shiftgrid


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 10, 10)
__modified__ = datetime.datetime(2014, 10, 10)
__version__  = "0.1.0"
__status__   = "Development"

"""----------------------------- Read from Excel files --------------------------------"""

def readXlsx(fileName,**args):
 import zipfile
 from xml.etree.ElementTree import iterparse
 if "sheet" in args:
    sheet=args["sheet"]
 else:
    sheet=1
 if "header" in args:
    isHeader=args["header"]
 else:
    isHeader=False

 rows = []
 row = {}
 header = {}
 z=zipfile.ZipFile(fileName)
 # Get shared strings
 strings = [el.text for e, el in iterparse(z.open('xl/sharedStrings.xml')) if el.tag.endswith('}t')]
 value = ''

 # Open specified worksheet
 for e, el in iterparse(z.open('xl/worksheets/sheet%d.xml'%(sheet))):
    # get value or index to shared strings
    if el.tag.endswith('}v'): # <v>84</v>
        value = el.text
    if el.tag.endswith('}c'): # <c r="A3" t="s"><v>84</v></c>
        # If value is a shared string, use value as an index
        if el.attrib.get('t') == 's':
            value = strings[int(value)]
        # split the row/col information so that the row leter(s) can be separate
        letter = el.attrib['r'] # AZ22
        while letter[-1].isdigit():
            letter = letter[:-1]
        # if it is the first row, then create a header hash for the names
        # that COULD be used
        if rows ==[]:
            header[letter]=value
        else:
            if value != '': 
                # if there is a header row, use the first row's names as the row hash index
                if isHeader == True and letter in header:
                    row[header[letter]] = value
                else:
                    row[letter] = value

        value = ''
    if el.tag.endswith('}row'):
        rows.append(row)
        row = {}
 z.close()
 return rows

"""------------------------- Topo   Modules --------------------------------"""

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    #file = '/Users/bell/Data_Local/MapGrids/etopo5.nc'
    ncdata = '/Users/bell/Programs/Python/AtSeaPrograms/data/etopo5.nc'
    etopodata = Dataset(ncdata)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)
    
"""------------------------- General   Modules -----------------------------"""

def data_ingest(file_in):
    """
    read in csv defined with lat, lon,         
    """    
    d = collections.OrderedDict()
    try:
        with open(file_in, 'rU') as csv_file:
            csv_reader = csv.DictReader(csv_file, dialect='excel', quotechar='|')
            for row in csv_reader:
                d[row['StationNumber']] = row
    except:
        print "File not found\n"
        
    return d

def data_save(file_out, data_dict):
    """
    write data to csv        
    """    
    try:
        with open(file_out,'wb') as fou:
            dw = csv.DictWriter(fou, delimiter=',', dialect='excel', quotechar='|', fieldnames=data_dict['2'].keys())
            dw.writeheader()
            for row in data_dict:
                dw.writerow(data_dict[row])
    
    except:
        pass
    
    return

        
def tunnel_fast(latvar,lonvar,lat0,lon0):
    '''
    Find closest point in a set of (lat,lon) points to specified point
    latvar - 2D latitude variable from an open netCDF dataset
    lonvar - 2D longitude variable from an open netCDF dataset
    lat0,lon0 - query point
    Returns iy,ix such that the square of the tunnel distance
    between (latval[it,ix],lonval[iy,ix]) and (lat0,lon0)
    is minimum.
    '''
    pi = np.pi
    
    rad_factor = pi/180.0 # for trignometry, need angles in radians
    # Read latitude and longitude from file into numpy arrays
    latvals = latvar[:] * rad_factor
    lonvals = lonvar[:] * rad_factor
    ny,nx = latvals.shape
    lat0_rad = lat0 * rad_factor
    lon0_rad = lon0 * rad_factor
    # Compute numpy arrays for all values, no loops
    clat,clon = np.cos(latvals),np.cos(lonvals)
    slat,slon = np.sin(latvals),np.sin(lonvals)
    delX = np.cos(lat0_rad)*np.cos(lon0_rad) - clat*clon
    delY = np.cos(lat0_rad)*np.sin(lon0_rad) - clat*slon
    delZ = np.sin(lat0_rad) - slat;
    dist_sq = delX**2 + delY**2 + delZ**2
    minindex_1d = dist_sq.argmin()  # 1D index of minimum element
    iy_min,ix_min = np.unravel_index(minindex_1d, latvals.shape)
    return iy_min,ix_min
    
def naive_fast(latvar,lonvar,lat0,lon0):
    # Read latitude and longitude from file into numpy arrays
    latvals = latvar[:]
    lonvals = lonvar[:]
    ny,nx = latvals.shape
    dist_sq = (latvals-lat0)**2 + (lonvals-lon0)**2
    minindex_flattened = dist_sq.argmin()  # 1D index of min element
    iy_min,ix_min = np.unravel_index(minindex_flattened, latvals.shape)
    return iy_min,ix_min    
    
"""-------------------------------------------------------------------------"""

W = readXlsx('/Users/bell/Documents/EcoFOCI Docs/maps/ArcticChuckchiMaps/2015ChuckchiProposalTransects.xlsx', sheet=1)

ship_speed_kts = 7 #knots
ship_speed_kmhr = ship_speed_kts * 1.852 #knots to km/hr conversion

operation_speed = {'ctd_cast': -20, 'plankton_tow': -20} #in meters/min

(topoin, elats, elons) = etopo5_data()

for index, row in enumerate(W):
    if index <=1:
        continue
    try:
        if row['H'] == '1': #port of call
            print ("calculating parameters for station {0} at Lat {1} Lon {2} ").format(row['B'], \
            row['D'], row['C'])
            origin = [np.float(row['D']),np.float(row['C'])]
    
            #find depth 
            iy_min,ix_min = tunnel_fast(elats,elons,origin[0], -1 * origin[1])
            Depth = topoin[iy_min,ix_min]
            print ("Depth is {0} at lat {1}, lon{2} \n").format(Depth, elats[iy_min,ix_min], elons[iy_min,ix_min])
        
        else: #all subsequent stations
            print ("calculating parameters for station {0} at Lat {1} Lon {2} ").format(row['B'], \
            row['D'], row['C'])

            destination = [np.float(row['D']),np.float(row['C'])]
        
            #find depth 
            iy_min,ix_min = tunnel_fast(elats,elons,destination[0], -1 * destination[1])
            Depth = topoin[iy_min,ix_min]
            print ("Depth is {0} at lat {1}, lon{2} \n").format(Depth, elats[iy_min,ix_min], elons[iy_min,ix_min])

            Distance2Station = sphered.distance(origin,destination)
            print ("Distance to station is {0} km").format(Distance2Station)

            TimeofTransit = Distance2Station / ship_speed_kmhr
            print ("Transit Time at {0} km/hr ({1} knots) will be {2} hr \n").format(ship_speed_kmhr, ship_speed_kts, TimeofTransit)

            #operations time
            station_elapsed_time = 0.0 #hours
            if Depth < -10: #no operations at shallow depths
            
                if Depth < -1510: #max plankton tow
                    op_depth = -1510
                else:
                    op_depth = Depth
                if (row['I'] == 'CTD'):
                    station_elapsed_time = station_elapsed_time + (op_depth +10)*2. / (operation_speed['ctd_cast']*60.)
                if (row['J'] == 'CTD'):
                    station_elapsed_time = station_elapsed_time + (op_depth +10)*2. / (operation_speed['ctd_cast']*60.)
                if (row['K'] == 'CTD'):
                    station_elapsed_time = station_elapsed_time + (op_depth +10)*2. / (operation_speed['ctd_cast']*60.)

                if Depth < -310: #max plankton tow
                    op_depth = -310
                else:
                    op_depth = Depth
                if (row['I'] == 'Bongo'):
                    station_elapsed_time = station_elapsed_time + (op_depth +10)*2. / (operation_speed['plankton_tow']*60.)
                if (row['J'] == 'Bongo'):
                    station_elapsed_time = station_elapsed_time + (op_depth +10)*2. / (operation_speed['plankton_tow']*60.)
                if (row['K'] == 'Bongo'):
                    station_elapsed_time = station_elapsed_time + (op_depth +10)*2. / (operation_speed['plankton_tow']*60.)

            print ("Operation Time at station assuming {0} m/min for ctd and 10m off " 
                    "bottom  or 1500m and plankton tow at {0} m/min to 300m or 10m off bottom is "
                    "{2} hr \n").format(operation_speed['plankton_tow'], operation_speed['ctd_cast'], station_elapsed_time)

            #make origin the destination
            TimeonStation = station_elapsed_time
            origin = destination
    except:
        continue
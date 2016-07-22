#!/usr/bin/env

"""
 ncprossessing.py
 
 Seabird CNV only
 
 Built using Anaconda packaged Python:
 

"""
from __future__ import absolute_import

# Standard library.
import datetime, os

# Scientific stack.
from netCDF4 import Dataset

# User library
from OnCruiseRoutines.EPICNetCDF import SBE_Epiclibrary
from OnCruiseRoutines.EPICNetCDF import epic_key_codes as ekc 


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 13)
__modified__ = datetime.datetime(2014, 10, 10)
__version__  = "0.2.0"
__status__   = "Development"


"""-------------------------------NCFile Creation--------------------------------------"""

"""-------------------------------EPIC Standard----------------------------------------"""

class CTD_NC(object):
    """ Class instance to generate a NetCDF file.  
    Assumes data format and information ingested is a dataframe object from ctd.py 

    Standards
    ---------
    EPICNetCDF (PMEL) Standards  


    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = CTD_NC()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.PMELglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
    """ 
    
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc', data=None):
        """data is a pandas dataframe"""
        
        self.data = data
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, CTD_NC.nc_read, format=CTD_NC.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, coord_system="GEOGRAPHICAL", Water_Mass="G"):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.CREATION_DATE = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.CRUISE = self.data.name.split('_')[0]
        self.rootgrpID.CAST = self.data.name.split('_')[-1]
        self.rootgrpID.INST_TYPE = self.data.header[0]
        self.rootgrpID.DATA_TYPE = 'CTD'
        self.rootgrpID.DATA_CMNT = self.data.header[1].replace('hex','cnv')
        self.rootgrpID.COORD_SYSTEM = coord_system
        self.rootgrpID.WATER_MASS = Water_Mass
        
    def PMELglobal_atts(self, Barometer=9999, Wind_Dir=999, Wind_Speed=99,
                        Air_Temp=99.9, Water_Depth=9999, Prog_Cmnt='', Edit_Cmnt='', Station_Name='', sfc_extend=''):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        Options
        -------
        
        Todo
        -----
        
        Retrieve PMEL header information from '@' comments in .cnv file or from separate
        header.txt file
        """        
        
        #From PMELheader
        
        self.rootgrpID.BAROMETER = Barometer
        self.rootgrpID.WIND_DIR = Wind_Dir
        self.rootgrpID.WIND_SPEED = Wind_Speed
        self.rootgrpID.AIR_TEMP = Air_Temp
        self.rootgrpID.WATER_DEPTH = Water_Depth
        self.rootgrpID.STATION_NAME = Station_Name
        self.rootgrpID.EPIC_FILE_GENERATOR = 'ncprossessing.py V' + __version__ 
        self.rootgrpID.PROG_CMNT01 = Prog_Cmnt
        self.rootgrpID.EDIT_CMNT01 = Edit_Cmnt
        self.rootgrpID.SFC_EXTEND = sfc_extend
        
        pass
        
    def dimension_init(self):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'dep', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], 1 ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], self.data.shape[0] ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self):
        """data.columns.values is a list of all parameters in seabird file.
        We need to match these to EPIC key codes.  These can be found in the EPICNetCDF folder
        
        Usage:
        ------
        
        from EPICnetCDF import SBE_Epiclibrary
        from EPICnetCDF import epic_key_codes as ekc 
        
        ekcl = ekc.EpicKeyCodes()
        
        ekcl.epic_dic_call(SBE_Epiclibrary.SBE_EPIC['sal00']) 
        
        #will return
        #['S  ', 'SALINITY (PSU)           ', 'sal', 'PSU', ' ', 'Practical Salinity Units']
        
        DataFrame.columns.values[0]
        """
        ekcl = ekc.EpicKeyCodes()
        self.epicvars = {}
        self.sbe2epic = {}
        
        # get list of only epic variables in sbe file
        for pname in self.data.columns.values:
            try:
                self.epicvars[pname] = ekcl.epic_dic_call(SBE_Epiclibrary.SBE_EPIC[pname])
                self.sbe2epic[pname] = SBE_Epiclibrary.SBE_EPIC[pname]
                print pname
            except KeyError:
                print "%s is not in the SBE_Epiclibrary and will not be added to the .nc file" % pname
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_FORTRAN, rec_var_units, rec_var_epic = [], [], [], []
        
        # for each epic variable, build required metainformation from epic.key file
        # temperatures should always be first


        for i, k in enumerate(sorted(self.epicvars.keys())):
            kname = self.epicvars[k]
            if kname is None: #dave K designated variables which aren't in epic.key of form -4084 for key 84
                print "Variables in .cnv file %s using identifier %s" % (k, self.sbe2epic[k].split('_')[-1])
                kname = ekcl.epic_dic_call( self.sbe2epic[k][-2:] )
                rec_vars.append('_'.join((kname[0].strip().strip('\\'), self.sbe2epic[k].split('-')[-1])))
            elif (kname[0].strip().lower()) is not '': #no variables without Epic Keys
                print "Variables in .cnv file %s" % ('_'.join((kname[0].strip().strip('\\'), self.sbe2epic[k])))
                rec_vars.append('_'.join((kname[0].strip().strip('\\'), self.sbe2epic[k])))

            else:
                print "No EPICkey. Variables in .cnv file %s -  %s skipped" % (k, self.sbe2epic[k].split('_')[-1])
                continue

                
            rec_var_name.append( kname[0].strip() )
            rec_var_longname.append( kname[1].strip() )
            rec_var_generic_name.append( kname[2].strip() )
            rec_var_units.append( kname[3].strip() )
            rec_var_FORTRAN.append( kname[4].strip() )
            rec_var_epic.append( int(self.sbe2epic[k].split('_')[-1]) )                            

        rec_vars = ['time','time2','dep','lat','lon'] + rec_vars

        rec_var_name = ['', '', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', '', ''] + rec_var_generic_name
        rec_var_FORTRAN = ['', '', '', '', ''] + rec_var_FORTRAN
        rec_var_units = ['True Julian Day', 'msec since 0:00 GMT','dbar','degree_north','degree_west'] + rec_var_units
        rec_var_type= ['i4', 'i4'] + ['f4' for spot in rec_vars[2:]]
        rec_var_strtype= ['EVEN', 'EVEN', 'EVEN', 'EVEN', 'EVEN']
        rec_epic_code = [624,624,1,500,501] + rec_var_epic
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[0]))#time2
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[4], rec_var_type[4], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[5:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+5], rec_var_type[i+5], self.dim_vars))

        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.FORTRAN_format = rec_var_FORTRAN[i]
            v.units = rec_var_units[i]
            if (i <= 4) :
            #no type indicator for non dimensional variables
                v.type = rec_var_strtype[i]
            v.epic_code = rec_epic_code[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

        
    def add_coord_data(self, pressure_var='prDM', latitude=None, longitude=None, time1=None, time2=None, CastLog=False):
        """ """
        self.var_class[0][:] = time1
        self.var_class[1][:] = time2
        if not CastLog:
            self.var_class[2][:] = self.data[pressure_var].values
            self.var_class[3][:] = self.data.latitude
            self.var_class[4][:] = -1 * self.data.longitude #PMEL standard direction
        else:
            self.var_class[2][:] = self.data[pressure_var].values
            self.var_class[3][:] = latitude
            self.var_class[4][:] = -1 * longitude #PMEL standard direction W is +

    def add_data(self):
        """ """
        ekcl = ekc.EpicKeyCodes()
        for k in self.data.columns.values:
            try:
                kname = self.epicvars[k]
                if kname is None: #dave K designated variables which aren't in epic.key of form -4084 for key 84
                    kname = ekcl.epic_dic_call( self.sbe2epic[k][-2:] )
                    temp = ('_'.join((kname[0].strip().strip('\\'),  self.sbe2epic[k].split('-')[-1]))) 

                elif (kname[0].strip().lower()) is not '': #no variables without Epic Keys
                    temp = ('_'.join((kname[0].strip().strip('\\'), self.sbe2epic[k])))

                else:
                    continue
            except:
                continue

            di = self.rec_vars.index(temp)
            self.var_class[di][:] = self.data[k].values
            
        
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.History = self.History + ' ' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()
    



"""-----------------------------CF V1.6 / COARDS Standards-----------------------------"""

class CF_CTD_NC(object):
    """
    Class instance to generate a NetCDF file.  
    Assumes data format and information ingested is a dataframe object from ctd.py 
    
    Standards
    ---------
    CF V1.6 / COARDS Standards
    

    Usage
    -----
    
    Order of routines matters and no error checking currently exists
    ToDo: Error Checking
    
    Use this to create a nc file with all default values
        ncinstance = CF_CTD_NC()
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.PMELglobal_atts()
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_coord_data()
        ncinstance.add_data()
        ncinstance.close()
        
    
    """ 
    
    nc_format = 'NETCDF3_CLASSIC'
    nc_read   = 'w'
    def __init__(self, savefile='ncfiles/test.nc', data=None):
        """data is a pandas dataframe"""
        
        self.data = data
        self.savefile = savefile
    
    def file_create(self):
            rootgrpID = Dataset(self.savefile, CTD_NC.nc_read, format=CTD_NC.nc_format)
            self.rootgrpID = rootgrpID
            return ( rootgrpID )
        
    def sbeglobal_atts(self, coord_system="GEOGRAPHICAL", Water_Mass="G"):
        """
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        """
        
        self.rootgrpID.creation_date = datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")
        self.rootgrpID.cruiseID = self.data.name.split('_')[0]
        self.rootgrpID.castID = self.data.name.split('_')[-1]
        self.rootgrpID.instrument_type = self.data.header[0]
        self.rootgrpID.data_type = 'CTD'
        self.rootgrpID.data_comment = self.data.header[0].replace('hex','cnv')
        self.rootgrpID.coordinate_system = coord_system
        self.rootgrpID.water_mass = Water_Mass
        
    def PMELglobal_atts(self, Barometer=9999, Wind_Dir=999, Wind_Speed=99,
                        Air_Temp=99.9, Water_Depth=9999, Prog_Cmnt='', Edit_Cmnt='', Station_Name='', sfc_extend=''):
        """
        
        Assumptions
        -----------
        
        Format of DataFrame.name = 'dy1309l1_ctd001'
        
        seabird related global attributes found in DataFrame.header list
        
        
        Todo
        ----
        
        Either ingest .cnv files with '@' comment codes, or a seperate text file
        """        
        
        #From PMELheader
        
        self.rootgrpID.barometer = Barometer
        self.rootgrpID.wind_direction = Wind_Dir
        self.rootgrpID.wind_speed = Wind_Speed
        self.rootgrpID.air_temperature = Air_Temp
        self.rootgrpID.water_depth = Water_Depth
        self.rootgrpID.station_name = Station_Name
        self.rootgrpID.ingest_software = 'ncprossessing.py V' + __version__ 
        self.rootgrpID.processing_level = 'a0'
        self.rootgrpID.history = ''
        self.rootgrpID.conventions = 'COARDS'
        self.rootgrpID.surface_extend = sfc_extend
        
        pass
        
    def dimension_init(self):
        """
        Assumes
        -------
        Dimensions will be 'time', 'depth', 'lat', 'lon'
        
        Todo
        ----
        User defined dimensions
        """

        self.dim_vars = ['time', 'dep', 'lat', 'lon']
        
        self.rootgrpID.createDimension( self.dim_vars[0], 1 ) #time
        self.rootgrpID.createDimension( self.dim_vars[1], self.data.shape[0] ) #depth
        self.rootgrpID.createDimension( self.dim_vars[2], 1 ) #lat
        self.rootgrpID.createDimension( self.dim_vars[3], 1 ) #lon
        
        
    def variable_init(self):
        """data.columns.values is a list of all parameters in seabird file.
        We need to match these to EPIC key codes.  These can be found in the EPICNetCDF folder
        
        Usage:
        ------
        
        from EPICnetCDF import SBE_Epiclibrary
        from EPICnetCDF import epic_key_codes as ekc 
        
        ekcl = ekc.EpicKeyCodes()
        
        ekcl.epic_dic_call(SBE_Epiclibrary.SBE_EPIC['sal00']) 
        
        #will return
        #['S  ', 'SALINITY (PSU)           ', 'sal', 'PSU', ' ', 'Practical Salinity Units']
        
        DataFrame.columns.values[0]
        """
        ekcl = ekc.EpicKeyCodes()
        self.epicvars = {}
        self.sbe2epic = {}
        
        # get list of only epic variables in sbe file
        for pname in self.data.columns.values:
            try:
                self.epicvars[pname] = ekcl.epic_dic_call(SBE_Epiclibrary.SBE_EPIC[pname])
                self.sbe2epic[pname] = SBE_Epiclibrary.SBE_EPIC[pname]
            except KeyError:
                print "%s is not in the SBE_Epiclibrary and will not be added to the .nc file" % pname
        
        #build record variable attributes
        rec_vars, rec_var_name, rec_var_longname = [], [], []
        rec_var_generic_name, rec_var_missing, rec_var_units, rec_epic_code = [], [], [], []
        
        # for each epic variable, build required metainformation from epic.key file
        for i, k in enumerate(self.epicvars.keys()):
            kname = self.epicvars[k]
            if kname is None: # variables not in epic.key but given epic like codes
                              # these are often secondary instruments
                kname = ekcl.epic_dic_call(self.sbe2epic[k][-2:])
                print "Variables in .cnv file %s listed as secondary" % ( k )
                rec_vars.append( k.replace('/','per') )
                rec_var_name.append( kname[0].strip() )
                rec_var_longname.append( kname[1].strip() )
                rec_var_generic_name.append( kname[2].strip() )
                rec_var_units.append( kname[3].strip() )
                rec_epic_code.append( self.sbe2epic[k] )


            else:
                print "Variables in .cnv file %s" % ( k )
                rec_vars.append( k.replace('/','per') )
                rec_var_name.append( kname[0].strip() )
                rec_var_longname.append( kname[1].strip() )
                rec_var_generic_name.append( kname[2].strip() )
                rec_var_units.append( kname[3].strip() )
                rec_epic_code.append( self.sbe2epic[k] )
                            
        #hard coded variables are expected coordinate variables
        rec_vars = ['time','dep','lat','lon'] + rec_vars
        rec_var_name = ['', '', '', ''] + rec_var_name
        rec_var_longname = ['', '', '', ''] + rec_var_longname
        rec_var_generic_name = ['', '', '', ''] + rec_var_generic_name
        rec_var_units = ['Days Since 01 01 0001 00:00:00','dbar','degrees_north','degrees_east'] + rec_var_units
        rec_var_type= ['f8'] + ['f4' for spot in rec_vars[1:]]
        rec_epic_code = ['','1','500','501'] + rec_epic_code
        rec_var_missing = [-9999. for spot in rec_vars]
        
        
        var_class = []
        var_class.append(self.rootgrpID.createVariable(rec_vars[0], rec_var_type[0], self.dim_vars[0]))#time1
        var_class.append(self.rootgrpID.createVariable(rec_vars[1], rec_var_type[1], self.dim_vars[1]))#depth
        var_class.append(self.rootgrpID.createVariable(rec_vars[2], rec_var_type[2], self.dim_vars[2]))#lat
        var_class.append(self.rootgrpID.createVariable(rec_vars[3], rec_var_type[3], self.dim_vars[3]))#lon
        
        for i, v in enumerate(rec_vars[4:]):  #1D coordinate variables
            var_class.append(self.rootgrpID.createVariable(rec_vars[i+4], rec_var_type[i+4], self.dim_vars))

        ### add variable attributes
        for i, v in enumerate(var_class): #4dimensional for all vars
            print ("Adding Variable {0}").format(v)#
            v.setncattr('name',rec_var_name[i])
            v.long_name = rec_var_longname[i]
            v.generic_name = rec_var_generic_name[i]
            v.units = rec_var_units[i]
            v.historic_epic_code = rec_epic_code[i]
            v.missing_value = rec_var_missing[i]
            
        self.var_class = var_class
        self.rec_vars = rec_vars

                    
    def add_coord_data(self, pressure_var='prDM', latitude=None, longitude=None, time=None, CastLog=False):

            self.var_class[0][:] = time
            if not CastLog:
                self.var_class[1][:] = self.data[pressure_var].values
                self.var_class[2][:] = self.data.latitude
                self.var_class[3][:] = self.data.longitude # +/- East/West
            else:
                self.var_class[1][:] = self.data[pressure_var].values
                self.var_class[2][:] = latitude
                self.var_class[3][:] = longitude # +/- East/West
        
    def add_data(self):
        try:
            for pname in self.data.columns.values:
                di = self.rec_vars.index(pname.replace('/','per'))
                self.var_class[di][:] = self.data[pname].values
        except ValueError:
            print "%s is not in epic library and will not be added" % (pname)
            
    def add_history(self, new_history):
        """Adds timestamp (UTC time) and history to existing information"""
        self.history = self.history + ' ' + datetime.datetime.utcnow().strftime("%B %d, %Y %H:%M UTC")\
                    + ' ' + new_history + '\n'
                    
    def close(self):
        self.rootgrpID.close()
    

#!/usr/bin/env

"""
 Background:
 --------
 CTD2NC.py
 
 Seabird CNV only
 
 Purpose:
 --------
 Reads and analyzes *.cnv files and converts to EPIC-NetCDF
 
 
 Usage:
 ------
 from CTD_Vis import ctd
 cast = ctd.from_cnv(filein)
 

 Original code reference:
 ------------------------

 Built using Anaconda packaged Python:


"""
# System Packages
import datetime, os


# User Packages
from CTD_Vis import ctd
from CTD_Vis import ncprocessing

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2014, 10, 13)
__version__  = "0.2.0"
__status__   = "Development"

"""-------------------------------Work Flow--------------------------------------------"""
"""
read sbe *.cnv files (python-ctd: Pandas Data Frame Utility)

Initialize .nc file
Write attributes, variables and variable attributes

"""
"""------------------------------- Data Pointer----------------------------------------"""

def data_processing(user_in, user_out):

    #add ability to ingest entire directory
    if os.path.isdir(user_in):
        user_in = [user_in] + [fi for fi in os.listdir(user_in) if fi.endswith('.cnv')]
    
    else:
        user_in = user_in.split(',')

    for i, filein in enumerate(user_in):
        if i == 0 and len(user_in) > 1:
            path = filein.strip()
            continue
        elif i == 0 and len(user_in) == 1:
            path = filein.strip()
        else:
            filein = path + filein.strip()
    
        #read in .cnv file generate pandas dataframe... includes some preprocessing
        #Todo: incorporate PMEL header information from cast logs (either as a '@' comment in the cnv file or from a separate text file)
        cast = ctd.from_cnv(filein)

        timeclass = ctd.DataTimes(time_str=cast.time_str)
        sfc_extend = 'Extrapolated to SFC from ' + str(cast.SFC_EXTEND) + 'm'
    
        # make sure save path exists
        savefile=(user_out)
        if not os.path.exists(savefile):
            os.makedirs(savefile)

        print "Working on Cast %s" % filein
        ### Change pressure_var to prDM for most 9/11 and prSM for sbe25 in following line or prdM for sbe19pV2
        pressure_varname = 'prDM'        
        
        #PMEL EPIC Conventions
        ncinstance = ncprocessing.CTD_NC(savefile=(savefile + cast.name.replace('_ctd', 'c') + '_ctd.nc'), data=cast)
        ncinstance.file_create()
        ncinstance.sbeglobal_atts() # 
        ncinstance.PMELglobal_atts(sfc_extend=sfc_extend)
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_data()
        ncinstance.add_coord_data(pressure_var=pressure_varname, time1=timeclass.get_EPIC_date()[0], time2=timeclass.get_EPIC_date()[1])
        ncinstance.close()
    
        #COARDS/CF Style Conventions
        '''
        ncinstance = ncprocessing.CF_CTD_NC(savefile=(savefile + cast.name.replace('_ctd', 'c') + '_cf_ctd.nc'), data=cast)
        ncinstance.file_create()
        ncinstance.sbeglobal_atts()
        ncinstance.PMELglobal_atts(sfc_extend=sfc_extend)
        ncinstance.dimension_init()
        ncinstance.variable_init()
        ncinstance.add_data()
        ncinstance.add_coord_data( time=timeclass.get_python_date() )
        ncinstance.close()    
        '''
    processing_complete = True
    return processing_complete

if __name__ == '__main__':

    user_in = raw_input("Please enter the abs path to the .cnv file: or \n path, file1, file2: ")
    data_processing()
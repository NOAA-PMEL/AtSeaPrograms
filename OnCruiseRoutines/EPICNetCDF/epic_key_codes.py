#!/usr/bin/env

"""
epic_key_codes.py

Purpose
-------

Store and retrieve epic.key as class

Usage
-----
import EpicKeyCodes as ekc
class instance -- keys = ekc.EpicKeyCodes()

requires epic.key (csv file) in same directory as this program and
will generate a pickle file in the directory this routine is located in

"""

# Standard Packages
import os, sys, csv
import datetime
import pickle

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2013, 12, 18)
__modified__ = datetime.datetime(2014, 01, 22)
__version__  = "0.1.0"
__status__   = "Development"


"""------------------------------------------------------------------------------------"""
class EpicKeyCodes(object):
    """    
    Uses:
    -----
    Requires a text file called epic.key 
    The first few lines of text look as follows:
    
    FILE NAME:
    ----------
    epic.key       dated: 7/23/2004
    List of "Key Codes" as defined in PMEL::EPIC NetCDF Conventions
    
    
    |    :   :UNDEFINED                : :counts: :Undefined Variable 
    |   0:   :Undefined                :generic:units:format:Undefined Variable 
    |   1:P  :PRESSURE (DB)            :depth:dbar:f10.1: 
    |   2:D  :DEPTH (CM)               :depth:cm: : 
    |   3:D  :DEPTH (M)                :depth:m:f10.1: 

    Since there are no comment lines, remove/skip the first four lines of the file and
    start with the "0" index.
    """
    def __init__(self, epickey_pickle='/epic_key.p'):
        """ 
        Keyword Args
        ----------
        epickey_pickle -- user path to alterate epic_key pickle file
    
    
        Purpose
        --------
        Will generate a pickle file from local epic.key file in folder
        
        """
        self.epickey_pickle = epickey_pickle
        
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        try:
            epic_keys = pickle.load( open( dir_path + epickey_pickle, "rb" ) )

        except:
            print "File did not exists, creating it now... \n"
            self.EpicKey_pickle_dump()
            try:
                epic_keys = pickle.load( open( dir_path + self.epickey_pickle, "rb" ) )
            except:
                print "No success in creating pickle file!", sys.exc_info()[0]
                raise
        
        
        self.epic_keys = epic_keys

    def EpicKey_pickle_dump(self, epic_text='/epic.key'):
        """
        Internal Routine - will not usually be called.
        
        Parameters
        ----------
        epic_text -- path to epic.key file 
        
        Website
        -------
        
        `ftp://ftp.unidata.ucar.edu/pub/netcdf/Conventions/PMEL-EPIC/epic.key` for most recent key file
        """
        d = {}
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)

        try:
            with open(dir_path + epic_text, 'rb') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=':')
                for row in csv_reader:
                    d[row[0].strip()] = row[1:]
            
            pickle.dump( d, open( dir_path + self.epickey_pickle, "wb" ) )
        except:
            print "No success in creating pickle file! \n Do you have the epic.key file? \n", sys.exc_info()[0]
            raise            


            
    def epic_dic_call(self, code='42'):
        """ 
        Parameters
        ----------

        code -- string representation of an epic key code (e.g. '42')
                           
           
        Returns
        -------
        Outputs : List
                  meta information associated with EPIC Code
                      
        """
     
        return self.epic_keys.get(code)


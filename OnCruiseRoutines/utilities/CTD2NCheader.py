#!/usr/bin/env

"""
 CTD2NCheader.py
 
 When run independantly, this program will allow the creation of a header text file for
 all ctd casts in a directory.  It relys mostly on the ship logs and not on the meta information
 within the ctd files.

 Using Anaconda packaged Python 
"""

import os, datetime
#user defined
from utilities import utilities

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 13)
__modified__ = datetime.datetime(2014, 01, 13)
__version__  = "0.1.0"
__status__   = "Development"

"""-----------------------------Cruise Log Class---------------------------------------"""
class CruiseLogHeader(object):
    """This class holds all necessary header information from a cruise log"""
    Vessel_ID = []
    Cruise_ID = []
    
    def __init__(self,CTD_num= 'n/a',lat= 'n/a',lon= 'n/a',day= 'n/a',date= 'n/a',time_gmt= 'n/a',
                    dry_bulb= 'n/a',wet_bulb= 'n/a',press= 'n/a',wind_dir= 'n/a',wind_speed= 'n/a',
                    bttm_depth= 'n/a',stat_name= 'n/a',water_mass_code= 'G'):
        self.CTD_num = CTD_num
        self.lat = lat
        self.lon = lon
        self.day = day
        self.date = date
        self.time_gmt = time_gmt
        self.dry_bulb = dry_bulb
        self.wet_bulb = wet_bulb
        self.press = press
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.bttm_depth = bttm_depth
        self.stat_name = stat_name
        self.water_mass_code = water_mass_code
        
    def hardcodedvars(self):
        self.seastate = 'n/a'
        self.visibility = 'n/a'
        self.cloud_amt = 'n/a'
        self.cloud_type = 'n/a'
        self.weather = 'n/a'
        
    
    def print2file(self, ofile):
        with open(ofile, "a") as myfile:
            myfile.write("Castnum=%s, Lat(N)=%s, Lon(W)=%s W, Day=%s, Date=%s, time (GMT)=%s, Dry_bulb=%s, Wet_bulb=%s, Pressure=%s, wind dir=%s, wind speed=%s, bottom depth=%s, station name/id=%s, water mass code=%s \n"
                % (self.CTD_num, self.lat, self.lon, self.day, self.date, self.time_gmt,
                self.dry_bulb, self.wet_bulb, self.press, self.wind_dir, self.wind_speed,
                self.bttm_depth, self.stat_name, self.water_mass_code))
        


    

"""-----------------------------Cruise Log---------------------------------------------"""

        
def CruiseLogHeaderRead(ifile_clh, idir):
    """ Get Existing header info from text file"""
    CruiseLogHeader.Cruise_ID = idir.split('/')[-2]
    dic_casts = {}
    
    print "Reading in " + ifile_clh
    with open(ifile_clh, "r") as myfile:
    #expecting format from CruiseLogHeader.print2file()
        for line in myfile:
            line_split = line.split(',')
            dic_casts[line_split[0].split('=')[1]] = CruiseLogHeader(line_split[0].split('=')[1],line_split[1].split('=')[1],line_split[2].split('=')[1],
                line_split[3].split('=')[1],line_split[4].split('=')[1],line_split[5].split('=')[1],line_split[6].split('=')[1],
                line_split[7].split('=')[1],line_split[8].split('=')[1],line_split[9].split('=')[1],line_split[10].split('=')[1],
                line_split[11].split('=')[1],line_split[12].split('=')[1],line_split[13].split('=')[1])
    
    return(dic_casts)
    
def CruiseLogHeaderCreate(ifile_clh, idir, castfiles):
    """ Create header info from existing files and cruise log"""
    #get info from cast files first
    CruiseLogHeader.Vessel_ID = idir.split('/')[-2][0:2]
    CruiseLogHeader.Cruise_ID = idir.split('/')[-2]
    CID = raw_input("The Cruise ID is listed as: [" + CruiseLogHeader.Cruise_ID + "]. If this is correct, press enter or input new ID. \n")
    if CID:
        CruiseLogHeader.Cruise_ID = CID
        
    dic_casts = {}
    ### add cruise header info
    for i, fid in enumerate(castfiles):
        
        idname = fid.split('.')[0]
        dic_casts[idname] = CruiseLogHeader()
        dic_casts[idname].CTD_num = idname
        #cast
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("ctd number: " + dic_casts[idname].CTD_num)
        if t_var:
            dic_casts[idname].CTD_num = t_var
        #lat
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Latitude (N): " + dic_casts[idname].lat)
        if t_var:
            dic_casts[idname].lat = t_var
        #lon        
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Longitude (W): " + dic_casts[idname].lon)
        if t_var:
            dic_casts[idname].lon = t_var        
        #day
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Day: " + dic_casts[idname].day)
        if t_var:
            dic_casts[idname].day = t_var        
        #date
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Date (Sep 13): " + dic_casts[idname].date)
        if t_var:
            dic_casts[idname].date = t_var
        #time
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("24hr GMT time (hh:mm): " + dic_casts[idname].time_gmt)
        if t_var:
            dic_casts[idname].time_gmt = t_var
        #dry bulb
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Dry Bulb (deg C): " + dic_casts[idname].dry_bulb)
        if t_var:
            dic_casts[idname].dry_bulb = t_var        
        #wet bulb
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Wet Bulb (deg C): " + dic_casts[idname].wet_bulb)
        if t_var:
            dic_casts[idname].wet_bulb = t_var        
        #pres
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("ctd number: " + dic_casts[idname].press)
        if t_var:
            dic_casts[idname].press = t_var        
        #wind dir
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Wind Dir.: " + dic_casts[idname].wind_dir)
        if t_var:
            dic_casts[idname].wind_dir = t_var            
        #wind speed
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Wind Speed (kts): " + dic_casts[idname].wind_speed)
        if t_var:
            dic_casts[idname].wind_speed = t_var            
        #bottom depth
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("bottom depth (m): " + dic_casts[idname].bttm_depth)
        if t_var:
            dic_casts[idname].bttm_depth = t_var        
        #station name
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Station Name/ID: " + dic_casts[idname].stat_name)
        if t_var:
            dic_casts[idname].stat_name = t_var            
        #wind speed
        print "For the following information: enter a new value or press return \n"
        t_var = raw_input("Water Mass Code: (A)rctic, (G)ulf of Alaska, (B)ering Sea,\n \
        (S)helikof Strait, (P)uget Sound, (V)ents: " + dic_casts[idname].water_mass_code)
        if t_var:
            dic_casts[idname].water_mass_code = t_var   

        dic_casts[idname].print2file(ifile_clh)
        
    return(dic_casts)

"""-----------------------------Main---------------------------------------------------"""

def header_main():
    idir = utilities.ChooseDirectoryofCruise() #user defined path to cruise
    (castfiles, btlfiles, ioerror) = utilities.GetCNVorBTL(idir) #check for .cnv and .btl files and retrieve
    if not ioerror == 0:
        print "No .cnv files are found, will not be able to generate header updates. \n"
        sys.exit()
    
    print "Looking for cruise header text file. \n"
    if os.path.exists(idir + 'cruiselogheader.txt'):
        print "Found existing cruiselogheader.txt \n"
        dic_casts = CruiseLogHeaderRead(idir + 'cruiselogheader.txt', idir)
    else:
        print """No cruiselogheader.txt file.  Proceeding to generate it.  \n
        You will need to have the cruise logs to proceed. \n""" 
        dic_casts = CruiseLogHeaderCreate(idir + 'cruiselogheader.txt', idir, castfiles)  #from Ship Logs


if __name__ == "__main__":
    header_main()    
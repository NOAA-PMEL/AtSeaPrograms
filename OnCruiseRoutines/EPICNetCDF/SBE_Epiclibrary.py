#!/usr/bin/env python

""" 
SBE_Epiclibrary.py

Purpose
-------

Collect SBE variables with their EPIC Key to retrieve meta information from Epic.Key

Usage
-----
Searching the SBE_EPIC dictionary for a SBE keyword will give you the EPIC Key to Use.

Modified From
-------------
seasoft_ctd.h 

Notes
-----
References to local keyrange have it set at 1000
References to secondary keyrange have it set at 2000
References to tertiary keyrange have it set at 3000
References to quaternary keyrange have it set at 4000
References to quintanary keyrange have it set at 5000

To Update Dictionary
--------------------
Any potential variable name can be added as the dictionary index item as long as an epic
key code is provided as well

Missing epic key_codes will ultimately be skipped

SBE_EPIC['sbe_var'] = 'key_code'

Modifications
-------------
Added 'depSM'
Added 'sbeox0V' with no Epic Key
Added 'sbeox1V' with no Epic Key
Added 'v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6' placeholders
Added 'flag' with no Epic Key
Gave "sbeox1ML/L", "sbeox1PS" secondary keys
Added "flECO-AFL" = '906'
Added EPIC key to conductivity
Added Transmissometry field
Added Turbidity (from Dyson FLNTUR - Wetlabs)
Changed flECO to flourescence key (not chlor A key)
Secondary O2 % sat now 4220
Added prSM as another identifier for pressure
Added attenuation for transmissometry
Added 'obs: OBS, Backscatterance (D & A) [NTU]' from EMA as 980

updated sbeox0V with key 5000
updated sbeox1V with key 5001
add 'nbin' = '9999' - CTD number of sample bins
add 'dz/dtM' = '9998' - CTD descent rate
add 'tv290C' = '35' for RUSALCA 2014 Cruise
add 'prdM' = '1' for RUSALCA 2014 Cruise

for fluorometers - micrograms / l is equivalent to milligrams / m**3 - 

add 'nb' = '103' for niskin bottles for bottle logs/ nutrient logs

add 'ph' = '159'
"""
import datetime

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2013, 01, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.2"
__status__   = "Development"

"""------------------------------------------------------------------------------------"""

SBE_EPIC = {}

#CTD
SBE_EPIC["bottle"]  = '103' 
SBE_EPIC["scan"]    = '' 
SBE_EPIC["pr"]      = '1' 
SBE_EPIC["prDM"]    = '1' 
SBE_EPIC["prdM"]    = '1' 
SBE_EPIC["prSM"]    = '1' 
SBE_EPIC["depSM"]    = '3' 
SBE_EPIC["t068"]    = '20' 
SBE_EPIC["t168"]    = '34' 
SBE_EPIC["t090"]    = '28' 
SBE_EPIC["t190"]    = '35' 
SBE_EPIC["t068C"]   = '20' 
SBE_EPIC["t168C"]   = '34' 
SBE_EPIC["t090C"]   = '28' 
SBE_EPIC["t190C"]   = '35' 
SBE_EPIC["tv290C"]    = '28' #RUSALCA SBE19

"""
# if conductivity is archived - following is potential epic key
SBE_EPIC["c0mS/cm"] = '51' # true epic key is for S/cm
SBE_EPIC["c0S/cm"]  = '51' 
SBE_EPIC["c1mS/cm"] = '-2051' # no true epic key for
SBE_EPIC["c1S/cm"]  = '-2051' # true epic key is for S/cm
"""
SBE_EPIC["c0mS/cm"] = '' 
SBE_EPIC["c0S/cm"]  = '' 
SBE_EPIC["c1mS/cm"] = '' 
SBE_EPIC["c1S/cm"]  = '' 
#salinity
SBE_EPIC["sal00"]   = '41' 
SBE_EPIC["sal11"]   = '42' 
SBE_EPIC["sal01"]   = '44' 
SBE_EPIC["sal10"]   = '45' 
#density
SBE_EPIC["density00"] = '84' 
SBE_EPIC["density11"] = '-2084' # (-2000 - primary key)
SBE_EPIC["density01"] = '-3084' # (-3000 - primary key)
SBE_EPIC["density10"] = '-4084' # (-4000 - primary key)
SBE_EPIC["sigma-t00"] = '70' 
SBE_EPIC["sigma-t11"] = '-2070' # (-2000 - primary key)
SBE_EPIC["sigma-t01"] = '-3070' # (-3000 - primary key) 
SBE_EPIC["sigma-t10"] = '-4070' # (-4000 - primary key) 

#Oxygen
SBE_EPIC["oxsatML/L"] = '60'    #60:ml/l,65:umol/kg
SBE_EPIC["oxC"]     = '110'     #oxygen current
SBE_EPIC["oxT"]     = '111'     #oxygen temperature
SBE_EPIC["oxML/L"]  = '65'      #oxygen ctd (seasoft calculated)
SBE_EPIC["sbeox0ML/L"] = '60'   #60:ml/l,65:umol/kg
SBE_EPIC["sbeox1ML/L"] = '-2060'   #(-2000 - primary key) 60:ml/l,65:umol/kg
SBE_EPIC["sbeox0Mm/Kg"] = '65' 
SBE_EPIC["sbox0Mm/Kg"] = '65' #different spelling of sbe/sb
SBE_EPIC["sbeox1Mm/Kg"] = '4221'#umol/kg 
SBE_EPIC["sbeox0PS"] = '62'     #oxygen % saturation
SBE_EPIC["sbeox1PS"] = '4220'     #CTD secondary oxygen % saturation
SBE_EPIC["sbeox0V"] = '5000'        #oxygen voltage
SBE_EPIC["sbeox1V"] = '5001'        #oxygen voltage

SBE_EPIC["bat"]     = '55'      #55 attn:m-1:f7.5:added for r2d2 ctd dat

#chlAM
SBE_EPIC["dm"]      = '10' 
SBE_EPIC["wetChConc"] = '937' 
SBE_EPIC["wetChAbs"] = '936' 
SBE_EPIC["volts_chlam"] = '935' 

#Fluorometers
SBE_EPIC["flS"]     = '906' 
SBE_EPIC["flC"]     = '906' 
SBE_EPIC["flCUVA"]  = '906' 
SBE_EPIC["flECO-AFL"]  = '903' 
SBE_EPIC["wetStar"] = '973' 
SBE_EPIC["SPFluor"] = '974' 
SBE_EPIC["FlSP"]    = '' 
SBE_EPIC["volts_fluor"] = '971' 

#turbidity
SBE_EPIC["turbWETntu0"] = '980' #NTU - Nephelemetric units
SBE_EPIC["obs"] = '980' #OBS, Backscatterance (D & A) [NTU]

#PAR
SBE_EPIC["par"]     = '905' 
SBE_EPIC["xmiss"]   = '904' 
SBE_EPIC["volts_par"]   = '916' 
SBE_EPIC["volts_trans"] = '107'

#Dimension Variables
SBE_EPIC["Depth"]       = '1'
SBE_EPIC["Latitude"]    = '500'
SBE_EPIC["LongitudeW"]  = '501' #positive West
SBE_EPIC["LongitudeE"]  = '502' #positive East

#Raw Voltage Variables with no identifier
SBE_EPIC["v0"] = ''
SBE_EPIC["v1"] = ''
SBE_EPIC["v2"] = ''
SBE_EPIC["v3"] = ''
SBE_EPIC["v4"] = '971'
SBE_EPIC["v5"] = ''
SBE_EPIC["v6"] = '971'
SBE_EPIC["flag"] = ''
SBE_EPIC["nbin"] = '9999'
SBE_EPIC["dz/dtM"] = '9998'

#Transmissometers
SBE_EPIC["CStarTr0"] = '904' #Beam Transmission, WET Labs C-Star [%]
SBE_EPIC["CStarAt0"] = '55' #Beam Attenuation, WET Labs C-Star [1/m]

#ph
SBE_EPIC["ph"] = '159' #IPHC ph value


#Niskin Bottles
SBE_EPIC["nb"] = '103'

"""------------------------------------------------------------------------------------"""

def test():
    import epic_key_codes as ekc 
    ekcl = ekc.EpicKeyCodes()
    for i, k in enumerate(SBE_EPIC.keys()):
        print 'SBE variable is: ' + k + ' which has been given EPIC.KEY ' + SBE_EPIC[k] + ''
        try:
            print 'The meta information in the epic.key file is [' + ' '.join(ekcl.epic_dic_call(SBE_EPIC[k])) + ']\n'
        except TypeError:
            print 'No key with epic.key ' + SBE_EPIC[k] + ' is in the epic.key file \n'
            
if __name__ == "__main__":
    test()
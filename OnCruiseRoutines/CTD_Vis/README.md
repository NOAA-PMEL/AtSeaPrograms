CTD_Vis
==========


Tools to load hydrographic data into pandas DataFrame and visualize (and some rudimentary methods for data pre-processing/analysis).

The pandas dataframe tools are heavily based on [python-ctd](https://github.com/ocefpaf/python-ctd).  Please view the README_orig.md document for information.

This module can load [SeaBird CTD (CNV)][SBE]

[SBE]: http://www.seabird.com/software/SBEDataProcforWindows.htm

Requires
--------
Pandas
numpy
matplotlib
netcdf4 (not currently available on windows Anaconda scientific package: use pythonxy)

Available Tools
---------------

See root directory for:

Wrapper Routines

* SEAbird_CTD.py - ingests seabird .cnv files for plotting   (does not require netcdf4)   
* NetCDF_CTD.py  - ingests EPIC flavored .nc files for plotting   

	Both of these make assumptions about what parameters to plot.  Use them as templates and import the plotting.py and ctd.py packages for custom plots.


		
Internal Routines of interest
-----------------------------

###### in ctd.py

**extrapolate2sfc()**   
copies data up to surface

**class defined time conversion**    
	
initialize with:
`timeinstance = DataTimes(time_str='jan 01 0001 00:00:00')`

retrieve python instance with:   
`timeinstance.get_python_date()`   

retrieve EPIC time with:   
`timeinstance.get_EPIC_date()`	


---
### Todo:

~~NetCDF Reader~~
~~NetCDF Generator~~

PMEL header files are not ingested or included to get metadata information (not available in raw .cnv files)

Will always build new files.  Need some append tools
send note to .nc files if data is extrapolated   

Some meta information is dependant on the file/folder names and the order in which they exist (e.g. /data/cruise/cast001.cnv) will give the cruise_name "cruise"

OnCruiseRoutines
================

## Research Group: EcoFOCI / PMEL

Tools to provide data analysis and visualization while on research cruises

!Warning!
---------

Although there may be great ideas and resources in this library of packages, it is intended more as an internal repository for information amongst the EcoFOCI research group.  Many files may make references to datasets not available to the general public.   

Packages are predominatly developed using the [Anaconda scientific python distribution](https://store.continuum.io/cshop/anaconda/) and assume user familiarity with this repository. 

The windows packaged form of Anaconda does not have the netcdf4 libraries or routines.  [Pythonxy](https://code.google.com/p/pythonxy) may be a more appropriate package.


---

### Included

###### Main Routines
* Seabird_CTD.py  **view .cnv**  uses packages in the CTD_Vis/ directory - many components come from the [python-ctd](https://github.com/ocefpaf/python-ctd) github repository from ocefpaf 
* NetCDF_CTD.py **view netcdf** uses packages in the CTD_Vis/ directory - many components come from the [python-ctd](https://github.com/ocefpaf/python-ctd) github repository from ocefpaf 
* CTD2NC.py **save .cnv to .nc** with EPIC standard metainformation

###### Directories
* EPICNetCDF/ a simple collection of packages to translate seabird variables (and potentially other measurements into EPIC.key codes)
* CTD_Vis/ collection of routines for plotting, analyzing, and storing seabird .cnv files as netcdf
* utilities/ a collection of packages with small jobs (concatanating btl files into a text file for Autosal calibrations, adding cruise log header information to a text file)


Example of Usage
----------------

Three methods to use from the command line:  
(NetCDF_CTD.py, CTD2NC.py, Seabird_CTD.py) 

1)	To analyze any casts in a directory:    
`python Seabird_CTD.py`    
>Please enter the abs path to the .cnv file: or path, file1, file2: 
   
		/absolute/pathtodata/, ctd001.cnv, ctd002.cnv

2)	To analyze one cast in a directory:    
`python Seabird_CTD.py`
>Please enter the abs path to the .cnv file: or path, file1, file2: 
   
		/absolute/pathtodata/ctd001.cnv

3)	To analyze all casts in a directory:    
`python Seabird_CTD.py`    
>Please enter the abs path to the .cnv file: or path, file1, file2: 
   
		/absolute/pathtodata/


Outputs
-------

In the local `images/` directory, `.png` files will be generated for:   

* histogram of all variables as a function of depth/pressure   
* boxplot of all variables as afunctio of depth/pressure   
* individual plots of each parameter as a function of depth/pressure
* primary temperature and salinity as a function of depth/pressure
* primary and secondary temperature and salinity as a function of depth/pressure
* primary, secondary O2 and %O2 as a function of depth/pressure

In the local `logs/` directory, `.md` files (markdown / plain text) reports will be generated for each cruise

In the local `ncfiles/` directory `.nc` files for each cast will be generated in a subfolder with the cruise identifier
	
#### Todo:
Add btl file netcdf creation, viewing and summary (overlay on .cnv)  
~~Add PMEL header edit options~~   
Build more tools for editing netcdf (appending or adding)
Applying calibrations (autosal)   
Add tools for CTD Transects
	
---

### License ###

The MIT License (MIT)

Copyright (c) 2013 Shaun Bell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
README
------

### Purpose

To provide a method to retrieve EPIC key codes from known variable names.  For more information on the EPIC standard vist the [EPIC Website][EPIC] (no longer actively supported)

For most recent key file:
`ftp://ftp.unidata.ucar.edu/pub/netcdf/Conventions/PMEL-EPIC/epic.key` 

[EPIC]: http://www.epic.noaa.gov/epic/document/convention.htm

### Included Files

epic_key_codes.py - python class for epic key codes
SBE_Epiclibrary.py - library of seabird variables and corresponding epic codes   
epic.key - text file with all EPIC codes   

### Usage

	from EPICNetCDF import SBE_Epiclibrary   
	from EPICNetCDF import epic_key_codes as ekc 

	ekc_instance = ekc.EpicKeyCodes(epic_text='/epic.key') 
		#epic key codes instance
	
	eekc_instance.epic_dic_call(code='42') #searches for code '42'
		# returns epic meta information
		
	eekc_instance.epic_dic_call(code=SBE_Epiclibrary['sal00'])
		# looks for sbe variable sal00 and returns epic meta information
		

__Updating SBE_Epiclibrary:__   
as the file is just a dictionary of variable names and epic codes, new variables can be added at any time if epic keys are known.




### License ###

The EPIC format is a product/standard of NOAA/PMEL

EPIC libraries and tools (also associated with ferret) are licensed under NOAA's terms and conditions.

Seabird variables are a product of Seabird instruments and are licensed under Seabirds terms and conditions.

The routines within make use of EPIC public information and are under the:

The MIT License (MIT)

Copyright (c) 2013 Shaun Bell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
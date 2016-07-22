#!/usr/bin/env 
"""
 Program:
 --------
    get_btl.py
    
 Usage:
 ------
    you can either input the path to the *.btl files at command prompt or feed them in
    as the first option when running at the command line.
    
    python get_btl.py '/full/path/to/ctd*.btl'
 
 Purpose:
 --------
    From raw ctd *.btl files, gather and concatenate all data into one tabbed output file
    
 Notes:
 ------
   Using Anaconda packaged Python
"""

import datetime, sys, os, csv


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 07)
__modified__ = datetime.datetime(2014, 9, 3)
__version__  = "0.1.0"
__status__   = "Development"

"""--------------------------------Data Source------------------------------------------"""

def get_files(data_path):
    print "Reading: " + data_path + "\n"
    files = [data_path + x for x in os.listdir(data_path) if x.endswith('.btl')]
    cast = [x.split('/')[-1].split('.')[0] for x in files]
    cruise = [x.split('/')[-3] for x in files] #assumes using btl fies wih updated headers
    return (files, cruise, cast)
    
"""--------------------------------Data Read------------------------------------------"""

def read_ctd_btl(ifile):
    """ """
    btl_data = []
    time = []
    headerline1 = []
    with open(ifile, 'r') as fhandle:
        for lines in fhandle:
            if not ((lines.split()[0] == '@') or (lines.split()[0] == '#') or (lines.split()[0] == '\*')):
                #skip comment lines
                if (lines.strip().split()[0] == 'Bottle'):
                    #first headerline - 
                    headerline1 = lines.strip() 
                    headerline1 = headerline1.replace('Sal11Sbeox0Mm/Kg', 'Sal11 Sbeox0Mm/Kg')
                    headerline1 = headerline1.replace('Sbeox0PSSbeox1Mm/Kg', 'Sbeox0PS Sbeox1Mm/Kg')
                    headerline1 = headerline1.split()
                elif (lines.strip().split()[0] == 'Position'):
                    #second headerline - first value is actually a continuation of previous line
                    headerline2 = lines.strip().split() 
                    
                else:
                    #list of lists based on btl number as identifier
                    #only repors averages
                    if (lines.split()[-1] == '(avg)'):
                        btl_data.append(lines.strip().split())
                    elif (lines.split()[-1] == '(sdev)'):
                        time.append(lines.strip().split()[0])
                    
        #with statement auto closes file    
    if not headerline1:
        print """headers ar not found in file, assuming format:
        Bottle        Date      Sal00      Sal11Sbeox0Mm/Kg   Sbeox0PSSbeox1Mm/Kg  Sigma-t00       PrDM      DepSM      T090C      T190C    WetStar        Par         V0         V6       Scan
        Position        Time  """  
        headerline2 = []                                                                                                                                                                 
    
    return(headerline1 + headerline2, btl_data, time)
    
"""--------------------------------Output Generation-----------------------------------"""

def ctd_btl_output(data_path, file_ending, cruise, data, time, header, cast, index, has_btl=''):
    output_file = data_path + cruise + file_ending
    print "Data can be found at " + data_path + " as " + output_file + " \n"

    if not os.path.isfile(output_file):
        with open(output_file, 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL) 
            #write header
            #csvwriter.writerow(['cast', 'date', 'time', 'nb', 'pres', 't1', 't2', 's1', 's2', 'par', 'WetStar', 'bottleID'])
            csvwriter.writerow(['cast', 'date', 'time', 'nb'] + header[2:-3])
            for d, v in enumerate(data):
                csvwriter.writerow([cast[index], v[2] + '-' + v[1] + '-' + v[3],
                                    time[d], v[0]] + v[4:-2]) #,has_btl
    else:
        with open(output_file, 'ab') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL) 
            for d, v in enumerate(data):
                csvwriter.writerow([cast[index], v[2] + '-' + v[1] + '-' + v[3],
                                    time[d], v[0]] + v[4:-2]) #,has_btl


"""--------------------------------Main-----------------------------------------------"""


def report(user_in, user_out):

    cruiseID = user_in.split('/')[-3]
    leg = cruiseID.lower().split('L')
    if len(leg) == 1:
        cruiseID = leg[0]
        leg = ''
    else:
        cruiseID = leg[0] + 'L' + leg[-1]

    
    (btl_files, cruise, cast) = get_files(user_in)
    
    for i, ifile in enumerate(btl_files):
        (header , btl_data, time) = read_ctd_btl(ifile)
        #the formating and output is not smart - it is hard coded in the ctd_btl_output module above
        ctd_btl_output(user_out, '.report_btl', cruiseID, btl_data, time, header, cast, i)
        
    processing_complete = True
    return processing_complete

if __name__ == '__main__':

    user_in = raw_input("Please enter the abs path to the .btl files: or \n path, file1, file2: ")
    user_out = user_in
    report(user_in, user_out)
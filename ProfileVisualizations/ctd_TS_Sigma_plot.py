#!/usr/bin/env

"""
ctd_2TSSigma_plot.py

Plot data from cruises

Currently
---------
timeseries of ship observations
ctd plots

Input - CruiseID

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import os
import argparse


#Science Stack
import numpy as np
from netCDF4 import Dataset

#Visual Packages
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# User Stack
from utilities import ncutilities as ncutil

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 06, 24)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Plots', 'Cruise', 'QC'

"""--------------------------------netcdf Routines---------------------------------------"""
def from_netcdf(infile):
    """ Uses ncreadfile_dic which returns a dictionary of all data from netcdf"""

    ###nc readin/out
    nchandle = ncutil.ncopen(infile)
    params = ncutil.get_vars(nchandle) #gets all of them

    global_atts = ncutil.get_global_atts(nchandle)
    
    ncdata = ncutil.ncreadfile_dic(nchandle, params)
    ncutil.ncclose(nchandle)
    
    return (ncdata, params, global_atts)

"""--------------------------------time Routines---------------------------------------"""

def date2pydate(file_time, file_time2=None, file_flag='EPIC'):

    if file_flag == 'EPIC':
        ref_time_py = datetime.datetime.toordinal(datetime.datetime(1968, 5, 23))
        ref_time_epic = 2440000
    
        offset = ref_time_epic - ref_time_py
    
       
        try: #if input is an array
            python_time = [None] * len(file_time)

            for i, val in enumerate(file_time):
                pyday = file_time[i] - offset 
                pyfrac = file_time2[i] / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
                python_time[i] = (pyday + pyfrac)

        except:
    
            pyday = file_time - offset 
            pyfrac = file_time2 / (1000. * 60. * 60.* 24.) #milliseconds in a day
        
            python_time = (pyday + pyfrac)
        
    else:
        print "time flag not recognized"
        sys.exit()
        
    return np.array(python_time)    
"""--------------------------------Plot Routines---------------------------------------"""

def twovar_minmax_plotbounds(var1,var2):
    """expects missing values to be np.nan"""
    if np.isnan(var1).all() and np.isnan(var2).all():
        min_bound = -1
        max_bound = 1
    elif np.isnan(var1).all() and not np.isnan(var2).all():
        min_bound = var2[~np.isnan(var2)].min()
        max_bound = var2[~np.isnan(var2)].max()
    elif np.isnan(var2).all() and not np.isnan(var1).all():
        min_bound = var1[~np.isnan(var1)].min()
        max_bound = var1[~np.isnan(var1)].max()
    else:
        min_bound = np.min((var1[~np.isnan(var1)].min(), var2[~np.isnan(var2)].min()))
        max_bound = np.max((var1[~np.isnan(var1)].max(), var2[~np.isnan(var2)].max()))
        
    return (min_bound, max_bound)

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.itervalues():
        sp.set_visible(False)


def plot_prisec_TSSigma(dep,T,T2,S,S2,Sigma,ptitle=""):
    """
    Plot PRI/SEC TSSIGMA
    
    """
    max_xticks = 5
    min_rangeT = 1.

    ### find values that are "missing" - 1e35 and make np.nan
    T[np.where(T>=1e34)]=np.nan
    T2[np.where(T2>=1e34)]=np.nan
    S[np.where(S>=1e34)]=np.nan
    S2[np.where(S2>=1e34)]=np.nan
    Sigma[np.where(Sigma>=1e34)]=np.nan

    #pri temp
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    tplot = ax.plot(T,dep)
    plt.setp(tplot, 'color', 'red', 'linestyle', '-', 'linewidth', .5)
    tplot = ax.plot(T2,dep)
    plt.setp(tplot, 'color', 'magenta', 'linestyle', '--', 'linewidth', .5)
    (min_bound, max_bound) = twovar_minmax_plotbounds(T,T2)
    plt.xlim( (min_bound - 0.1, max_bound + 0.1) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
    ax.invert_yaxis()
    plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
    plt.xlabel('Temperature (C)', fontsize=12, fontweight='bold')
    xloc = plt.MaxNLocator(max_xticks)
    ax.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax.xaxis.set_major_formatter(fmt)
    ax.tick_params(axis='both', which='major', labelsize=12)

    #salinity
    
    ax2 = ax.twiny()
    tplot = ax2.plot(S,dep)
    plt.setp(tplot, 'color', 'blue', 'linestyle', '-', 'linewidth', .5)
    tplot = ax2.plot(S2,dep)
    plt.setp(tplot, 'color', 'cyan', 'linestyle', '--', 'linewidth', .5)
    (min_bound, max_bound) = twovar_minmax_plotbounds(S,S2)
    plt.xlim( (min_bound - 0.01, max_bound + 0.01) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
    plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
    plt.xlabel('Salinity (PSU)', fontsize=12, fontweight='bold')
    xloc = plt.MaxNLocator(max_xticks)
    ax2.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax2.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax2.xaxis.set_major_formatter(fmt)
    ax2.tick_params(axis='x', which='major', labelsize=12)

    ax3 = ax.twiny()
    ax3.spines["top"].set_position(("axes", 1.07))
    make_patch_spines_invisible(ax3)
    # Second, show the right spine.
    ax3.spines["top"].set_visible(True)
    tplot = ax3.plot(Sigma,dep)
    plt.setp(tplot, 'color', 'black', 'linestyle', '-', 'linewidth', .5)
    if np.isnan(Sigma).all():
        plt.xlim(-1,1)
    elif np.isnan(Sigma).any():
        plt.xlim( (Sigma[~np.isnan(Sigma)].min() - 0.01, Sigma[~np.isnan(Sigma)].max() + 0.01) )
    else:
        plt.xlim( (Sigma[~np.isnan(Sigma)].min() - 0.01, Sigma[~np.isnan(Sigma)].max() + 0.01) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
    plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
    plt.xlabel('SigmaT (kg/m**3)', fontsize=12, fontweight='bold')
    xloc = plt.MaxNLocator(max_xticks)
    ax3.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax3.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax3.xaxis.set_major_formatter(fmt)
    ax3.invert_yaxis()
    ax3.tick_params(axis='x', which='major', labelsize=12)

    textstr = [[r'$Pri T$', 'red'],
               [r'$Sec T$', 'magenta'],
               [r'$Pri S$', 'blue'],
               [r'$Sec S$', 'cyan'],
               [r'$SigmaT$', 'black']]
    ax.text(0.85, 0.60, textstr[0][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[0][1])
    ax.text(0.85, 0.58, textstr[1][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[1][1])
    ax.text(0.85, 0.55, textstr[2][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[2][1])
    ax.text(0.85, 0.53, textstr[3][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[3][1])
    ax.text(0.85, 0.51, textstr[4][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[4][1])
   
    
      
    t = fig.suptitle(ptitle, fontsize=12, fontweight='bold')
    t.set_y(1.08)
    return fig    

def plot_pri_TSSigma(dep,T,S,Sigma,ptitle=""):
    """
    Plot Primary TSSigma
    
    """
    max_xticks = 5
    min_rangeT = 1.

        
    #pri temp
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    tplot = ax.plot(T,dep)
    plt.setp(tplot, 'color', 'red', 'linestyle', '-', 'linewidth', .5)
    if (T == 1e35).all():
        plt.xlim(-1,1)
    elif (T == 1e35).any():
        plt.xlim( (T[T != 1e35].min() - 0.1, T[T != 1e35].max() + 0.1) )
    else:
        plt.xlim( (T[T != 1e35].min() - 0.1, T[T != 1e35].max() + 0.1) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
    ax.invert_yaxis()
    plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
    plt.xlabel('Temperature (C)', fontsize=12, fontweight='bold')
    xloc = plt.MaxNLocator(max_xticks)
    ax.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax.xaxis.set_major_formatter(fmt)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True)

    #pri salinity
    
    ax2 = ax.twiny()
    tplot = ax2.plot(S,dep)
    plt.setp(tplot, 'color', 'blue', 'linestyle', '-', 'linewidth', .5)
    if (S == 1e35).all():
        plt.xlim(-1,1)
    elif (S == 1e35).any():
        plt.xlim( (S[S != 1e35].min() - 0.1, S[S != 1e35].max() + 0.1) )
    else:
        plt.xlim( (S[S != 1e35].min() - 0.1, S[S != 1e35].max() + 0.1) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
    plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
    plt.xlabel('Salinity (PSU)', fontsize=12, fontweight='bold')
    xloc = plt.MaxNLocator(max_xticks)
    ax2.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax2.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax2.xaxis.set_major_formatter(fmt)
    ax2.tick_params(axis='x', which='major', labelsize=12)
    ax2.grid(True)

    ax3 = ax.twiny()
    ax3.spines["top"].set_position(("axes", 1.07))
    make_patch_spines_invisible(ax3)
    # Second, show the right spine.
    ax3.spines["top"].set_visible(True)
    tplot = ax3.plot(Sigma,dep)
    plt.setp(tplot, 'color', 'black', 'linestyle', '-', 'linewidth', .5)
    if (Sigma == 1e35).all():
        plt.xlim(-1,1)
    elif (Sigma == 1e35).any():
        plt.xlim( (Sigma[Sigma != 1e35].min() - 0.01, Sigma[Sigma != 1e35].max() + 0.01) )
    else:
        plt.xlim( (Sigma[Sigma != 1e35].min() - 0.01, Sigma[Sigma != 1e35].max() + 0.01) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
    plt.ylabel('Depth (dB)', fontsize=12, fontweight='bold')
    plt.xlabel('SigmaT (kg/m**3)', fontsize=12, fontweight='bold')
    xloc = plt.MaxNLocator(max_xticks)
    ax3.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax3.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax3.xaxis.set_major_formatter(fmt)
    ax3.invert_yaxis()
    ax3.tick_params(axis='x', which='major', labelsize=12)


    textstr = [[r'$Pri T$', 'red'],
               [r'$Pri S$', 'blue'],
               [r'$SigmaT$', 'black']]
    ax.text(0.85, 0.60, textstr[0][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[0][1])
    ax.text(0.85, 0.58, textstr[1][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[1][1])
    ax.text(0.85, 0.55, textstr[2][0], transform=ax.transAxes, fontsize=12,
        verticalalignment='top', color=textstr[2][1])

   
    
      
    t = fig.suptitle(ptitle, fontsize=12, fontweight='bold')
    t.set_y(1.08)
    return fig    

        

"""------------------------------------- Main -----------------------------------------"""

parser = argparse.ArgumentParser(description='CTD Pri/Sec TSSigma plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,help='full path to directory of processed nc files')
parser.add_argument('NumTempSensors', metavar='NumTempSensors', type=int, help='number of T/C sensors (1, 2)')
          
args = parser.parse_args()

nc_path = args.DataPath

if not '.nc' in nc_path:
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]
else:
    nc_path = [nc_path,]
    
    
if args.NumTempSensors == 1:
    for ncfile in sorted(nc_path):
     
        print "Working on file %s " % ncfile
        (ncdata, params, g_atts) = from_netcdf(ncfile)

        if not os.path.exists('images/' + g_atts['CRUISE']):
            os.makedirs('images/' + g_atts['CRUISE'])
        if not os.path.exists('images/' + g_atts['CRUISE'] + '/pri_TSSigma/'):
            os.makedirs('images/' + g_atts['CRUISE'] + '/pri_TSSigma/')

        xtime = date2pydate(ncdata['time'],ncdata['time2'])[0]
        cast_time = datetime.datetime.fromordinal(int(xtime)) + datetime.timedelta(xtime - int(xtime))
        ptitle = ("Plotted on: {0} from {1} \n\n"
                  "Cruise: {2} Cast: {3}  Stn: {4} \n"
                  "Lat: {5:3.3f}  Lon: {6:3.3f} at {7}\n").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                                  ncfile.split('/')[-1], g_atts['CRUISE'], g_atts['CAST'], g_atts['STATION_NAME'], 
                                                  ncdata['lat'][0], ncdata['lon'][0], datetime.datetime.strftime(cast_time,"%Y-%m-%d %H:%M GMT" ))
   


        ### pri/sec temp, sal, sigma
    

        fig = plot_pri_TSSigma(ncdata['dep'],ncdata['T_28'][0,:,0,0],\
        ncdata['S_41'][0,:,0,0],ncdata['ST_70'][0,:,0,0], ptitle)

        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )
        plt.savefig('images/' + g_atts['CRUISE'] + '/pri_TSSigma/' + ncfile.split('/')[-1].split('.')[0] + '_plot_pri_TSSigma.png', bbox_inches='tight', dpi = (300))
        plt.close()

elif args.NumTempSensors == 2:

    for ncfile in sorted(nc_path):
     
        print "Working on file %s " % ncfile
        (ncdata, params, g_atts) = from_netcdf(ncfile)

        if not os.path.exists('images/' + g_atts['CRUISE']):
            os.makedirs('images/' + g_atts['CRUISE'])
        if not os.path.exists('images/' + g_atts['CRUISE'] + '/prisec_TSSigma/'):
            os.makedirs('images/' + g_atts['CRUISE'] + '/prisec_TSSigma/')

        try:
            g_atts['STATION_NAME'] = g_atts['STATION_NAME']
        except:
            g_atts['STATION_NAME'] = 'NA'
    
        xtime = date2pydate(ncdata['time'],ncdata['time2'])[0]
        cast_time = datetime.datetime.fromordinal(int(xtime)) + datetime.timedelta(xtime - int(xtime))
        ptitle = ("Plotted on: {0} from {1} \n\n"
                  "Cruise: {2} Cast: {3}  Stn: {4} \n"
                  "Lat: {5:3.3f}  Lon: {6:3.3f} at {7}\n").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                                  ncfile.split('/')[-1], g_atts['CRUISE'], g_atts['CAST'], g_atts['STATION_NAME'], 
                                                  ncdata['lat'][0], ncdata['lon'][0], datetime.datetime.strftime(cast_time,"%Y-%m-%d %H:%M GMT" ))
    


        ### pri/sec temp, sal, sigma

        fig = plot_prisec_TSSigma(ncdata['dep'],ncdata['T_28'][0,:,0,0],ncdata['T2_35'][0,:,0,0],\
        ncdata['S_41'][0,:,0,0],ncdata['S_42'][0,:,0,0],ncdata['ST_70'][0,:,0,0], ptitle)

        DefaultSize = fig.get_size_inches()
        fig.set_size_inches( (DefaultSize[0], DefaultSize[1]*2) )

        plt.savefig('images/' + g_atts['CRUISE'] + '/prisec_TSSigma/' + ncfile.split('/')[-1].split('.')[0] + '_plot_2TSSigma.png', bbox_inches='tight', dpi = (300))
        plt.close()

else:
    print "Choose 1 or 2 T/C sensor pairs"

    


#!/usr/bin/env python

"""
PostCruise_editsfcextend.py

manually choose point from whic to extrapolate to sfc
only shows top 30m

Input - CruiseID

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import os
import shutil
import argparse

#Science Stack
import numpy as np
from netCDF4 import Dataset

#Visual Packages
import matplotlib as mpl
#mpl.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# User Stack
from utilities import ncutilities as ncutil

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 06, 24)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'CTD', 'Plots', 'Cruise', 'QC'

        
"""--------------------------------netcdf Routines---------------------------------------"""
def from_netcdf(infile):
    """ Uses ncreadfile_dic which returns a dictionary of all data from netcdf"""

    ###nc readin/out
    nchandle = Dataset(infile,'a')
    params = ncutil.get_vars(nchandle) #gets all of them

    global_atts = ncutil.get_global_atts(nchandle)
    
    ncdata = ncutil.ncreadfile_dic(nchandle, params)
    
    return (nchandle, ncdata, params, global_atts)

"""-------------------------------- MPL Events ---------------------------------------"""


def onpick1(event):
    #if isinstance(event.artist, Line2D):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    print event.inaxes
    print(' :', zip(np.take(xdata, ind), np.take(ydata, ind)))

    
def line_picker(line, mouseevent):
    """
    find the points within a certain distance from the mouseclick in
    data coords and attach some extra attributes, pickx and picky
    which are the data points that were picked
    """
    if mouseevent.xdata is None: return False, dict()
    xdata = line.get_xdata()
    ydata = line.get_ydata()
    label = line.get_label()
    maxd = 0.5
    d = np.sqrt((xdata-mouseevent.xdata)**2. + (ydata-mouseevent.ydata)**2.)
    if (mouseevent.button == 1) and ((label == 'T (sec)') or (label == 'S (sec)')):
        return False, dict()
    if (mouseevent.button == 3) and ((label == 'T (pri)') or (label == 'S (pri)')):
        return False, dict()
    if (mouseevent.button == 'up') or (mouseevent.button == 'down'):
        return False, dict()
                    
    ind = np.nonzero(np.less_equal(d, maxd))
    if len(ind):
        pickx = np.take(xdata, ind)
        picky = np.take(ydata, ind)
        markertype = 1e35
        props = dict(ind=ind, pickx=pickx.tolist()[0], picky=picky.tolist()[0], label=label, markertype=markertype)
        return True, props
    else:
        return False, dict()

def onpick2(event):
    with open(logfile, "a") as lfile:
        lfile.write(('extraptosfc: {0} {1} {2} {3}\n').format(event.pickx, event.picky, event.label, event.markertype)) 
        print('extraptosfc:', event.pickx, event.picky, event.label, event.markertype)    
    #copy ncfile to be modified
    shutil.copy (ncfile, "/".join(ncfile.split('/')[:-1])+'/orig/'+ncfile.split('/')[-1]+'.ed_'+datetime.datetime.now().strftime('%y%m%d_%H%M'))
    ncdata[EPIC_VAR][0,:event.picky[0],0,0] = ncdata[EPIC_VAR][0,event.picky[0],0,0]
    nchandle.variables[EPIC_VAR][:] = ncdata[EPIC_VAR][:]
    #nchandle.setncattr('SFC_EXTEND','Extrapolated to SFC from ' + str(event.picky[0]) + 'm')
    nchandle.close()

    
"""--------------------------------Plot Routines---------------------------------------"""

def plot_prisec_TSSig_threepannel(dep,T1,T2,S1,S2,Sig1,Sig2,ptitle=""):
    """
    Plot CTD temperature, salinity, sigma-t. (both sensors)
    

    """
    max_xticks = 5
    min_rangeT = 1.
    min_rangeS = 0.05
    min_rangeSig = 0.1
    
    sig1_inv_ind = (np.diff(Sig1) < -0.02) #mark bottom of inversion
    sig2_inv_ind = (np.diff(Sig2) < -0.02)


    #temperature
    
    fig = plt.figure()
    ax1 = plt.subplot2grid((3,21), (0,0), colspan=7, rowspan=3)
    tplot1, = ax1.plot(T2,dep, picker=line_picker, label="T (sec)")
    plt.setp(tplot1, 'color', 'k', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    tplot2, = ax1.plot(T1,dep, picker=line_picker, label="T (pri)")
    plt.setp(tplot2, 'color', 'r', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    ax1.grid(True)
    if (T1.max() - T1.min()) < min_rangeT:
        plt.xlim( (T1.min() - min_rangeT/2, T1.max() + min_rangeT/2) )
    plt.ylim(-5,30)
    ax1.invert_yaxis()
    plt.ylabel('Depth (dB)')
    plt.xlabel('Temp(C)')
    xloc = plt.MaxNLocator(max_xticks)
    ax1.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax1.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax1.xaxis.set_major_formatter(fmt)
    ax1.yaxis.set_minor_locator


    #salinity
    
    ax2 = plt.subplot2grid((3,21), (0,7), colspan=7, rowspan=3)
    tplot3 = ax2.plot(S2,dep, picker=line_picker, label="S (sec)")
    plt.setp(tplot3, 'color', 'k', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    tplot4 = ax2.plot(S1,dep, picker=line_picker, label="S (pri)")
    plt.setp(tplot4, 'color', 'b', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    ax2.grid(True)
    if (S1.max() - S1.min()) < min_rangeS:
        plt.xlim( (S1.min() - min_rangeS/2, S1.max() + min_rangeS/2) )
    plt.ylim(-5,30)
    ax2.invert_yaxis()
    plt.ylabel('Depth (dB)')
    plt.xlabel('Salinity(PSU)')
    xloc = plt.MaxNLocator(max_xticks)
    ax2.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax2.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax2.xaxis.set_major_formatter(fmt)
    ax2.yaxis.set_minor_locator(AutoMinorLocator(5))


    #sigma-t
    
    ax3 = plt.subplot2grid((3,21), (0,14), colspan=7, rowspan=3)

    
    tplot = ax3.plot(Sig2,dep)
    plt.setp(tplot, 'color', 'k', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    tplot = ax3.plot(Sig1,dep)
    plt.setp(tplot, 'color', 'c', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    tplot = ax3.plot(Sig1[sig1_inv_ind],dep[1:][sig1_inv_ind])
    plt.setp(tplot, 'color', 'r', 'linestyle', 'none', 'marker', 'o', 'markersize', 10, markeredgecolor = 'yellow', mfc='none')
    tplot = ax3.plot(Sig2[sig2_inv_ind],dep[1:][sig2_inv_ind])
    plt.setp(tplot, 'color', 'r', 'linestyle', 'none', 'marker', 'o', 'markersize', 10, markeredgecolor = 'yellow', mfc='none')
    ax3.grid(True)
    if (Sig1.max() - Sig1.min()) < min_rangeSig:
        plt.xlim( (Sig1.min() - min_rangeSig/2, Sig1.max() + min_rangeSig/2) )
    plt.ylim(-5,30)
    ax3.invert_yaxis()
    plt.ylabel('Depth (dB)')
    plt.xlabel('Sigma-T')
    xloc = plt.MaxNLocator(max_xticks)
    ax3.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax3.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax3.xaxis.set_major_formatter(fmt)
    ax3.yaxis.set_minor_locator(AutoMinorLocator(5))
    
    
    textstr = [[r'$T (pri)$', 'red'],
               [r'$T (sec)$', 'black'],
               [r'$S (pri)$', 'blue'],
               [r'$S (sec)$', 'black'],
               [r'$\sigma (pri)$', 'cyan'],
               [r'$\sigma (sec)$', 'black']]
    ax1.text(0.05, 0.60, textstr[0][0], transform=ax1.transAxes, fontsize=10,
        verticalalignment='top', color=textstr[0][1])
    ax1.text(0.05, 0.58, textstr[1][0], transform=ax1.transAxes, fontsize=10,
        verticalalignment='top', color=textstr[1][1])
    ax2.text(0.05, 0.55, textstr[2][0], transform=ax2.transAxes, fontsize=10,
        verticalalignment='top', color=textstr[2][1])
    ax2.text(0.05, 0.53, textstr[3][0], transform=ax2.transAxes, fontsize=10,
        verticalalignment='top', color=textstr[3][1])
    ax3.text(0.05, 0.50, textstr[4][0], transform=ax3.transAxes, fontsize=10,
        verticalalignment='top', color=textstr[4][1])
    ax3.text(0.05, 0.48, textstr[5][0], transform=ax3.transAxes, fontsize=10,
        verticalalignment='top', color=textstr[5][1])

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    return fig    
    
def plot_1var(dep,T1,T2,inputvar,inputvar_name,ptitle=""):
    """
    Plot CTD temperature, and chosen var
    

    """
    max_xticks = 5
    min_rangeT = 1.

    
    ####### temperature
    
    fig = plt.figure(figsize=(8, 16))
    ax1 = plt.subplot2grid((3,20), (0,0), colspan=10, rowspan=3)
    tplot1, = ax1.plot(T2,dep, picker=line_picker, label="T (sec)")
    plt.setp(tplot1, 'color', 'k', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    tplot2, = ax1.plot(T1,dep, picker=line_picker, label="T (pri)")
    plt.setp(tplot2, 'color', 'r', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    ax1.grid(True)
    if (T1.max() - T1.min()) < min_rangeT:
        plt.xlim( (T1.min() - min_rangeT/2, T1.max() + min_rangeT/2) )
    plt.ylim(-5,30)
    ax1.invert_yaxis()
    plt.ylabel('Depth (dB)')
    plt.xlabel('Temp(C)')
    xloc = plt.MaxNLocator(max_xticks)
    ax1.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax1.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax1.xaxis.set_major_formatter(fmt)
    ax1.yaxis.set_minor_locator


    # user chosen variable
    
    ax2 = plt.subplot2grid((3,20), (0,10), colspan=10, rowspan=3)
    tplot3 = ax2.plot(inputvar,dep, picker=line_picker, label=inputvar_name)
    plt.setp(tplot3, 'color', 'b', 'linestyle', '-', 'linewidth', .1, 'marker', '.', 'markersize', 4)
    ax2.grid(True)
    plt.xlim(inputvar.min(), inputvar.max())
    plt.ylim(-5,30)
    ax2.invert_yaxis()
    plt.ylabel('Depth (dB)')
    plt.xlabel(inputvar_name)
    xloc = plt.MaxNLocator(max_xticks)
    ax2.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax2.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax2.xaxis.set_major_formatter(fmt)
    ax2.yaxis.set_minor_locator(AutoMinorLocator(5))

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    return fig   
"""------------------------------------- System -----------------------------------------"""

def createDir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
"""------------------------------------- Main -----------------------------------------"""

parser = argparse.ArgumentParser(description='EPIC PAR QC')
parser.add_argument('inputdir', metavar='inputdir', type=str,
               help='EPIC nc files input directory or file')
parser.add_argument('EPIC_VAR', metavar='EPIC_VAR', type=str,
               help='EPIC VAR ID (PAR_905)')

args = parser.parse_args()
nc_path = args.inputdir
EPIC_VAR = args.EPIC_VAR

if not '.nc' in nc_path:
    logfile = nc_path + "manual_edit_sfcextend.txt"
    createDir(nc_path+'orig/')
    nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]
else:
    logfile = "/".join(nc_path.split('/')[:-1]) + "/manual_edit_sfcextend.txt"
    createDir("/".join(nc_path.split('/')[:-1])+'/orig/')
    nc_path = [nc_path,]
    
    
for ncfile in nc_path:
     
    print "Working on file %s " % ncfile
    with open(logfile, "a") as lfile:
        lfile.write("Working on file %s \n" % ncfile)
    
    (nchandle, ncdata, params, g_atts) = from_netcdf(ncfile)


    
    ptitle = ("Plotted on: {0} \n from {1}"
              "Cast: {2}  Stn: {3} \n"
              "Lat: {4:3.3f}  Lon: {5:3.3f} \n").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                              ncfile.split('/')[-1], g_atts['CAST'], g_atts['STATION_NAME'], 
                                              ncdata['lat'][0], ncdata['lon'][0] )

    try: #two sigma values
        fig = plot_1var(ncdata['dep'],ncdata['T_28'][0,:,0,0],ncdata['T2_35'][0,:,0,0],ncdata[EPIC_VAR][0,:,0,0],\
        EPIC_VAR, ptitle)

        fig.canvas.mpl_connect('pick_event', onpick2 )
        plt.show()
    except:
        pass
    
    """
    ### pri/sec temp, sal, sigma
    try: #two sigma values
        fig = plot_prisec_TSSig_threepannel(ncdata['dep'],ncdata['T_28'][0,:,0,0],ncdata['T2_35'][0,:,0,0],ncdata['S_41'][0,:,0,0],\
        ncdata['S_42'][0,:,0,0],ncdata['ST_70'][0,:,0,0],ncdata['ST_2070'][0,:,0,0], ptitle)

        #fig.canvas.mpl_connect('key_press_event', press)
        fig.canvas.mpl_connect('pick_event', onpick2 )
        plt.show()

    except KeyError: #no secondary density
        fig = plot_prisec_TSSig_threepannel(ncdata['dep'],ncdata['T_28'][0,:,0,0],ncdata['T2_35'][0,:,0,0],ncdata['S_41'][0,:,0,0],\
        ncdata['S_42'][0,:,0,0],ncdata['ST_70'][0,:,0,0], ptitle)

        fig.canvas.mpl_connect('pick_event', onpick2 )
        plt.show()
    """

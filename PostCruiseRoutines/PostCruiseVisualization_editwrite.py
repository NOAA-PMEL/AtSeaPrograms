#!/usr/bin/env

"""
PostCruiseVisualization_editwrite.py

plot EPIC netcdf CTD data for editing

Currently
---------
ctd plots

Input - CruiseID

Using Anaconda packaged Python 
"""

#System Stack
import datetime
import os
import sys
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

"""-------------------------------- MPL Events ---------------------------------------"""

"""
def onclick(event):
    if event.inaxes and not (plt.get_current_fig_manager().toolbar.mode == 'zoom rect' or
    plt.get_current_fig_manager().toolbar.mode == 'pan/zoom'):
        with open(logfile, "a") as lfile:
            if event.button == 1:
                lfile.write(('DomainBegin: {0} {1} Pri\n').format(np.round(event.xdata), np.round(event.ydata))) 
                print('DomainBegin:', np.round(event.xdata), np.round(event.ydata), 'Pri') 
            if event.button == 3:
                lfile.write(('DomainBegin: {0} {1} Sec\n').format(np.round(event.xdata), np.round(event.ydata))) 
                print('DomainBegin:', np.round(event.xdata), np.round(event.ydata), 'Sec') 
            
def onrelease(event):
    if event.inaxes and not (plt.get_current_fig_manager().toolbar.mode == 'zoom rect' or
    plt.get_current_fig_manager().toolbar.mode == 'pan/zoom'):
        with open(logfile, "a") as lfile:
            if event.button == 1:
                lfile.write(('DomainEnd: {0} {1} Pri\n').format(np.round(event.xdata), np.round(event.ydata))) 
                print('DomainEnd:', np.round(event.xdata), np.round(event.ydata), 'Pri') 
            if event.button == 3:
                lfile.write(('DomaDomainEndinBegin: {0} {1} Sec\n').format(np.round(event.xdata), np.round(event.ydata))) 
                print('DomainEnd:', np.round(event.xdata), np.round(event.ydata), 'Sec') 
"""
    
def press(event):
    if event.key == 'x':
        print('MarkType', 'EOF')
        sys.exit()

    else:
        print('MarkType', event.key)
    
def line_picker(line, mouseevent):
    """
    find the points within a certain distance from the mouseclick in
    data coords and attach some extra attributes, pickx and picky
    which are the data points that were picked
    """
    if mouseevent.xdata is None: return False, dict(typelabel='blank')
    xdata = line.get_xdata()
    ydata = line.get_ydata()
    label = line.get_label()
    maxd = 0.5
    d = np.sqrt((xdata-mouseevent.xdata)**2. + (ydata-mouseevent.ydata)**2.)
    if (mouseevent.button == 1) and ((label == 'T (sec)') or (label == 'S (sec)')):
        return False, dict(typelabel='blank')
    if (mouseevent.button == 3) and ((label == 'T (pri)') or (label == 'S (pri)')):
        return False, dict(typelabel='blank')
    if (mouseevent.button == 'up') or (mouseevent.button == 'down'):
        return False, dict(typelabel='blank')
                    
    if (mouseevent.button == 2): #interp to surface from here
        ind = np.nonzero(np.less_equal(d, maxd))
        if len(ind):
            pickx = np.take(xdata, ind)
            picky = np.take(ydata, ind)
            markertype = 1e35
            onepointinterp = 1e35
            typelabel = 'extraptosfc'
            props = dict(ind=ind, pickx=pickx.tolist()[0], picky=picky.tolist()[0], \
                label=label, markertype=markertype, onepointinterp=onepointinterp, typelabel=typelabel)
            return True, props
    
    ind = np.nonzero(np.less_equal(d, maxd))
    if len(ind):
        pickx = np.take(xdata, ind)
        picky = np.take(ydata, ind)
        markertype = 1e35
        typelabel = 'onepointinterp'
        onepointinterp = np.interp(picky,(np.take(ydata, ind[0][0]-1),np.take(ydata, ind[0][0]+1)),\
                        (np.take(xdata, ind[0][0]-1),np.take(xdata, ind[0][0]+1)))[0][0]
        props = dict(ind=ind, pickx=pickx.tolist()[0], picky=picky.tolist()[0], \
            label=label, markertype=markertype, onepointinterp=onepointinterp, typelabel=typelabel)
        return True, props
    else:
        return False, dict(typelabel='blank')

def onpick2(event):
    with open(logfile, "a") as lfile:
        lfile.write(('{0}: {1} {2} {3} {4}\n').format(event.typelabel, event.pickx, event.picky, event.label, event.markertype)) 
        print(event.typelabel,':', event.pickx, event.picky, event.label, event.markertype, event.onepointinterp)    
        
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
    tplot1 = ax1.plot(T2,dep, picker=line_picker, label='T (sec)')
    plt.setp(tplot1, 'color', 'k', 'marker', 'o')
    tplot2 = ax1.plot(T1,dep, picker=line_picker, label='T (pri)')
    plt.setp(tplot2, 'color', 'r', 'marker', 'o')
    ax1.grid(True)
    if (T1.max() - T1.min()) < min_rangeT:
        plt.xlim( (T1.min() - min_rangeT/2, T1.max() + min_rangeT/2) )
    plt.ylim(-5,dep.max() + .1 * dep.max())
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
    tplot3 = ax2.plot(S2,dep, picker=line_picker, label='S (sec)')
    plt.setp(tplot3, 'color', 'k', 'marker', 'o')
    tplot4 = ax2.plot(S1,dep, picker=line_picker, label='S (pri)')
    plt.setp(tplot4, 'color', 'b', 'marker', 'o')
    ax2.grid(True)
    if (S1.max() - S1.min()) < min_rangeS:
        plt.xlim( (S1.min() - min_rangeS/2, S1.max() + min_rangeS/2) )
    plt.ylim(-5,dep.max() + .1*dep.max())
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
    plt.setp(tplot, 'color', 'k', 'marker', 'o')
    tplot = ax3.plot(Sig1,dep)
    plt.setp(tplot, 'color', 'c', 'marker', 'o')
    ax3.grid(True)
    if (Sig1.max() - Sig1.min()) < min_rangeSig:
        plt.xlim( (Sig1.min() - min_rangeSig/2, Sig1.max() + min_rangeSig/2) )
    plt.ylim(-5,dep.max() + .1*dep.max())
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
    
def plot_var(yvar,xvar,varname,ptitle):

    max_xticks = 5


    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    tplot1 = ax1.plot(xvar,yvar, picker=line_picker, label=varname)
    plt.setp(tplot1, 'color', 'k', 'marker', 'o')
    ax1.grid(True)
    if (xvar == 1e35).all():
        plt.xlim(-1,1)
    else:
        plt.xlim( (xvar[xvar != 1e35].min(), xvar[xvar != 1e35].max()) )
    plt.ylim(-5,yvar.max() + .1 * yvar.max())
    ax1.invert_yaxis()
    plt.ylabel('Depth (dB)')
    plt.xlabel(varname)
    xloc = plt.MaxNLocator(max_xticks)
    ax1.xaxis.set_major_locator(xloc) 
    xloc = plt.MaxNLocator(max_xticks*2)
    ax1.xaxis.set_minor_locator(xloc) 
    fmt=mpl.ticker.ScalarFormatter(useOffset=False)
    fmt.set_scientific(False)
    ax1.xaxis.set_major_formatter(fmt)
    ax1.yaxis.set_minor_locator

    #salinity
    
    ax2 = fig.add_subplot(121)
    yvar_text = [[str(x)] for x in yvar]
    tplot3 = ax2.table(cellText=yvar_text)

    t = fig.suptitle(ptitle)
    t.set_y(1.06)
    return fig    
    
"""------------------------------------- Main -----------------------------------------"""

parser = argparse.ArgumentParser(description='plot all vars to edit')
parser.add_argument('inputpath', metavar='inputpath', type=str,
               help='path to .nc file')

args = parser.parse_args()

#read in netcdf data file
nc_path = args.inputpath
nc_path = [nc_path + fi for fi in os.listdir(nc_path) if fi.endswith('.nc') and not fi.endswith('_cf_ctd.nc')]

for ncfile in nc_path:
     
    print "Working on file %s " % ncfile
    (ncdata, params, g_atts) = from_netcdf(ncfile)

    xtime = date2pydate(ncdata['time'],ncdata['time2'])[0]
    cast_time = datetime.datetime.fromordinal(int(xtime)) + datetime.timedelta(xtime - int(xtime))

    ptitle = ("Plotted on: {0} from {1} \n\n"
              "Cruise: {2} Cast: {3}  Stn: {4} \n"
              "Lat: {5:3.3f}  Lon: {6:3.3f} at {7}\n").format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'), 
                                              ncfile.split('/')[-1], g_atts['CRUISE'], g_atts['CAST'], g_atts['STATION_NAME'], 
                                              ncdata['lat'][0], ncdata['lon'][0], datetime.datetime.strftime(cast_time,"%Y-%m-%d %H:%M GMT" ))

    #cycle through variables to plot
    fig = plot_var(ncdata['dep'],ncdata['T_28'][0,:,0,0],'T_28', ptitle)

    #fig.canvas.mpl_connect('key_press_event', press)
    fig.canvas.mpl_connect('pick_event', onpick2 )
    plt.show()




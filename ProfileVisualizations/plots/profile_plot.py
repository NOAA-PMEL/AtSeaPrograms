#!/usr/bin/env

"""
class definitions for ctd profile plots

limit to four variables

"""

#System Stack
import datetime

# science stack
import numpy as np

# Visual Stack

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, WeekdayLocator, MonthLocator, DayLocator, HourLocator, DateFormatter
import matplotlib.ticker as ticker


class CTDProfilePlot(object):

    mpl.rcParams['svg.fonttype'] = 'none'

    def __init__(self, fontsize=10, labelsize=10, plotstyle='k-.', stylesheet='bmh'):
        """Initialize the timeseries with items that do not change.

        This sets up the axes and station locations. The `fontsize` and `spacing`
        are also specified here to ensure that they are consistent between individual
        station elements.

        Parameters
        ----------
        fontsize : int
            The fontsize to use for drawing text
        labelsize : int
          The fontsize to use for labels
        stylesheet : str
          Choose a mpl stylesheet [u'seaborn-darkgrid', 
          u'seaborn-notebook', u'classic', u'seaborn-ticks', 
          u'grayscale', u'bmh', u'seaborn-talk', u'dark_background', 
          u'ggplot', u'fivethirtyeight', u'seaborn-colorblind', 
          u'seaborn-deep', u'seaborn-whitegrid', u'seaborn-bright', 
          u'seaborn-poster', u'seaborn-muted', u'seaborn-paper', 
          u'seaborn-white', u'seaborn-pastel', u'seaborn-dark', 
          u'seaborn-dark-palette']
        """

        self.fontsize = fontsize
        self.labelsize = labelsize
        self.plotstyle = plotstyle
        plt.style.use(stylesheet)

    @staticmethod
    def add_title(cruiseid='', fileid='', stationid='',castdate=datetime.datetime.now(),lat=-99.9,lon=-99.9):
      """Pass parameters to annotate the title of the plot

      This sets the standard plot title using common meta information from PMEL/EPIC style netcdf files

      Parameters
      ----------
      cruiseid : str
        Cruise Identifier
      fileid : str
        File Identifier
      stationid : str
        Station Identifier
      lat : float
        The latitude of the mooring
      lon : float
        The longitude of the mooring
      depth : int
        Nominal depth of the instrument
      """  

      ptitle = ("Plotted on: {time:%Y/%m/%d %H:%M} \n from {fileid} \n "
                "Lat: {latitude:3.3f}  Lon: {longitude:3.3f} at {castdate}" 
    			  " ").format(
    			  time=datetime.datetime.now(), 
                  cruiseid=cruiseid,
                  fileid=fileid,
                  latitude=lat, 
                  longitude=lon, 
                  depth=depth,
                  castdate=datetime.datetime.strftime(castdate,"%Y-%m-%d %H:%M GMT" ) )

      return ptitle

    def plot1var(self, epic_key=None, xdata=None, ydata=None, ylabel=None, secondary=False, **kwargs):
      fig = plt.figure(1)
      ax1 = fig.add_subplot(111)
      p1 = ax1.plot(xdata[0], ydata)
      plt.setp(p1, **(self.var2format(epic_key[0])))
      if secondary:
        p1 = ax1.plot(T2,dep)
        plt.setp(p1, **(self.var2format(epic_key[1])))

      ax1.invert_yaxis()
      plt.ylabel('Depth (dB)', fontsize=self.labelsize, fontweight='bold')
      plt.xlabel('Temperature (C)', fontsize=self.labelsize, fontweight='bold')
      xloc = plt.MaxNLocator(max_xticks)
      ax1.xaxis.set_major_locator(xloc) 
      xloc = plt.MaxNLocator(max_xticks*2)
      ax1.xaxis.set_minor_locator(xloc) 
      fmt=mpl.ticker.ScalarFormatter(useOffset=False)
      fmt.set_scientific(False)
      ax1.xaxis.set_major_formatter(fmt)
      ax1.tick_params(axis='both', which='major', labelsize=self.labelsize)

      return plt, fig

    def var2format(self, epic_key):
      """list of plot specifics based on variable name"""
      plotdic={}
      if epic_key is 'T_28':
        plotdic['color']='red'
        plotdic['linestyle']='-'
        plotdic['linewidth']=0.5
      elif epic_key is 'T2_35':
        plotdic['color']='magenta'
        plotdic['linestyle']='--'
        plotdic['linewidth']=0.5
      else:
        plotdic['color']='black'
        plotdic['linestyle']='--'
        plotdic['linewidth']=1.0        
      return plotdic


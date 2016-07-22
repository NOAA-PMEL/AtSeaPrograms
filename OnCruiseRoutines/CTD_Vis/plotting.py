#!/usr/bin/env

"""
 plotting.py
 
 converted monkey patched code to methods/modules
 
 Built using Anaconda packaged Python:
 
 Original code:
 --------------

 plotting.py

 purpose:  Plotting methods for ctd DataFrame.
 author:   Filipe P. A. Fernandes
 e-mail:   ocefpaf@gmail
 web:      http://ocefpaf.tiddlyspot.com/
 created:  23-Jul-2013
 modified: Tue 23 Jul 2013 01:31:06 PM BRT

"""


from __future__ import absolute_import

# Standard library.
import datetime

# Scientific stack.
import gsw
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as AA

from pandas import Series
from scipy.interpolate import interp1d
from mpl_toolkits.axes_grid1 import host_subplot


__all__ = ['plot',
           'plot_vars']


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 13)
__modified__ = datetime.datetime(2014, 01, 13)
__version__  = "0.2.0"
__status__   = "Development"


def plot(cast, variables=None, **kw):
    """
    Plot a CTD variable against the index (pressure or depth).
    
    (fig, ax) = plot(cast['t090C'])
    """
    
    
    fig, ax = plt.subplots(figsize=(4, 10))

    ax.plot(cast[variables[0]], cast.index, **kw)
    ax.set_ylabel(cast.index.name)
    ax.set_xlabel(cast[variables[0]].name)
    ax.invert_yaxis()
    offset = 0.01
    x1, x2 = ax.get_xlim()[0] - offset, ax.get_xlim()[1] + offset
    ax.set_xlim(x1, x2)

        
    try:  # FIXME with metadata.
        fig.suptitle(r"Station %s profile" % cast.name)
    except AttributeError:
        pass
    
    return fig, ax

def plot_prisec_ts(cast, variables=None, **kwds):
    """
    Plot CTD temperature and salinity. (both sensors)
    
    (fig, ax0, ax1) = plot_prisec_ts(cast, variables=['t090C', 't190C', 'sal00', 'sal11'])
    
    Todo: Unify labels to be variable dependent
    """
    fig = plt.figure(figsize=(4, 10))
    ax0 = host_subplot(111, axes_class=AA.Axes)
    ax1 = ax0.twiny()

    # Axis location.
    host_new_axis = ax0.get_grid_helper().new_fixed_axis
    ax0.axis["bottom"] = host_new_axis(loc="top", axes=ax0, offset=(0, 0))
    par_new_axis = ax1.get_grid_helper().new_fixed_axis
    ax1.axis["top"] = par_new_axis(loc="bottom", axes=ax1, offset=(0, 0))

    ax0.plot(cast[variables[0]], cast.index, 'r.', label=cast[variables[0]].name)
    ax0.plot(cast[variables[1]], cast.index, 'k+', label=cast[variables[1]].name)
    ax1.plot(cast[variables[2]], cast.index, 'b.', label=cast[variables[2]].name)
    ax1.plot(cast[variables[3]], cast.index, 'k+', label=cast[variables[3]].name)

    ax0.set_ylabel("Pressure [dbar]")
    ax0.set_xlabel(u"Temperature [\u00b0C]")
    ax1.set_xlabel("Salinity [kg g$^{-1}$]")
    ax1.invert_yaxis()

    try:  # FIXME with metadata.
        fig.suptitle(r"Station %s profile" % cast.name)
    except AttributeError:
        pass

    ax0.legend(shadow=True, fancybox=True,
               numpoints=1, loc='lower right')

    offset = 0.01
    x1, x2 = ax0.get_xlim()[0] - offset, ax0.get_xlim()[1] + offset
    ax0.set_xlim(x1, x2)

    offset = 0.01
    x1, x2 = ax1.get_xlim()[0] - offset, ax1.get_xlim()[1] + offset
    ax1.set_xlim(x1, x2)

    return fig, (ax0, ax1)

def plot_O2_comp(cast, variables=None, **kwds):
    """
    Plot CTD Oxygen and Percent Saturation. (2-vars)
    
    (fig, ax0, ax1) = plot_O2_comp(cast, variables=['sbeox0Mm/Kg', 'sbeox1Mm/Kg', 'sbeox0PS'])
    
    Todo: Unify labels to be variable dependent
    """
    fig = plt.figure(figsize=(4, 10))
    ax0 = host_subplot(111, axes_class=AA.Axes)
    ax1 = ax0.twiny()

    # Axis location.
    host_new_axis = ax0.get_grid_helper().new_fixed_axis
    ax0.axis["bottom"] = host_new_axis(loc="top", axes=ax0, offset=(0, 0))
    par_new_axis = ax1.get_grid_helper().new_fixed_axis
    ax1.axis["top"] = par_new_axis(loc="bottom", axes=ax1, offset=(0, 0))

    ax0.plot(cast[variables[0]], cast.index, 'r.', label=cast[variables[0]].name)
    ax0.plot(cast[variables[1]], cast.index, 'k+', label=cast[variables[1]].name)
    ax1.plot(cast[variables[2]], cast.index, 'b.', label=cast[variables[2]].name)

    ax0.set_ylabel("Pressure [dbar]")
    ax0.set_xlabel("O2 [Mm/Kg]")
    ax1.set_xlabel("O2 [%]")
    ax1.invert_yaxis()

    try:  # FIXME with metadata.
        fig.suptitle(r"Station %s profile" % cast.name)
    except AttributeError:
        pass

    ax0.legend(shadow=True, fancybox=True,
               numpoints=1, loc='lower right')

    offset = 0.01
    x1, x2 = ax0.get_xlim()[0] - offset, ax0.get_xlim()[1] + offset
    ax0.set_xlim(x1, x2)

    offset = 0.01
    x1, x2 = ax1.get_xlim()[0] - offset, ax1.get_xlim()[1] + offset
    ax1.set_xlim(x1, x2)


    return fig, (ax0, ax1)
        
def plot_ts(cast, variables=None, **kwds):
    """
    Plot CTD temperature and salinity. (only one sensor)
    
    (fig, ax0, ax1) = plot_ts(cast, variables=['t090C', 'sal00'])
    
    Todo: Unify labels to be variable dependent
    """
    fig = plt.figure(figsize=(4, 10))
    ax0 = host_subplot(111, axes_class=AA.Axes)
    ax1 = ax0.twiny()

    # Axis location.
    host_new_axis = ax0.get_grid_helper().new_fixed_axis
    ax0.axis["bottom"] = host_new_axis(loc="top", axes=ax0, offset=(0, 0))
    par_new_axis = ax1.get_grid_helper().new_fixed_axis
    ax1.axis["top"] = par_new_axis(loc="bottom", axes=ax1, offset=(0, 0))

    ax0.plot(cast[variables[0]], cast.index, 'r.', label=cast[variables[0]].name)
    ax1.plot(cast[variables[1]], cast.index, 'b.', label=cast[variables[1]].name)

    ax0.set_ylabel("Pressure [dbar]")
    ax0.set_xlabel(u"Temperature [\u00b0C]")
    ax1.set_xlabel("Salinity [kg g$^{-1}$]")
    ax1.invert_yaxis()

    try:  # FIXME with metadata.
        fig.suptitle(r"Station %s profile" % cast.name)
    except AttributeError:
        pass

    ax0.legend(shadow=True, fancybox=True,
               numpoints=1, loc='lower right')

    offset = 0.01
    x1, x2 = ax0.get_xlim()[0] - offset, ax0.get_xlim()[1] + offset
    ax0.set_xlim(x1, x2)

    offset = 0.01
    x1, x2 = ax1.get_xlim()[0] - offset, ax1.get_xlim()[1] + offset
    ax1.set_xlim(x1, x2)

    return fig, (ax0, ax1)

"""
def plot_section(self, reverse=False, filled=False, **kw):
    lon, lat, data = map(np.asanyarray, (self.lon, self.lat, self.values))
    data = ma.masked_invalid(data)
    h = self.get_maxdepth()
    if reverse:
        lon = lon[::-1]
        lat = lat[::-1]
        data = data.T[::-1].T
        h = h[::-1]
    x = np.append(0, np.cumsum(gsw.distance(lon, lat)[0] / 1e3))
    z = self.index.values.astype(float)

    if filled:  # FIXME: Cause discontinuities.
        data = data.filled(fill_value=np.nan)
        data = extrap_sec(data, x, z, w1=0.97, w2=0.03)

    # Contour key words.
    fmt = kw.pop('fmt', '%1.0f')
    extend = kw.pop('extend', 'both')
    fontsize = kw.pop('fontsize', 12)
    labelsize = kw.pop('labelsize', 11)
    cmap = kw.pop('cmap', plt.cm.rainbow)
    levels = kw.pop('levels', np.arange(np.floor(data.min()),
                    np.ceil(data.max()) + 0.5, 0.5))

    # Colorbar key words.
    pad = kw.pop('pad', 0.04)
    aspect = kw.pop('aspect', 40)
    shrink = kw.pop('shrink', 0.9)
    fraction = kw.pop('fraction', 0.05)

    # Topography mask key words.
    dx = kw.pop('dx', 1.)
    kind = kw.pop('kind', 'linear')
    linewidth = kw.pop('linewidth', 1.5)

    # Station symbols key words.
    color = kw.pop('color', 'k')
    offset = kw.pop('offset', -5)
    marker = kw.pop('marker', 'v')
    alpha = kw.pop('alpha', 0.5)

    # Figure.
    figsize = kw.pop('figsize', (12, 6))
    fig, ax = plt.subplots(figsize=figsize)
    xm, hm = gen_topomask(h, lon, lat, dx=dx, kind=kind)
    ax.plot(xm, hm, color='black', linewidth=linewidth, zorder=3)
    ax.fill_between(xm, hm, y2=hm.max(), color='0.9', zorder=3)

    if marker:
        ax.plot(x, [offset] * len(h), color=color, marker=marker, alpha=alpha,
                zorder=5)
    ax.set_xlabel('Cross-shore distance [km]', fontsize=fontsize)
    ax.set_ylabel('Depth [m]', fontsize=fontsize)
    ax.set_ylim(offset, hm.max())
    ax.invert_yaxis()

    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_label_position('left')
    ax.xaxis.set_tick_params(tickdir='out', labelsize=labelsize, pad=1)
    ax.yaxis.set_tick_params(tickdir='out', labelsize=labelsize, pad=1)

    if False:  # TODO: +/- Black-and-White version.
        cs = ax.contour(x, z, data, colors='grey', levels=levels,
                        extend=extend, linewidths=1., alpha=1., zorder=2)
        ax.clabel(cs, fontsize=8, colors='grey', fmt=fmt, zorder=1)
        cb = None
    if True:  # Color version.
        cs = ax.contourf(x, z, data, cmap=cmap, levels=levels, alpha=1.,
                         extend=extend, zorder=2)  # manual=True
        # Colorbar.
        cb = fig.colorbar(mappable=cs, ax=ax, orientation='vertical',
                          aspect=aspect, shrink=shrink, fraction=fraction,
                          pad=pad)
    return fig, ax, cb
"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()

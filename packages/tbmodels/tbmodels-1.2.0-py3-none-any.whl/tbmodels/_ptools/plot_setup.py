#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    06.10.2014 17:39:24 CEST
# File:    plot_setup.py

"""
El Pueschelifier
"""
from .wheel import Wheel
from .color import default_cycle

import sys
import cycler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import rc
from matplotlib.font_manager import FontProperties

import ptools.colormaps as cmaps
for name, cmap in cmaps.cmaps.items():
    plt.register_cmap(name=name, cmap=cmap)
#~ plt.register_cmap(name='viridis', cmap=cmaps.viridis)
#~ plt.register_cmap(name='viridis_r', cmap=cmaps.viridis_r)
#~ plt.set_cmap(cmaps.viridis) # This will all be default soon

def plot_style(background='#eeeeee',  grid='white', axes='white', axeslw=1.2, gridlw=0.7, font=None, color_cycle=['b', 'g', 'r', 'c', 'm', 'y', 'k']):
    rc('text', usetex=True)
    rc('axes', facecolor=background)
    rc('axes', edgecolor=axes)
    rc('axes', linewidth=axeslw)
    rc('axes', grid=True)
    if color_cycle is not None:
        rc('axes', prop_cycle=cycler.cycler('color', color_cycle))
    rc('axes', axisbelow=True)
    rc('grid', color=grid)
    rc('grid', linestyle='-')
    rc('grid', linewidth=gridlw)
    rc('xtick.major', size=0)
    rc('xtick.minor', size=0)
    rc('ytick.major', size=0)
    rc('ytick.minor', size=0)
    rc('font',**{'family':'sans-serif', 'sans-serif':['Gill Sans MT']})
    # cmbright is default, looks nicest
    if font == 'cmbright':
        #~ matplotlib.rcParams['text.latex.preamble'] = [
            #~ r'\usepackage{siunitx}',   
            #~ r'\sisetup{detect-all}'
            #~ r'\usepackage{cmbright}',    
            #~ r'\usepackage{sansmath}',
            #~ r'\sansmath'  
            #~ ]
        rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{cmbright}\usepackage{siunitx}\sisetup{detect-all}')
    # use helvet if something doesn't work in cmbright (e.g. \angstrom)
    elif font == 'helvet':
        matplotlib.rcParams['text.latex.preamble'] = [
            r'\usepackage{siunitx}',   
            r'\sisetup{detect-all}',   
            r'\usepackage{helvet}',    
            r'\usepackage{sansmath}',  
            r'\sansmath'
            ]
    # fallback (for Cluster)
    else:
        rc('text.latex', preamble=r'\usepackage{amsmath}')
    rc('mathtext', fontset='stixsans')
    if color_cycle is not None:
        return Wheel(color_cycle)

def use_style(name, **kwargs):
    defaults = {'fancy': dict(background='#eeeeee', grid='white',
                              axes='white', axeslw=1.2, gridlw=0.7,
                              font='cmbright',
                              color_cycle=default_cycle(4)),
                'plain': dict(background='#ffffff', grid='#cccccc',
                              axes='#000000', axeslw=1.2, gridlw=0.7,
                              font='cmbright',
                              color_cycle=default_cycle(4)),
                'plain_2': dict(background='#ffffff', grid='white',
                              axes='#000000', axeslw=1.2, gridlw=0.7,
                              font='cmbright',
                              color_cycle=default_cycle(4))}
    settings = defaults[name]
    settings.update(kwargs)
    return plot_style(**settings)
    
plot_style()

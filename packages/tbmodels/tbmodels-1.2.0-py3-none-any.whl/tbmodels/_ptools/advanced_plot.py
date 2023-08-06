#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    24.07.2015 10:07:20 CEST
# File:    advanced_plot.py

import numpy as np
import copy
from matplotlib.colors import Normalize, LogNorm
import matplotlib.pyplot as plt
import scipy.spatial as sp

def cmap_irregular(val, pos, cmap=plt.get_cmap(), axis=None, xlim='auto', ylim='auto', log_norm=False, fill_lines=True, scale_val=None, zero_color=None, **kwargs):
    r"""
    Creates a cmap from irregularly spaced values ``val`` on a mesh n_x * n_y.
    
    :param fill_lines:  Determines whether a line is plotted or not. This has the advantage of not creating ugly white lines, but the areas may be slightly off.
    :type fill_lines:   bool
    
    Kwargs are passed to pyplot.fill()
    """
    if xlim == 'auto':
        xcoord = [p[0] for p in pos]
        xlim = (min(xcoord), max(xcoord))
    if ylim == 'auto':
        ycoord = [p[1] for p in pos]
        ylim = (min(ycoord), max(ycoord))
    # add 'points at infinity'
    helper_points = []
    # add 1 to ensure any point within is closer
    x_width = xlim[1] - xlim[0] + 1.
    y_width = ylim[1] - ylim[0] + 1.
    for i, xval in enumerate(xlim):
        x_mul = -1 if i == 0 else 1
        for j, yval in enumerate(ylim):
            y_mul = -1 if j == 0 else 1
            helper_points.append([xval + x_mul * x_width, yval + y_mul * y_width])
            helper_points.append([xval, yval + y_mul * y_width])
            helper_points.append([xval + x_mul * x_width, yval])
    
    new_pos = copy.deepcopy(pos)
    new_val = copy.deepcopy(val)
    new_pos.extend(helper_points)
    new_val.extend([0] * len(helper_points))

    vor = sp.Voronoi(new_pos)
    if log_norm:
        norm = LogNorm()
    else:
        norm = Normalize()
    if scale_val is None:
        norm.autoscale(val)
    else:
        norm.autoscale(scale_val)
    colors = cmap([norm(v) for v in new_val])

    # adjust for logplot -- set colors where v == 0 to zero_color
    if zero_color is not None:
        for i, v in enumerate(new_val):
            if v == 0:
                colors[i] = zero_color
    if axis is None:
        fig, axis = plt.subplots()

    for color, region_idx in zip(colors, vor.point_region):
        region = vor.regions[region_idx]
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            axis.fill(
                *zip(*polygon),
                lw=1e-11 if fill_lines else 0.,
                color=color,
                **kwargs
            )

    axis.set_xlim(xlim)
    axis.set_ylim(ylim)

    return axis, cmap, norm

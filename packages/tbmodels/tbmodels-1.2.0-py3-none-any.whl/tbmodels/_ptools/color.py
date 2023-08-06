#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.04.2015 19:09:38 CEST
# File:    color.py

"""
Creates color gradients and cycles based on luminosity.
"""

from .namespace import Namespace
import numpy as np

def _luminosity(color):
    """calculates the effective luminosity of a color"""
    return np.dot([0.2126, 0.7172, 0.0722], color)

def _crop_color(color):
    """crops invalid rgb values to [0, 1]"""
    return np.array([max(0, min(1, x)) for x in color])

class Gradient(object):
    """
    Color gradient containing base_color.
    """
    def __init__(self, base_color):
        self._base_color = np.array(base_color)
        self._base_luminosity = _luminosity(base_color)

    def __call__(self, pos, center=None):
        """
        Returns a color on the gradient. If center is None, pos is the
        color's luminosity. Else the gradient's base color is located
        at center and pos is relative to that.
        """
        if center is None:
            center = self._base_luminosity
        ratio = pos / center
        if ratio <= 1.:
            return _crop_color(ratio * self._base_color)
        else:
            # complementary color & position
            compl = np.array([1, 1, 1]) - self._base_color
            compl_strength = (pos - center) / (1 - center)
            return _crop_color(self._base_color + compl_strength * compl)

def to_hex(color):
    """turns list-like rgb into hex code"""
    return '#' + ''.join([hex(min(int(x * 256), 255)).lstrip('0x').zfill(2) for x in color]).upper()

# predefined color gradients
gradients = Namespace()
gradients.r = Gradient([1, 0, 0])
gradients.g = Gradient([0, 1, 0])
gradients.b = Gradient([0, 0, 1])
gradients.y = Gradient([1, 1, 0])
gradients.c = Gradient([0, 1, 1])
gradients.m = Gradient([1, 0, 1])

def color_cycle(color_list, luminosity_list='auto', coding='rgb'):
    """
    Creates a color cycle.
    """
    if isinstance(luminosity_list, str):
        if luminosity_list == 'auto':
            luminosity_list = np.linspace(0, 1, len(color_list) + 1, endpoint=False)[1:]
        else:
            raise ValueError('unrecognized mode for luminosity_list')

    if len(luminosity_list) != len(color_list):
        raise ValueError('color_list & luminosity_list must have the same length')

    colors = []
    for color, luminosity in zip(color_list, luminosity_list):
        # catch the case of predefined colors
        if isinstance(color, str):
            gradient = gradients[color]
        else:
            gradient = Gradient(color)
        colors.append(gradient(luminosity))
    if coding == 'rgb':
        return colors
    elif coding == 'hex':
        return [to_hex(c) for c in colors]
    else:
        raise ValueError('invalid coding')

def default_cycle(num_colors, coding='hex'):
    """
    Default color cycle for up to 6 colors. If you're using more than
    6 colors in a polished plot, maybe you're doing something wrong to begin with.
    """
    assert 0 < num_colors
    assert num_colors <= 6
    colors = [('b', 0), ('g', 3), ('r', 1), ('c', 4), ('m', 2), ('y', 5)][:num_colors]
    colors = sorted(colors, key=lambda x: x[1])
    colors = [c[0] for c in colors]
    return color_cycle(colors, coding=coding)




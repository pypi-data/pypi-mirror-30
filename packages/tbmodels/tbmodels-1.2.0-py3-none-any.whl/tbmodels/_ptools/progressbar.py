#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    22.05.2014 08:33:00 CEST
# File:    progressbar.py

from __future__ import print_function

import sys
from .termcolor import color, UP_

progress_colors = ['redb', 'yellowb', 'greenb', 'cyanb']

def progressbar(p, width = 50):
    n = int(p * width + 1e-8)
    color_now = progress_colors[min(len(progress_colors) - 1, int(p * len(progress_colors)))]
    bar = "\r{}[" + n * "*" + (width - n) * "-" + "]{}"
    bar = bar.format(color[color_now], color['none'])
    return bar


    

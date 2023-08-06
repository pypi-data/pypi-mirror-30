#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    06.06.2013 15:00:17 EDT
# File:    color.py

from __future__ import print_function

import sys

ALL_COLORS = ["BLACK", "BLACKB", "RED", "REDB", "GREEN", "GREENB", "YELLOW", "YELLOWB", "BLUE", "BLUEB", "MAGENTA", "MAGENTAB", "CYAN", "CYANB", "WHITE", "WHITEB", "BLACKBG", "REDBG", "GREENBG", "YELLOWBG", "BLUEBG", "MAGENTABG", "CYANBG", "WHITEBG", "BLACKBGB", "REDBGB", "GREENBGB", "YELLOWBGB", "BLUEBGB", "MAGENTABGB", "CYANBGB", "WHITEBGB", "NONE"]
ALL_COLORS_IMPL = ["\033[0;30m", "\033[1;30m", "\033[0;31m", "\033[1;31m", "\033[0;32m", "\033[1;32m", "\033[0;33m", "\033[1;33m", "\033[0;34m", "\033[1;34m", "\033[0;35m", "\033[1;35m", "\033[0;36m", "\033[1;36m", "\033[0;37m", "\033[1;37m", "\033[40m", "\033[41m", "\033[42m", "\033[43m", "\033[44m", "\033[45m", "\033[46m", "\033[47m", "\033[100m", "\033[101m", "\033[102m", "\033[103m", "\033[104m", "\033[105m", "\033[106m", "\033[107m", "\033[0m"]

__all__ = ALL_COLORS + ["color", "enable_color", "disable_color"]

#------------------- special bash prompt ------------------- 
_CLRSCR = "\033[2J\033[100A"
_CLEAR = "\x1B[2K"
_UP = "\033[1A"
_RENTER = _UP + _CLEAR

color = {}

def _import_color(color_on = True):
    for i in range(len(ALL_COLORS)):
        _impl = ALL_COLORS_IMPL[i] if color_on else ""
        exec("_{} = '{}'".format(ALL_COLORS[i], _impl), globals())
        _col  = ALL_COLORS[i]
        
        
        if sys.version_info >= (3, 0):
            exec("def {0}(*out, end = '\\n'):\n\tprint(_{0} + ' '.join([str(x) for x in out]) + _NONE, end=end)".format(ALL_COLORS[i]), globals())
        else:
            exec("def {0}(*out, **kwargs):\n\tend = kwargs.get('end', '\\n')\n\tprint(_{0} + ' '.join([str(x) for x in out]) + _NONE, end = end)".format(ALL_COLORS[i]), globals())
        
        color[ALL_COLORS[i].lower()] = _impl
        
    for i in ["clrscr", "clear", "up", "renter"]:
        color[i] = eval("_{}".format(i.upper())) if color_on else ""


def enable_color():
    _import_color(True)

def disable_color():
    _import_color(False)

enable_color() # default enabled

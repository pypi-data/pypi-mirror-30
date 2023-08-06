#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    31.03.2015 09:24:49 CEST
# File:    io_manip.py

from .is_instance import *
from .decorator_collection import listable
from .termcolor import color

from functools import partial
import re

__all__ = ["to_number", "to_str", "split_clean", "sstr", "time_int", "time_str", "ms_time_str", "dyn_time_str", "padding"]

@listable
def to_number(obj, strip_quotes = True):
    """
    Tries to convert the input string into an int, if that doesn't work into a float and if that also fails, returns the string again.
    """
    if is_dict(obj):
        return dict([(k, to_number(v, strip_quotes)) for k, v in obj.items()])
        
    try:
        res = int(obj)
        return res
    except:
        pass
    try:
        res = float(obj)
        return res
    except:
        pass
    
    test = obj.strip()
    if len(test) != 0 and test[0] == "[" and test[-1] == "]":
        #~ l = test[1:-1].split(",") #too easy, splits [[a, b], [c, d]] -> [[a<> b]<> [c<> d]]
        l = test[1:-1].split(",")
        l = re.split(",(?=(?:[^\\[\\]]*(?:\\[[^\\[\\]]*\\]))*[^\\[\\]]*$)", test[1:-1]) # splits only , outside of [] bc of recursive lists [[a, b], [c, d]]
        
        if len(l) == 1 and l[0] == "":
            return []
        
        return to_number(l, strip_quotes)
    
    if strip_quotes == True:
        return re.sub('^[\s]*(["\'])([\s\S]*)(\\1)$', "\\2", obj)
    return obj

def to_str(obj, add_quotes = True):
    if is_list(obj):
        strs = []
        for o in obj:
            strs.append(to_str(o, add_quotes))
        res = "[" + ",".join(strs) + "]"
        return res
    elif is_dict(obj):
        return dict([(k, to_str(v, add_quotes)) for k, v in obj.items()])
    elif is_str(obj):
        if add_quotes:
            if "'" in obj:
                return '"{}"'.format(obj)
            else:
                return "'{}'".format(obj)
            #~ return str([obj])[1:-1] #trick since the list chooses the right quotes
        else:
            return obj
    else:
        return str(obj)

@listable
def split_clean(string, strip_quotes = False):
    string = re.sub("^[\\s]+|[\\s]+$", "", string) # remove front and back whitespace (strip would also work)
    not_in_quotes = '(?=(?:[^"\']*(?:"[^"]*"|\'[^\']*\'))*[^"\']*$)'
    e = '\\s+'+not_in_quotes # split on whitespace sections but not in "" or ''
    prog = re.compile(e)
    res = prog.split(string)
    if strip_quotes:
        for i in range(len(res)):
            res[i] = re.sub('^(["\'])([\s\S]*)(\\1)$', "\\2", res[i]) #strips "" or '' if found at ^ and $
        return res
    else:
        return res

def sstr(obj, length = 50):
    sv = str(obj)
    if len(sv) > length: # shorten too lengthong objects to size 60
        sv = sv[:length//2] + " ...{}... ".format(len(sv) - length) + sv[-length//2:]
    return sv

#------------------- time conversion 00:00:00 -> sec -------------------
def time_int(t_str):
    t_str = to_number(t_str.split(":"))
    return 3600 * t_str[0] + 60 * t_str[1] + t_str[2]

#------------------- time conversion sec -> 00:00:00 -------------------
def time_str(sec_int):
    return "{:02d}:{:02d}:{:02d}".format(int(sec_int / 3600), int(sec_int / 60) % 60, int(sec_int) % 60)

def ms_time_str(sec_float):
    if sec_float < 60:
        return "{:.1f}s".format(sec_float)
    else:
        return "{}m {:.0f}s".format(int(sec_float/60), sec_float%60)
        
def dyn_time_str(t_int):
    y, d, h, m, s = [int(t_int / (60 * 60 * 24 * 365))
                   , int(t_int / (60 * 60 * 24)) % 365
                   , int(t_int / (60 * 60)) % 24
                   , int(t_int / (60)) % 60
                   , int(t_int) % 60]
    if d == 0:
        return "{:02d}:{:02d}:{:02d}".format(h, m, s)
    else:
        res = ""
        if y > 0:
            res += "{}y ".format(y)
        res += "{}d {:02d}h".format(d, h)
        return res

def padding(s, modulo, char = " "):
    """
    Padding a string to a multiple length of modulo.
    """
    if is_bytes(s):
        char = char.encode()
        
    if len(s) % modulo != 0:
        return s.ljust(len(s) + modulo - len(s) % modulo, char)
    else:
        return s

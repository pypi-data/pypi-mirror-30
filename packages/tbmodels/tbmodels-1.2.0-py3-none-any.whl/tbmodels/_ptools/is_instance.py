#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    30.03.2015 15:40:22 CEST
# File:    is_instance.py

import inspect
import numbers
import collections

__all__ = ["is_list", "is_tuple", "is_iterable", "is_dict", "is_int", "is_float", "is_number", "is_str", "is_bytes", "is_function"]

def is_list(obj):
    """
    Checks if the obj is a list.
    """
    return isinstance(obj, list)

def is_tuple(obj):
    """
    Checks if the obj is a tuple.
    """
    return isinstance(obj, tuple)

def is_iterable(obj):
    """
    Checks if the obj is an iterable.
    """
    return isinstance(obj, collections.Iterable)
    
def is_dict(obj):
    """
    Checks if the obj is a dict.
    """
    return isinstance(obj, dict)
    
def is_int(obj):
    """
    Checks if the obj is an int.
    """
    return isinstance(obj, numbers.Integral)

def is_float(obj):
    """
    Checks if the obj is a float.
    """
    return isinstance(obj, float)

def is_number(obj):
    """
    Checks if the obj is an int or a float.
    """
    return is_int(obj) or is_float(obj)

def is_str(obj):
    """
    Checks if the obj is a string.
    """
    return isinstance(obj, str)

def is_bytes(obj):
    """
    Checks if the obj is a bytes array.
    """
    return isinstance(obj, bytes)

def is_function(obj):
    """
    Checks if the obj is a python function.
    """
    return inspect.isfunction(obj)

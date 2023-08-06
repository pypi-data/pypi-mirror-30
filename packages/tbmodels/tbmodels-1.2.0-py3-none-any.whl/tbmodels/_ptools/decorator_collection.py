#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    15.06.2015 08:25:45 CEST
# File:    decorator_collection.py

from decorator import decorator
from .is_instance import is_list, is_int, is_tuple

__all__ = ["listable"]

def inf_listable(fct):
    def inner(fct, arg, *args, **kwgs):
        if is_list(arg) or is_tuple(arg):
            return list(map(lambda a: inner(fct, a, *args, **kwgs), arg))
        else:
            return fct(arg, *args, **kwgs)
    
    return decorator(inner, fct)

@decorator
def single_listable(fct, arg, *args, **kwgs):
    if is_list(arg) or is_tuple(arg):
        return list(map(lambda a: fct(a, *args, **kwgs), arg))
    else:
        return fct(arg, *args, **kwgs)

def listable(fct_or_int):
    if is_int(fct_or_int):
        if fct_or_int == 1:
            return single_listable
        else:
            raise NotImplementedError
    else:
        return inf_listable(fct_or_int)

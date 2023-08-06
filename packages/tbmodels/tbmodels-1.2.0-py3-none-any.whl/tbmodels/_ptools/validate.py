#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    24.06.2015 11:44:07 CEST
# File:    validate.py

import copy
import inspect

def validate(func):
    annot = copy.deepcopy(func.__annotations__)
    spec = copy.deepcopy(inspect.getfullargspec(func))
    try:
        ret = annot['return']
        del annot['return']
        no_ret = False
    except KeyError:
        no_ret = True

    def inner(*args, **kwargs):
        for key, val in annot.items():
            #args
            if key in spec.args:
                if not val(args[spec.args.index(key)]):
                    raise ValueError('Input value {1}={0} does not match the annotated condition "{2}"'.format(args[spec.args.index(key)], key, val.__name__))
            #varargs
            elif key == spec.varargs:
                for argval in args[len(spec.args):]:
                    if not val(argval):
                        raise ValueError('Input value {} in {} does not match the annotated condition "{}"'.format(argval, key, val.__name__))
            #kwargs
            elif key in spec.kwonlyargs:
                if not val(kwargs[key]):
                    raise ValueError('Input value {1}={0} does not match the annotated condition "{2}"'.format(kwargs[key], key, val.__name__))
            #varkwargs
            elif key == spec.varkw:
                for kw, kwval in kwargs.items():
                    if not kw in spec.kwonlyargs:
                        if not val(kwval):
                            raise ValueError('Input value {1}={0} does not match the annotated condition "{2}"'.format(kwval, kw, val.__name__))
                        
        res = func(*args, **kwargs)
        if not ret(res):
            raise ValueError('Return value does not match the annotated condition')
        return res
    return inner

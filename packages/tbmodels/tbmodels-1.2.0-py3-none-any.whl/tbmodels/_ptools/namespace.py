#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    26.03.2015 15:38:59 CET
# File:    namespace.py

import inspect

class Namespace(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, val):
        self[key] = val
        return val

    def __delattr__(self, key):
        del self[key]

def to_ns(ns_name):
    def inner(func):
        ns_name[func.__name__] = func
    return inner

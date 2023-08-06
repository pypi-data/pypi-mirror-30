#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>, Dominik Gresch <greschd@gmx.ch>
# Date:    24.06.2015 18:34:56 CEST
# File:    abc_prototype.py

import sys

__all__ = ["ABCProto", "check_concept"]

from abc import ABCMeta
if sys.version < '3':
    class ABC(object):
        __metaclass__ = ABCMeta
else:
    from abc import ABC

class ABCProto(ABCMeta):
    def __new__(mcls, name, bases, namespace):
        items = set(namespace.keys())
        for b in bases: # for derived concepts
            for k in b.__dict__.keys():
                items.add(k)
        remove = set(ABC.__dict__.keys()).union(set(object.__dict__.keys()))
        remove.add("__qualname__") # exist only during class construction
        remove.add("__subclasshook__")
        remove.add("__slots__") # for mixing Sized, Container .. concepts with other concepts
        remove.add("_concept_items")
        items.difference_update(remove) # take out all that's in ABC
        def subclasshook(cls, instance):
            for it in items:
                if not hasattr(instance, it):
                    return False
            return True
        
        namespace["_concept_items"] = list(items)
        namespace["__subclasshook__"] = classmethod(subclasshook)

        return super(ABCProto, mcls).__new__(mcls, name, bases, namespace)

def check_concept(instance, concept, level='class'):
    res = {}
    if level == 'class':
        cls = instance.__class__
        for it in concept._concept_items:
            res[it] = hasattr(cls, it)
    elif level == 'instance':
        for it in concept._concept_items:
            res[it] = hasattr(instance, it)
    else:
        raise ValueError('Invalid input for \'level\': must be \'class\' or \'instance\'')
    return res

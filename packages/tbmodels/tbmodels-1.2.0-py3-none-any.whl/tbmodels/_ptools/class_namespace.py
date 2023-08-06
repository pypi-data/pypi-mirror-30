#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    12.10.2015 10:52:22 CEST
# File:    test.py

import collections as co

r"""
Module for disclosing parts of a class into a separate "namespace". As of yet, this only works for methods accessed via an instance, but it should be extensible to classmethods, staticmethods etc.
"""


#--------------------- HELPERS (FORWARD SELF) --------------------------#
class _namespace_descriptor(object):
    def __init__(self, namespace_proxy_type):
        self.__doc__ = 'doc'
        self.namespace_proxy_type = namespace_proxy_type
        
    def __get__(self, cls, owner):
        if cls is None:
            return self
        return self.namespace_proxy_type(cls, owner)

class _Proxy(object):
    """proxy doc"""
    def __init__(self, suself, sucls):
        self.suself = suself
        self.sucls = sucls

class _function_descriptor(object):
    def __init__(self, fct):
        self.fct = fct
        
    def __get__(self, obj, objtype):
        if obj is None:
            return self.fct
        return self.fct.__get__(obj.suself, obj.sucls)
#-----------------------------------------------------------------------#
    
def add_namespaces(cls):
    methods = co.defaultdict(lambda: [])
    # search all disclosure names
    for k, v in cls.__dict__.items():
        if hasattr(v, '_namespace_tag'):
            tag = v._namespace_tag
            if tag[1] is None:
                methods[tag[0]].append((k, _function_descriptor(v)))
            elif tag[1] is classmethod:
                methods[tag[0]].append((k, _function_descriptor(classmethod(v))))
            elif tag[1] is staticmethod:
                methods[tag[0]].append((k, _function_descriptor(staticmethod(v))))

    # create a _Proxy type for each disclosure name
    new_cls_dict = dict()
    for k in methods.keys():
        # Check needs to happen before objects get deleted
        if hasattr(cls, k):
            raise AttributeError('Class already has attribute called {0}'.format(k))

        # Create _Proxy object
        namespace = dict(methods[k])
        if '__doc__' not in namespace.keys():
            namespace['__doc__'] = 'This is a namespace class. Functions defined here behave as if they were defined in the parent class, but are encapsulated in this namespace.'
        setattr(cls, k, _namespace_descriptor(type(k, (_Proxy,), namespace)))

        for name, _ in methods[k]:
            delattr(cls, name)

    return cls

def to_namespace(name):
    def _to_namespace_impl(fct):
        if isinstance(fct, classmethod):
            fct = fct.__func__
            fct._namespace_tag = (name, classmethod)
        elif isinstance(fct, staticmethod):
            fct = fct.__func__
            fct._namespace_tag = (name, staticmethod)
        else:
            fct._namespace_tag = (name, None)
        return fct

    return _to_namespace_impl

def use_sphinx_mode():
    """Breaks the namespace functionality but fixes Sphinx documentation. Use this in conf.py."""
    def __get__(self, obj, objtype):
        # This breaks the functionality but fixes Sphinx
        if obj is None:
            return self.namespace_proxy_type
        return self.namespace_proxy_type(obj, objtype)

    _namespace_descriptor.__get__ = __get__

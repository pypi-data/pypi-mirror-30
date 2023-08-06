#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    18.06.2015 15:34:20 CEST
# File:    cache.py

"""
Tools related to caching the values of functions.
"""

import pickle

def store_hashable(fct, filename, overwrite=False):
    r"""
    Creates a function which stores its values in a file. The functions arguments / keyword arguments must be hashable
    
    :param fct:     The function whose values should be cached.
    :type fct:      function
    
    :param filename:    Path to the file where the values are stored
    :type filename:     str
    
    :param overwrite:   Indicates whether values previously saved in the file should be overwritten
    :type overwrite:    bool
    """
    fct_cache = _HashableCache(filename, overwrite=overwrite)
    return fct_cache.lookup_decorator(fct)

class _HashableCache(object):
    """
    Creates a lookup for a function with hashable arguments and keyword arguments.
    """
    def __init__(self, filename, overwrite=False):
        self._filename = filename
        self._res = []
        if not overwrite:
            self.load()
        self._parse_res()        

    def load(self):
        """
        Load the results from file.
        """
        try:
            with open(self._filename, 'r') as f:
                self._res = pickle.load(f)
        except IOError:
            pass

    def save(self):
        """
        Saves the results to file.
        """
        with open(self._filename, 'w') as f:
            pickle.dump(self._res, f)

    def _parse_res(self):
        """
        Creates the dict of hashable args/kwargs pairs.
        """
        self._lookup_dict = {}
        for args, kwargs, res in self._res:
            self._to_dict(args, kwargs, res)

    def _to_dict(self, args, kwargs, res):
        """
        Adds the result (res) to the lookup dictionary, with keys args and kwargs.
        """
        if args not in self._lookup_dict.keys():
            self._lookup_dict[args] = {}
        self._lookup_dict[args][_dict_hash(kwargs)] = res

    def lookup_decorator(self, fct):
        """
        Returns a decorated version of fct which saves its values to filename
        """
        def inner(*args, **kwargs):
            try:
                res = self._lookup_dict[args][_dict_hash(kwargs)]
            except KeyError:
                res = fct(*args, **kwargs)
                self._to_dict(args, kwargs, res)
                self._res.append((args, kwargs, res))
                self.save()
            return res
        return inner

#----------------HELPER FUNCTIONS---------------------------------------#

def _dict_hash(obj):
    return hash(frozenset(obj))

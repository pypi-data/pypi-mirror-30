#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    28.08.2015 09:11:42 CEST
# File:    spatial_data.py


from __future__ import division

from ptools.monitoring import timing
from ptools.tolerantfloat import tolerantfloat, toleranttuple

#~ import mtools as phys
import copy
import pickle
import numpy as np
import scipy.linalg as la

__all__ = ['SpatialDataReader', 'SpatialDataCache', 'cache_spatial_data']

class SpatialDataReader(object):
    def __init__(self, tol=1e-6, pfile=None, autoload=True, quiet=False):
        r"""
        ...
        
        :param tol: Tolerance with which spatial points are identified as being equal.
        :type tol:  float
        
        :param pfile: File where the data is stored.
        :type pfile:  str
        """
        self.pfile = pfile
        self.results = {}
        self.tol = tol
        self.FloatType = tolerantfloat('FloatType', tol)
        self.TupleType = toleranttuple('TupleType', tol)
        if autoload:
            self.load(quiet=quiet)

    def __getitem__(self, pt):
        """
        Returns the value corresponding to pt if is already in self.points, else returns None.
        """
        return self.results[self.TupleType(pt)]

    def load(self, quiet=False):
        r"""
        Loads the points and their values from ``pfile``. This may overwrite existing points and values!
        """
        try:
            if self.pfile is not None:
                with open(self.pfile, 'rb') as f:
                    state = pickle.load(f)

                self.results = {self.TupleType(p): val for p, val in state['results']}
        except IOError as e:
            if quiet:
                pass
            else:
                raise e

    def filter_line(self, start, end):
        r"""
        Returns the points that are in between start and end on a straight line.
        """
        res = []
        axis = np.array(end) - np.array(start)
        axis_len = la.norm(axis)
        start_pt = np.array(start)
        for pt in self.results.keys():
            delta_pt = self.TupleType(np.array(pt) - start_pt)
            alpha = la.norm(delta_pt) / axis_len
            if alpha < 0 or alpha > 1:
                continue
            if self.TupleType(alpha * np.array(axis)) == delta_pt:
                res.append(pt)
        return res
    

class SpatialDataCache(SpatialDataReader):
    def __init__(self, fct, tol=1e-6, pfile=None, autoload=True, quiet=True):
        r"""
        Caches the data of a function that takes spatial data as an input. The function must be listable, i.e. it must take a list of points as input and create a list of return values corresponding to these input points.
        
        :param fct: Function to be cached.
        :type fct:  function
        
        :param tol: Tolerance with which spatial points are identified as being equal.
        :type tol:  float
        
        :param pfile: File where the data is stored.
        :type pfile:  str
        
        :param quiet:   Determines whether the error is suppressed if pfile doesn't exist on loading.
        :type quiet:    True
        """
        self.fct = fct
        super(SpatialDataCache, self).__init__(tol=tol, pfile=pfile, autoload=autoload, quiet=quiet)

    @timing
    def _filter(self, pts):
        """
        Filter pts against those who are already in self.points.
        pts are assumed to be of type self.TupleType.
        """
        points_all = set(pts)
        points_to_calculate = points_all - set(self.results.keys())
        return list(points_to_calculate), list(points_all)

    @timing
    def calculate(self, pts, autosave=True):
        """
        Call to fct
        """
        # empty list
        if len(pts) == 0:
            return []
        # single point
        if not (hasattr(pts[0], '__iter__') or hasattr(pts[0], '__len__')):
            points = [self.TupleType(pts)]
            single_point = True
        else:
            points = [self.TupleType(pt) for pt in pts]
            single_point = False
            
        points_to_calculate, points_all = self._filter(points)
        values = self.fct(points_to_calculate)

        # write results to main and current points/values
        res = {p: val for p, val in zip(copy.deepcopy(points_to_calculate), copy.deepcopy(values))}
        self.results.update(res)
        if autosave and len(points_to_calculate) > 0:
            self.save()

        # single point -> return only the resulting value, else give the list of results
        if single_point:
            return self.results[points[0]]
        else:
            return [self.results[pt] for pt in points]

    def __call__(self, *args, **kwargs):
        """
        Makes ``calculate`` available through the call operator.
        """
        return self.calculate(*args, **kwargs)

    def save(self, protocol=pickle.HIGHEST_PROTOCOL):
        r"""
        Saves the points and their values to ``pfile``.
        """
        if self.pfile is not None:
            state = {}
            to_save = []
            for key in to_save:
                state[key] = self.__dict__[key]
            state['results'] = [([float(pval) for pval in p], val) for p, val in self.results.items()]
            
            with open(self.pfile, 'wb') as f:
                pickle.dump(state, f, protocol=protocol)

    def load(self, quiet=False):
        r"""
        Loads the points and their values from ``pfile``. This may overwrite existing points and values!
        """
        try:
            if self.pfile is not None:
                with open(self.pfile, 'rb') as f:
                    state = pickle.load(f)

                self.results = {self.TupleType(p): val for p, val in state['results']}
        except IOError as e:
            if quiet:
                pass
            else:
                raise e

def cache_spatial_data(**kwargs):
    """
    Decorator to simplify caching data of a given function.
    """
    def outer(func):
        cache = SpatialDataCache(func, **kwargs)
        def inner(kpt, **kwarguments):
            return cache(kpt, **kwarguments)
        return inner
    return outer

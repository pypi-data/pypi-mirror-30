#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    08.04.2015 10:58:02 CEST
# File:    tolerantfloat.py


class TolerantFloat(float):
    @classmethod
    def set_precision(cls, p):
        cls.precision = p

    @property
    @classmethod
    def precision(cls):
        return cls.precision
        
    @precision.setter
    @classmethod
    def precision(cls, value):
        cls.precision = value
    
    def __eq__(self, other):
        super_eq = super(TolerantFloat, self).__eq__(other)
        if super_eq is True:
            return True
        else:
            try:
                precision = min(self.precision, other.precision)
                return True if abs(self - other) < precision else False
            except AttributeError:
                return super_eq
            except TypeError:
                return NotImplemented

    def __ne__(self, other):
        equal = self.__eq__(other)
        
        if isinstance(equal, bool):
            return not equal
        else:
            return equal


    def __le__(self, other):
        super_le = super(TolerantFloat, self).__lt__(other)
        if super_le is True:
            return True
        # only the equal case is handled incorrectly
        else:
            return self.__eq__(other)
            
    def __ge__(self, other):
        super_ge = super(TolerantFloat, self).__gt__(other)
        if super_ge is True:
            return True
        # only the equal case is handled incorrectly
        else:
            return self.__eq__(other)
        
            
    def _round(self):
        return int(self / self.precision + 0.5) * self.precision

    def __hash__(self):
        return hash(self._round())

def tolerantfloat(name, p):
    return type(name, (TolerantFloat,), {'precision':p})
        
class TolerantTuple(tuple):
    def __new__(cls, x):
        return super(TolerantTuple, cls).__new__(cls, (cls.float_class(xval) for xval in x))

def toleranttuple(name, p):
    return type(name, (TolerantTuple,), {'float_class': tolerantfloat(name, p)})

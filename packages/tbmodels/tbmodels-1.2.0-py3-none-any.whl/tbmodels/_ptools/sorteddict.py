#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    24.06.2015 14:16:42 CEST
# File:    sorteddict.py

class SortedDict(dict):
    """
    sorted dictionary
    """
            
    def __iter__(self):
        for key in sorted(super(SortedDict, self).__iter__()):
            yield key
            
    def keys(self):
        for key in sorted(super(SortedDict, self).keys()):
            yield key
            
    def items(self):
        for item in sorted(super(SortedDict, self).items()):
            yield item
            
    def values(self):
        for key, val in self.items():
            yield val

    def __str__(self):
        return '{' + ', '.join(['\'{}\': {}'.format(*item) for item in self.items()]) + '}'

    def __repr__(self):
        return '{' + ', '.join(['\'{}\': {}'.format(*item) for item in self.items()]) + '}'

    def iteritems(self):
        raise NotImplementedError

    def iterkeys(self):
        raise NotImplementedError

    def itervalues(self):
        raise NotImplementedError

    def viewitems(self):
        raise NotImplementedError

    def viewkeys(self):
        raise NotImplementedError

    def viewvalues(self):
        raise NotImplementedError

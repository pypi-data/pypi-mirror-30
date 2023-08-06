#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    20.04.2015 17:11:07 CEST
# File:    wheel.py

import numbers

class Wheel(object):
    """
    Creates a 'wheel' which can be accessed with an arbitrary int
    (periodically) from a list.
    """
    def __init__(self, wheel):
        self.wheel = wheel
        self.length = len(wheel)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return self.wheel[key % self.length]
        else:
            raise AttributeError

    def __len__(self):
        return self.length

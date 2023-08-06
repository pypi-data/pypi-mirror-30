#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    23.09.2015 15:25:15 CEST
# File:    vec_tools.py

import copy

def neighbours(dim, order = 1):
    res = [[]]
    for _ in range(dim):
        tmp = []
        for vec in res:
            for i in range(-order, order + 1):
                vec_tmp = copy.deepcopy(vec)
                vec_tmp.append(i)
                tmp.append(vec_tmp)
        res = tmp
    return res

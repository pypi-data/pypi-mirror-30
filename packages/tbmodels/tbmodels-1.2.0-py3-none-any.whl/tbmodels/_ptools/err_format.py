#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    29.04.2015 14:47:27 CEST
# File:    err_format.py

import numpy as np

def format_error(val, err, mode='pm'):
    val, err = round_to_error(val, err)
    if mode == 'pm':
        return r'{} \pm {}'.format(val, err)
    if mode == '()':
        err_magnitude = _magnitude(err)
        if err_magnitude < 0:
            string = ('{:.' + str(-err_magnitude) + 'f}').format(val)
            string = '('.join([string[:-1], string[-1]])
            string += ')'
            return string
        else:
            string = str(val)[::-1]
            string = string[:err_magnitude] + ')' + string[err_magnitude] + '(' + string[err_magnitude + 1:]
            return string[::-1]
        #~ else:
    if mode == 'sc':
        err_magnitude = _magnitude(err)
        val_magnitude = _magnitude(val)
        mantissa, exponent = ('{:.' + str(val_magnitude - err_magnitude) + 'e}').format(val).split('e')
        mantissa = '('.join([mantissa[:-1], mantissa[-1]])
        mantissa += ')'
        exp_sign = exponent[0].lstrip('+')
        exp_val = exponent[1:].lstrip('0')
        exponent = exp_sign + exp_val
        if not len(exponent) == 0:
            exponent = ' \\times 10^{' + exponent + '}'
        string = mantissa + exponent
        return string

def round_to_error(val, err):
    err_magnitude = _magnitude(err)
    val = _try_int(round(val, -err_magnitude))
    err = _round_to(err)
    return val, err

def _round_to(x, digits=1):
    magnitude = _magnitude(x)
    val = round(x, -magnitude + digits - 1)
    return _try_int(val)

def _magnitude(x):
    if x == 0:
        return 0
    else:
        return int(np.floor(np.log10(abs(x))))

def _try_int(x):
    int_x = int(x)
    if int_x - x == 0:
        return int_x
    else:
        return x

if __name__ == "__main__":
    print(_round_to(12.0012313, 3))    
    print(format_error(12235.1092313, 131, mode='sc'))    

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    03.08.2015 16:55:36 CEST
# File:    lsf_tools.py

import os
import sys
import time
import numbers
import subprocess
import collections as co

def submit(cmd, time=None, mem=None, scratch=None, cores=None, cwd=None):
    opt_string = ''
    if cores is not None:
        opt_string += ' -n {}'.format(cores)
    if time is not None:
        if isinstance(time, numbers.Integral):
            opt_string += ' -W {}:{:0>2}'.format(time // 60, time % 60)
        elif isinstance(time, str):
            opt_string += ' -W {}'.format(time)
        else:
            raise TypeError('time is of invalid type {}'.format(type(time)))
    if (mem is not None) or (scratch is not None):
        mem_scr = []
        if mem is not None:
            mem_scr.append('mem={}'.format(mem))
        if scratch is not None:
            mem_scr.append('scratch={}'.format(scratch))
        opt_string += ' -R "rusage[{}]"'.format(','.join(mem_scr))
    with open(os.devnull, 'w') as devnull:
        ret = subprocess.check_output('bsub' + opt_string + ' "' + cmd + '"', shell=True, cwd=cwd, stderr=devnull)
    ret = ret.split('<', 1)[1].split('>', 1)[0]
    return int(ret)

def is_alive(num):
    return num in get_joblist()

def get_joblist(status=None):
    if status is None:
        tag = ''
    elif status == 'p':
        tag = '-p'
    elif status == 'r':
        tag = '-r'
    else:
        raise ValueError('unknown status "{}"'.format(status))
    with open(os.devnull, 'w') as devnull:
        lines = filter(None, subprocess.check_output('bjobs ' + tag, shell=True, stderr=devnull).split('\n'))
    lines = lines[1:]
    return [int(line.split(' ')[0]) for line in lines]
    
def wait_for(num, timeout=5, init_timeout=20):
    if isinstance(num, numbers.Integral):
        num = [num]
    time.sleep(init_timeout)
    while any([is_alive(n) for n in num]):
        time.sleep(timeout)

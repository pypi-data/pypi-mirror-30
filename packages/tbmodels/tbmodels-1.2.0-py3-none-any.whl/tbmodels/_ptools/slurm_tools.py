#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    04.04.2016 14:54:05 CEST
# File:    slurm_tools.py

import os
import time
import subprocess

def submit(cmd, time=None, mem=None, cores=1, cwd=None):
    for n in range(40, 0, -1):
        if cores % n == 0:
            tasks_per_node = n
            nodes = cores // n
            break

    sbatch_options = [
        'sbatch',
        '--get-user-env',
        '--partition=dphys_compute',
        '--nodes={}'.format(nodes),
        '--ntasks-per-node={}'.format(tasks_per_node),
        "--wrap='{}'".format(cmd)
    ]
    if mem is not None:
        sbatch_options.append('--mem={}'.format(mem))
    if time is not None:
        sbatch_options.append('--time-min={}'.format(time))

    subprocess.check_output(' '.join(sbatch_options), shell=True, cwd=cwd)
    return int(ret.split()[-1])

#~ def is_alive(num):
    #~ return num in get_joblist()

#~ def get_joblist(status=None):
    #~ if status is None:
        #~ tag = ''
    #~ elif status == 'p':
        #~ tag = '-p'
    #~ elif status == 'r':
        #~ tag = '-r'
    #~ else:
        #~ raise ValueError('unknown status "{}"'.format(status))
    #~ with open(os.devnull, 'w') as devnull:
        #~ lines = filter(None, subprocess.check_output('bjobs ' + tag, shell=True, stderr=devnull).split('\n'))
    #~ lines = lines[1:]
    #~ return [int(line.split(' ')[0]) for line in lines]
    
#~ def wait_for(num, timeout=5, init_timeout=20):
    #~ if isinstance(num, int):
        #~ num = [num]
    #~ time.sleep(init_timeout)
    #~ while any([is_alive(n) for n in num]):
        #~ time.sleep(timeout)

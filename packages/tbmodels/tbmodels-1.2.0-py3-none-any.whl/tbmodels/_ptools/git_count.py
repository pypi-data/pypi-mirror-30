#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    26.01.2015 15:37:59 CET
# File:    git_count.py

from __future__ import division, print_function

import subprocess

def git_count(cwd='./'):
    try:
        branches = list(filter(None, subprocess.check_output('git branch', shell=True, cwd=cwd).decode('utf-8').split('\n')))
    except subprocess.CalledProcessError:
        return None, None
    if len(branches) == 0:
        return 0, 0

    hashes = list(filter(None, subprocess.check_output('git rev-list --all', shell=True).decode('utf-8').split('\n')))

    chksum = 0
    for num in hashes:
        chksum += int(num, base=16)

    return len(hashes), chksum


#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    01.02.2015 18:17:45 CET
# File:    argus.py

from __future__ import division, print_function

import subprocess

def count_active():
    """
    Counts the number of active jobs on Brutus
    """
    jobs = subprocess.check_output('bjobs').decode('utf-8')
    return len([line for line in jobs.split('\n') if line]) - 1


#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    04.04.2016 15:58:58 CEST
# File:    submit_tools.py

import warnings
import subprocess

hostname = str(subprocess.check_output('hostname')).strip()
if 'monch' in hostname:
    from slurm_tools import *
elif any(name in hostname for name in ['brutus', 'euler']):
    from lsf_tools import *
else:
    raise ImportError('unknown host')

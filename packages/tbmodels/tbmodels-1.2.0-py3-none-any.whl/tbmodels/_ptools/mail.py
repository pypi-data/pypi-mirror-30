#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    01.02.2015 17:55:46 CET
# File:    mail.py

import subprocess

def send(subj='', msg='', dest='greschd@gmx.ch'):
    """
    Sends an Email to dest, with given subject (subj) and message (msg)
    """
    proc1 = subprocess.Popen(['echo', msg], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['mail', '-s', subj, dest], stdin=proc1.stdout)
    proc1.stdout.close()
    return proc2.communicate()[0]



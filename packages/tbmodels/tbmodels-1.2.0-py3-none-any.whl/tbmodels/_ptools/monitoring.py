#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Mario S. Könz <mskoenz@gmx.net>, Dominik Gresch <greschd@gmx.ch>
# Date:    01.04.2015 12:46:51 CEST
# File:    monitoring.py

from __future__ import print_function

import time
import warnings
import collections

from .termcolor import color, GREENB
from .io_manip import ms_time_str

__all__ = ['Timer', "progress_bar", "Monitor"]

class Timer(object):
    """
    Context manager for timing
    """
    def __init__(self, descr='Timer', silent=False, div=1, color=True):
        self.descr = descr
        self.silent = silent
        self.div = div
        self.start = 0
        self.end = 0
        self.diff = 0
        self._watch = 0
        self._color = color

    @property
    def watch(self):
        return time.time() - self._watch

    @property
    def time(self):
        return time.time() - self.start

    def reset(self):
        self._watch = time.time()

    def __enter__(self):
        self.start = time.time()
        self._watch = self.start
        return self

    def __exit__(self, type_, value, traceback):
        self.diff = self.time / self.div
        if not self.silent:
            if self._color:
                print('{green}{}: {greenb}{:.5f}s{none}'.format(
                    self.descr, self.diff, **color
                ))
            else:
                print('{}: {:.5f}s'.format(self.descr, self.diff))
                

def progress_bar(p, size=50):
    """
    p is a number between 0 and 1 and progress_bar will return a string
    that contains a progress bar representing that progress.
    """

    bars = int(min(1, p) * size)
    bar = "<"

    bar += "|" * bars
    bar += " " * (size - bars)
    bar += ">"
    end = "{0:3}%".format(int(p * 100))

    col = color[["red", "yellow", "green", "cyan"][min(int(p * 3), 3)]] # duh! ;-)

    if p > 1:
        warnings.warn("progress > 100%")
    return "{}{}{none}{}".format(col, bar, end, **color)

class Monitor(object):
    def __init__(self, seq, name="unknown"):
        self.seq = seq
        self.name = name

    def __iter__(self):
        GREENB(self.name)
        print("--- initializing progress bar ---")
        N = len(self)
        max_eta = 10
        eta = collections.deque([[0, 0] for _ in range(max_eta)])
        last_i_x = 0
        n_len = str(len(str(N)))
        format_str = "{renter}({:>" + n_len + "}/{}) {} {blue}done in {blueb}{}{none}"
        with Timer(silent=True) as t:
            for i_x, x in enumerate(self.seq):
                passed = t.watch
                if passed > 1:
                    p = (i_x + 1.0) / N

                    eta.rotate(-1)
                    eta[-1] = [(i_x - last_i_x), passed]
                    last_i_x = i_x
                    t.reset()
                    idx_per_sec = sum([eta_val[0] for eta_val in eta]) / sum([eta_val[1] for eta_val in eta])

                    predict = (N-i_x) / idx_per_sec

                    print(format_str.format(
                        i_x + 1,
                        N,
                        progress_bar(p),
                        ms_time_str(predict),
                        **color)
                         )

                yield x

        print(
            "{renter}({}/{}) {} {green}done in {greenb}{}{none}".format(
                N,
                N,
                progress_bar(1),
                ms_time_str(t.diff),
                **color)
            )

    def __len__(self):
        return len(self.seq)

#--------------------- DECORATORS --------------------------------------#

def timing(fct):
    def inner(*args, **kwargs):
        with Timer(fct.__name__):
            return fct(*args, **kwargs)
    return inner

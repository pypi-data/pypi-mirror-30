#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    06.11.2015 13:50:23 CET
# File:    messaging.py

import copy

class MessageFilter(object):
    _msg_filter_stack = []
    _active_msg_filter = None
    
    def __init__(self, name, filter_fct=None):
        self.name = name
        if self.__class__._active_msg_filter is None:
            if filter_fct is None:
                self.__class__._active_msg_filter = staticmethod(lambda *args, **kwargs: True)
                self._set_filter = False
            else:
                self.__class__._active_msg_filter = staticmethod(filter_fct)
                self._set_filter = True
                
    def __enter__(self):
        self.__class__._msg_filter_stack.append(self.name)
        return self

    def __exit__(self, type_, value, traceback):
        assert(self.__class__._msg_filter_stack.pop() == self.name)
        if self._set_filter:
            self.__class__._active_msg_filter = None

    @classmethod
    def get_stacklevel(cls):
        return len(cls._msg_filter_stack) - 1

    @classmethod
    def get_stack(cls):
        return copy.deepcopy(cls._msg_filter_stack)

class MessageType(str):
    def __init__(self, string):
        if string is None:
            string = "other"
        valid_types = ["data", "status", "progress", "warning", "other"]
        if string not in ["data", "status", "progress", "warning", "other"]:
            raise ValueError(
                "invalid message type '{0}'\nPossible types: {1}".format(
                    string,
                    ', '.join("'" + str(x) + "'" for x in valid_types)
                )
            )
        super(MessageType, self).__init__(string)

def print_msg(string, msg_type=None):
    msg_type = MessageType(msg_type)
    if MessageFilter._active_msg_filter(msg_type):
        print(string)

with MessageFilter("outermost"):
    print_msg("foo", "bla")

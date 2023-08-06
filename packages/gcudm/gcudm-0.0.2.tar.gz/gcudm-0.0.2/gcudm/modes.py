#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/8/18
"""
.. currentmodule:: modes
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module can be used to describe the mode in which the library is running.
"""

from singleton_decorator import singleton


@singleton
class Modes(object):
    """
    Represents the mode in which the library is currently being run.  If
    the module has been loaded to generate documentation, the `sphinx`
    attribute should be set to `True`.
    """
    def __init__(self):
        self.sphinx = False
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/5/18
"""
.. currentmodule:: model
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'model' module.
"""

import pkgutil
import gcudm.models

_SKIP_ON_LOAD = [

]  #: the names of modules that are not loaded automatically with the model


def load():
    """
    Load the data model.
    """
    package = gcudm.models
    prefix = package.__name__ + '.'
    for importer, modname, ispkg in pkgutil.walk_packages(
            package.__path__, prefix):
        if modname in _SKIP_ON_LOAD:
            continue
        else:
            _ = __import__(modname)


#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/8/18
"""
.. currentmodule:: esblaw
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'esblaw' module.
"""

from .esbs import EsbMixin
from ..model import model
from ..base import Base, ModelMixin


@model(label='Emergency Services Boundary (Law)')
class EsbLaw(Base, ModelMixin, EsbMixin):
    """
    Emergency service boundaries for law enforcement define the areas to which
    law enforcement responds.
    """

    __tablename__ = 'esblaw'


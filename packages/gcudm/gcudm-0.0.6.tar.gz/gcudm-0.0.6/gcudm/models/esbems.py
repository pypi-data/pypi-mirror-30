#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/8/18
"""
.. currentmodule:: esbems
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'esbems' module.
"""

from .esbs import EsbMixin
from ..model import model
from ..base import Base, ModelMixin


@model(label='Emergency Services Boundary (EMS)')
class EsbEms(Base, ModelMixin, EsbMixin):
    """
    This table needs a description.
    """

    __tablename__ = 'esbems'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/8/18
"""
.. currentmodule:: esbpsap
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'esbpsap' module.
"""

from .esbs import EsbMixin
from ..model import model
from ..base import Base, ModelMixin


@model(label='Emergency Services Boundary (PSAP)')
class EsbPsap(Base, ModelMixin, EsbMixin):
    """
    This table needs a description.
    """

    __tablename__ = 'esbpsap'
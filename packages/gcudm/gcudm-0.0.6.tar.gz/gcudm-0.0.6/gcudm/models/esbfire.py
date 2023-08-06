#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/8/18
"""
.. currentmodule:: esbfire
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Say something descriptive about the 'esbfire' module.
"""

from .esbs import EsbMixin
from ..model import model
from ..base import Base, ModelMixin


@model(label='Emergency Services Boundary (Fire)')
class EsbFire(Base, ModelMixin, EsbMixin):
    """
    This table needs a description.
    """

    __tablename__ = 'esbfire'
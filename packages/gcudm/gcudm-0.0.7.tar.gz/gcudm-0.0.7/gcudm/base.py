#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/4/18
"""
.. currentmodule:: base
.. moduleauthor:: Pat Daburu <pat@daburu.net>

The GeoAlchemy declarative base for the data model is defined in this module
along with some other helpful classes.
"""
from .meta import column, ColumnMeta, Requirement
from .types import GUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, DateTime


Base = declarative_base()  #: This is the model's declarative base.


class ModelMixin(object):
    """
    This is the parent class for all entity classes in the model.  It defines
    common fields.
    """
    gcUnqId = column(
        GUID,
        meta=ColumnMeta(
            label='GeoComm ID',
            guaranteed=True,
            calculated=True
        ),
        primary_key=True
    )

    srcOfData = column(
        String,
        ColumnMeta(
            label='Data Source'
        )
    )

    srcLastEd = column(
        DateTime,
        ColumnMeta(
            label='Source of Last Update'
        )
    )

    uploadAuth = column(
        String,
        ColumnMeta(
            label='Upload Authority'
        )
    )

    updateDate = column(
        DateTime,
        ColumnMeta(
            label='Last Update'
        )
    )

    effective = column(
        DateTime,
        ColumnMeta(
            label='Effective Date',
            requirement=Requirement.REQUESTED
        )
    )

    expire = column(
        DateTime,
        ColumnMeta(
            label='Expiration Date',
            requirement=Requirement.REQUESTED
        )
    )

    srcUnqId = column(
        String,
        ColumnMeta(
            label='NENA ID',
            nena='RCL_NGUID',
            requirement=Requirement.REQUESTED
        )
    )

    @classmethod
    def geometry_type(cls):
        return 'LINESTRING'  # TODO: Retrieve the geometry type.


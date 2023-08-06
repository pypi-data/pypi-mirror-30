#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/5/18
"""
.. currentmodule:: road_centerlines
.. moduleauthor:: Pat Daburu <pat@daburu.net>




"""

from ..model import model
from ..meta import column, ColumnMeta, Requirement, Usage
from ..base import Base, ModelMixin
from sqlalchemy import Column, Integer, String, DateTime
from geoalchemy2 import Geometry


@model(label='Road Centerlines')
class RoadCenterline(Base, ModelMixin):
    """
    Road centerlines are the principal polyline features that represent
    road segments traversable by most emergency vehicles.
    """

    __tablename__ = 'road_centerlines'

    geom = Column(Geometry('LINESTRING'))

    srcFullNam = column(
        String,
        ColumnMeta(
            label='Source Full Name',
            requirement=Requirement.REQUESTED
        )
    )  #: here is an annotation!

    addRngPreL = column(
        String,
        ColumnMeta(
            label='Left Address Number Prefix',
            requirement=Requirement.REQUESTED,
            nena='AdNumPre_L',
            usage=Usage.DISPLAY

        )
    )

    addRngPreR = column(
        String,
        ColumnMeta(
            label='Right Address Number Prefix',
            requirement=Requirement.REQUESTED,
            nena='AdNumPre_R',
            usage=Usage.DISPLAY

        )
    )

    fromAddL = column(
        String,
        ColumnMeta(
            label="Left 'From' Address",
            nena='FromAddr_L',
            requirement=Requirement.REQUESTED,
            usage=Usage.DISPLAY
        )
    )

    toAddL = column(
        String,
        ColumnMeta(
            label="Left 'To' Address",
            nena='ToAddr_L',
            requirement=Requirement.REQUESTED,
            usage=Usage.DISPLAY
        )
    )

    fromAddR = column(
        String,
        ColumnMeta(
            label="Right 'From' Address",
            nena='FromAddr_R',
            requirement=Requirement.REQUESTED,
            usage=Usage.DISPLAY
        )
    )

    toAddR = column(
        String,
        ColumnMeta(
            label="Right 'To' Address",
            nena='ToAddr_R',
            requirement=Requirement.REQUESTED,
            usage=Usage.DISPLAY
        )
    )

    rngType = column(
        String,
        ColumnMeta(
            label='Ranging Type'
        )
    )

    parityL = column(
        String,
        ColumnMeta(
            label='Parity Left',
            nena='Parity_L'
        )
    )

    parityR = column(
        String,
        ColumnMeta(
            label='Parity Right',
            nena='Parity_R'
        )
    )

    preMod = column(
        String,
        ColumnMeta(
            label='Street Name Pre Modifier',
            nena='St_PreMod'
        )
    )

    preDir = column(
        String,
        ColumnMeta(
            label='Street Name Pre Directional',
            nena='St_PreDir'
        )
    )

    preType = column(
        String,
        ColumnMeta(
            label='Street Name Pre Type',
            nena="St_PreTyp"
        )
    )

    preTypeSep = column(
        String,
        ColumnMeta(
            label='Street Name Pre Type Separator',
            nena='St_PreSep'
        )
    )

    strName = column(
        String,
        ColumnMeta(
            label='Street Name',
            nena='StreetName',
            requirement=Requirement.REQUIRED
        )
    )

    postType = column(
        String,
        ColumnMeta(
            label='Street Name Post Type',
            nena='St_PosTyp'
        )
    )
    
    postDir = column(
        String,
        ColumnMeta(
            label='Street Name Post Directional',
            nena='St_PosDir'
        )
    )

    postMod = column(
        String,
        ColumnMeta(
            label='Street Name Post Modifier',
            nena='St_PosMod'
        )
    )

    lgcyPreMod = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Pre Modifier',
        )
    )

    lgcyPreDir = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Pre Directional',
            nena=None
        )
    )
    
    lgcyPrType = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Pre Type',
            nena='LSt_PreDir'
        )
    )
    
    lgcyPrTySp = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Pre Type Separator'
        )
    )

    lgcyName = column(
        String,
        ColumnMeta(
            label='Legacy Street Name',
            nena='LSt_Name'
        )
    )

    lgcyType = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Post Type',
            nena='LSt_Type'
        )
    )
    
    lgcyPstDir = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Post Directional',
            nena='LStPosDir'
        )
    )

    lgcyPstMod = column(
        String,
        ColumnMeta(
            label='Legacy Street Name Post Modifier'
        )
    )
    
    esnL = column(
        String,
        ColumnMeta(
            label='ESN Left',
            nena='ESN_L',
            requirement=Requirement.REQUIRED
        )
    )
    
    esnR = column(
        String,
        ColumnMeta(
            label='ESN Right',
            nena='ESN_R',
            requirement=Requirement.REQUIRED
        )
    )

    msagCommL = column(
        String,
        ColumnMeta(
            label='MSAG Community Name Left',
            nena='MSAGComm_L',
            requirement=Requirement.REQUIRED,
            usage=Usage.DISPLAY
        )
    )

    msagCommR = column(
        String,
        ColumnMeta(
            label='MSAG Community Name Right',
            nena='MSAGComm_R',
            requirement=Requirement.REQUIRED,
            usage=Usage.DISPLAY
        )
    )

    countryL = column(
        String,
        ColumnMeta(
            label='Country Left',
            nena='Country_L'
        )
    )

    countryR = column(
        String,
        ColumnMeta(
            label='Country Right',
            nena='Country_R'
        )
    )

    stateL = column(
        String,
        ColumnMeta(
            label='State Left',
            nena='State_L',
            usage=Usage.DISPLAY
        )
    )

    stateR = column(
        String,
        ColumnMeta(
            label='State Right',
            nena='State_R',
            usage=Usage.DISPLAY
        )
    )

    addCodeL = column(
        String,
        ColumnMeta(
            label='Additional Code Left',
            nena='AddCode_L'
        )
    )

    addCodeR = column(
        String,
        ColumnMeta(
            label='Additional Code Right',
            nena='AddCode_R'
        )
    )

    incMuniL = column(
        String,
        ColumnMeta(
            label='Incorporated Municipality Left',
            nena='IncMuni_L',
            usage=Usage.DISPLAY
        )
    )

    incMuniR = column(
        String,
        ColumnMeta(
            label='Incorporated Municipality Right',
            nena='IncMuni_R',
            usage=Usage.DISPLAY
        )
    )
    
    unincCommL = column(
        String,
        ColumnMeta(
            label='Unincorporated Community Left',
            nena='UnincCom_L'
        )
    )
    
    unincCommR = column(
        String,
        ColumnMeta(
            label='Unincorporated Community Right',
            nena='UnincCom_R'
        )
    )












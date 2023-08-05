#! /usr/bin/env python
# -*- coding: utf8 -*-

"""
Created by jianbing on 2017-11-03
"""

from aenum import Enum, unique


@unique
class Tag(Enum):
    FULL = 1000
    SMOKE = 1

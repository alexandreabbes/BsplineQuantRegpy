#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models module - Régressions quantile avec B-splines de degré 1 à 4
"""

from .quantile_reg import (
    SplineLinearQuant,
    SplineQuadraticQuant,
    SplineCubicQuant,
    SplineQuarticQuant,
    rhotau
)

__all__ = [
    'SplineLinearQuant',
    'SplineQuadraticQuant',
    'SplineCubicQuant',
    'SplineQuarticQuant',
    'rhotau'
]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models module - Quantile regressions with B-splines of degree 1 to 4

Exported functions:
- SplineLinearQuant : Regression with linear splines
- SplineQuadraticQuant : Regression with quadratic splines
- SplineCubicQuant : Regression with cubic splines
- SplineQuarticQuant : Regression with quartic splines
- quantile_spline : Unified interface
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models module - Régressions quantile avec B-splines de degré 1 à 4


Fonctions exportées:
- SplineLinearQuant : Régression avec splines linéaires
- SplineQuadraticQuant : Régression avec splines quadratiques
- SplineCubicQuant : Régression avec splines cubiques
- SplineQuarticQuant : Régression avec splines quartiques
- quantile_spline : Interface unifiée
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

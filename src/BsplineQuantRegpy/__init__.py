#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BsplineQuantRegpy - Quantile Regression with Constrained Splines
==============================================================

Package pour la régression quantile avec splines sous contraintes
(monotonie, convexité, dérivée troisième).

Degrés disponibles:
- 1: Linéaire (affine par morceaux)
- 2: Quadratique
- 3: Cubique
- 4: Quartique
"""

__version__ = "1.0.1"
__author__ = "Alexandre Abbes"
__email__ = "alexandre.abbes@proton.me"
__license__ = "GPLv3"

# ============ MODÈLES DE RÉGRESSION ============
from .models.quantile_reg import (
    SplineLinearQuant,
    SplineQuadraticQuant,
    SplineCubicQuant,
    SplineQuarticQuant,
    quantile_spline,  # Interface unifiée
)

# ============core

from .core.bases import build_bsplines_and_deriv
from .core.constraints import (apply_karlin_constraints_cubic,
                               apply_karlin_constraints_quadratic,
                               apply_val_constraints)

# ============ GUI ============
# La GUI n'est pas importée automatiquement pour éviter les dépendances Tkinter
# mais on expose une fonction pour la lancer
def run_gui():
    """Lance l'interface graphique."""
    from .gui.Quant_reg_tk import main
    main()

# ============ EXPORT ============
__all__ = [
    # Modèles
    "SplineLinearQuant",
    "SplineQuadraticQuant",
    "SplineCubicQuant",
    "SplineQuarticQuant",
    "quantile_spline",
    # Cœur
    "build_bsplines_and_deriv",
    "apply_karlin_constraints_cubic",
    "apply_karlin_constraints_quadratic",
    "apply_val_constraints",
    # GUI
    "run_gui",
]

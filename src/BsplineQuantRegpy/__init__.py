#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BsplineQuantRegpy - Quantile Regression with Constrained B-Splines
==================================================================

Package pour la régression quantile avec splines sous contraintes
(monotonie, convexité, dérivée troisième).

Degrés disponibles:
- 1: Linéaire (affine par morceaux)
- 2: Quadratique
- 3: Cubique
- 4: Quartique

Auteur: Alexandre Abbes
Version: 1.0.1
Licence: GPLv3
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
    quantile_spline
)

# ============ CŒUR ============
from .core.bases import build_bsplines_and_deriv
from .core.constraints import (
    apply_karlin_constraints_cubic,
    apply_karlin_constraints_quadratic,
    apply_val_constraints,
)

# ============ EXEMPLES ============
from .examples import (
    logistic_example,
    example_temperature,
    example_temperature_basic,
    quick_start,
    quick_start2,
)

# ============ GUI ============
# La GUI n'est pas importée automatiquement pour éviter les dépendances Tkinter
# mais on expose une fonction pour la lancer

def run_gui():
    """Lance l'interface graphique."""
    from .gui.Quant_reg_tk import main
    main()

def run_basic_example():
    """Lance l'exemple basique."""
    from .examples.example_basic import test_all_degrees
    test_all_degrees()


    """Lance l'analyse des données de température."""

from .examples.example_temperature import run_temperature_analysis
from .examples.example_temperature_basic import run_temperature_analysis_basic    


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
    # Exemples
    "run_logistic_example",
    "run_basic_example",
    "run_temperature_analysis",
    "run_temperature_analysis_basic"
    "quick_start"
    "quick_start2"
    # GUI
    "run_gui",
]

# ============ INFORMATION ============
print(f"BsplineQuantRegpy v{__version__} chargé")
print(f"Auteur: {__author__}")
print("Fonctions disponibles: SplineLinearQuant, SplineQuadraticQuant, SplineCubicQuant, SplineQuarticQuant")
print("Pour lancer la GUI: run_gui()")

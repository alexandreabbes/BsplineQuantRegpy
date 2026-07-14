#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BsplineQuantRegpy - Quantile Regression with Constrained B-Splines
==================================================================

Package pour la régression quantile avec splines sous contraintes
de forme (monotonie, convexité, dérivée troisième).

Auteur: Alexandre Abbes
Version: 1.0.1
Licence: GPLv3

DESCRIPTION
-----------
Ce package implémente la régression quantile avec des B-splines
de degrés 1 à 4, sous contraintes de forme (monotonie, convexité,
dérivée troisième). Les contraintes sont appliquées via la
caractérisation de Karlin-Studden, formulée comme un problème
de programmation conique du second ordre (SOCP).

Ce package utilise les bibliothèques B-spline de SciPy pour la
construction des splines et CVXPY pour l'optimisation SOCP.

PACKAGES RELIÉS
---------------
Ce package est le l'équivalent Python de **BsplineQuantReg** (R),
disponible sur le CRAN (https://cran.r-project.org/package=BsplineQuantReg).

Le package R **BsplineQuantReg** propose des splines cubiques
avec contraintes et est entièrement self-contained (calculs de
splines et polynômes intégrés). Il est lui-même complémentaire
de **cobs** (Constrained B-Splines) qui traite les splines
linéaires et quadratiques.

Contrairement à cobs (R) qui ne traite que des splines quadratiques,
ce package (Python) étend la méthode aux splines cubiques et
quartiques avec des contraintes exactes sur tout l'intervalle
(pas seulement aux nœuds).

Packages R associés :

- **BsplineQuantReg** (R) : Splines cubiques contraintes, self-contained
  https://cran.r-project.org/package=BsplineQuantReg

- **cobs** (R) : Constrained B-Splines Smoothing (linéaires et quadratiques)
  https://cran.r-project.org/package=cobs

- **quantreg** (R) : Quantile Regression (splines linéaires uniquement)
  https://cran.r-project.org/package=quantreg

FONCTIONNALITÉS
---------------
- Régression quantile avec splines de degré 1 à 4
- Contraintes de monotonie (croissant/décroissant)
- Contraintes de convexité (convexe/concave)
- Contraintes sur la dérivée troisième
- Contraintes uniformes ou par région
- Interface graphique (Tkinter)
- Multiples solveurs supportés (CLARABEL, ECOS, SCS, MOSEK)

MODULES
-------
core/           - Construction des B-splines et contraintes de Karlin
models/         - Fonctions de régression quantile (degrés 1 à 4)
gui/            - Interface graphique Tkinter
examples/       - Exemples d'utilisation

FONCTIONS PRINCIPALES
---------------------
SplineLinearQuant      - Régression avec splines linéaires (degré 1)
SplineQuadraticQuant   - Régression avec splines quadratiques (degré 2)
SplineCubicQuant       - Régression avec splines cubiques (degré 3)
SplineQuarticQuant     - Régression avec splines quartiques (degré 4)
quantile_spline        - Interface unifiée pour tous les degrés
run_gui                - Lance l'interface graphique

EXEMPLES
--------
Voici un exemple d'utilisation du package ::

    import numpy as np
    from BsplineQuantRegpy import SplineCubicQuant, run_gui

    # Générer des données
    x = np.linspace(0, 1, 100)
    y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.05*np.random.randn(100)
    knots = np.quantile(x, np.linspace(0, 1, 11))

    # Régression avec contrainte croissante
    result = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)

    # Évaluer la spline
    x_eval = np.linspace(0, 1, 200)
    y_eval = result(x_eval)

    # Lancer l'interface graphique
    run_gui()

RÉFÉRENCES BIBLIOGRAPHIQUES
---------------------------
Abbes, A. (2025). Quantile regression with cubic polynomial splines
under shape constraints with applications.
doi:10.5281/zenodo.17427913

He, X., & Shi, P. (1998). Monotone B-spline smoothing.
Journal of the American Statistical Association, 93(442), 643-650.

Karlin, S., & Studden, W.J. (1966). Tchebycheff Systems:
With Applications in Analysis and Statistics. Interscience Publishers.

Papp, D., & Alizadeh, F. (2014). Shape-Constrained Estimation
Using Nonnegative Splines. Journal of Computational and Graphical
Statistics, 23(1), 211-231.
"""

__version__ = "1.0.1"
__author__ = "Alexandre Abbes"
__email__ = "alexandre.abbes@proton.me"
__license__ = "GPLv3"

# ============ MODÈLES ============
from .models.quantile_reg import (
    SplineLinearQuant,
    SplineQuadraticQuant,
    SplineCubicQuant,
    SplineQuarticQuant,
    quantile_spline,
)

# ============ CŒUR ============
from .core.bases import build_bsplines_and_deriv
from .core.constraints import (
    apply_karlin_constraints_cubic,
    apply_karlin_constraints_quadratic,
    apply_val_constraints,
)

# ============ EXEMPLES ============
from .examples import run_logistic_example
from .examples.quick_start import main as quick_start
from .examples.quick_start2 import main as quick_start2
from .examples.comparison_example import main as run_comparison_example
from .examples.example_temperature import run_temperature_analysis


def run_basic_example():
    """Lance l'exemple basique."""
    from .examples.example_basic import test_all_degrees
    test_all_degrees()


# ============ GUI ============
def run_gui():
    """
    Lance l'interface graphique Tkinter.

    Cette fonction est le point d'entrée principal pour l'interface
    graphique. Elle ouvre une fenêtre interactive permettant de :

    - Charger des données
    - Configurer les splines et les contraintes
    - Lancer des régressions
    - Visualiser et exporter les résultats

    Returns
    -------
    None
        La fonction lance l'interface et ne retourne rien.

    Examples
    --------
    Lancement de l'interface graphique ::

        from BsplineQuantRegpy import run_gui
        run_gui()

    See Also
    --------
    BsplineQuantRegpy.gui.Quant_reg_tk : Module GUI complet
    """
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
    # Exemples
    "run_logistic_example",
    "run_comparison_example",
    "run_basic_example",
    "run_temperature_analysis",
    "quick_start",
    "quick_start2",
    # GUI
    "run_gui",
]

print(f"BsplineQuantRegpy v{__version__} chargé")
print(f"Auteur: {__author__}")
print("Fonctions disponibles: SplineLinearQuant, SplineQuadraticQuant, SplineCubicQuant, SplineQuarticQuant")
print("Pour lancer la GUI: run_gui()")
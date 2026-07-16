#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
BsplineQuantRegpy - Quantile Regression with Constrained B-Splines
==================================================================

Package for quantile regression with shape-constrained splines
(monotonicity, convexity, third derivative).


DESCRIPTION
-----------
This package implements quantile regression with B-splines of
degrees 1 to 4, under shape constraints (monotonicity, convexity,
third derivative). Constraints are applied via the
Karlin-Studden characterization, formulated as a second-order
cone programming (SOCP) problem.

This package uses SciPy's B-spline libraries for spline
construction and CVXPY for SOCP optimization.

RELATED PACKAGES
----------------
This package is the Python equivalent of **BsplineQuantReg** (R),
available on CRAN (https://cran.r-project.org/package=BsplineQuantReg).

The R package **BsplineQuantReg** provides cubic splines with
constraints and is fully self-contained (integrated spline and
polynomial computations). It is itself complementary to
**cobs** (Constrained B-Splines), which handles linear and
quadratic splines.

Unlike cobs (R), which only handles quadratic splines, this
package (Python) extends the method to cubic and quartic splines
with exact constraints over the entire interval (not just at knots).

Related R packages:

- **BsplineQuantReg** (R): Constrained cubic splines, self-contained
  https://cran.r-project.org/package=BsplineQuantReg

- **cobs** (R): Constrained B-Splines Smoothing (linear and quadratic)
  https://cran.r-project.org/package=cobs

FEATURES
--------
- Quantile regression with splines of degree 1 to 4
- Monotonicity constraints (increasing/decreasing)
- Convexity constraints (convex/concave)
- Third derivative constraints
- Uniform or region-specific constraints
- Graphical user interface (Tkinter)
- Multiple supported solvers (CLARABEL, ECOS, SCS, MOSEK)

MODULES
-------
- core/           - B-spline construction and Karlin constraints
- models/         - Quantile regression functions (degrees 1 to 4)
- gui/            - Tkinter graphical user interface
- examples/       - Usage examples

MAIN FUNCTIONS
--------------
- SplineLinearQuant      - Regression with linear splines (degree 1)
- SplineQuadraticQuant   - Regression with quadratic splines (degree 2)
- SplineCubicQuant       - Regression with cubic splines (degree 3)
- SplineQuarticQuant     - Regression with quartic splines (degree 4)
- quantile_spline        - Unified interface for all degrees
- run_gui                - Launch the graphical user interface

EXAMPLES
--------
Here is an example of using the package::

    import numpy as np
    from BsplineQuantRegpy import SplineCubicQuant, run_gui

    # Generate data
    x = np.linspace(0, 1, 100)
    y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.05*np.random.randn(100)
    knots = np.quantile(x, np.linspace(0, 1, 11))

    # Regression with increasing constraint
    result = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)

    # Evaluate the spline
    x_eval = np.linspace(0, 1, 200)
    y_eval = result(x_eval)

    # Launch the graphical user interface
    run_gui()

REFERENCES
----------
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

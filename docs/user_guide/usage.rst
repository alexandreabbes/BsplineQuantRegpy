Utilisation
===========

Avec contrainte de convexité (degree>=2)
----------------------------------------

.. code-block:: python

    from BsplineQuantRegpy import SplineQuadraticQuant

    # Données avec forme convexe
    x = np.linspace(0, 1, 100)
    y = x**2 + 0.05*np.random.randn(100)
    knots = np.quantile(x, np.linspace(0, 1, 11))

    result = SplineQuadraticQuant(x, y, knots, tau=0.5, convex=1)

Interface unifiée
-----------------

.. code-block:: python

    from BsplineQuantRegpy import quantile_spline

    # Spline cubique avec contrainte croissante
    result = quantile_spline(x, y, knots, degree=3, tau=0.5, monot=1)

    # Spline quartique avec contrainte convexe
    result = quantile_spline(x, y, knots, degree=4, tau=0.5, convex=1)

Interface graphique (GUI)
-------------------------

.. code-block:: python

    from BsplineQuantRegpy import run_gui
    run_gui()

Paramètres des fonctions
------------------------

Les principales fonctions acceptent les paramètres suivants :

- `x` : Variables explicatives (1D)
- `y` : Variables à expliquer (1D)
- `knots` : Nœuds pour les B-splines
- `tau` : Quantile à estimer (entre 0 et 1)
- `monot` : Contrainte de monotonie (0, 1, -1)
- `convex` : Contrainte de convexité (0, 1, -1)
- `deriv3` : Contrainte sur la dérivée troisième (0, 1, -1)
- `solver` : Solveur SOCP à utiliser
- `n_int` : Nombre de points d'évaluation pour les contraintes
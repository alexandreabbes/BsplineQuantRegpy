Utilisation
===========

Exemple basique
---------------

Voici un exemple d'utilisation du package :

.. code-block:: python

    import numpy as np
    from BsplineQuantRegpy import SplineCubicQuant

    # Générer des données
    x = np.linspace(0, 1, 100)
    y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.05*np.random.randn(100)

    # Définir les nœuds
    knots = np.quantile(x, np.linspace(0, 1, 11))

    # Régression quantile avec contrainte croissante
    result = SplineCubicQuant(x, y, knots, tau=0.5, monot=1)

    # Évaluer la spline
    x_eval = np.linspace(0, 1, 200)
    y_eval = result(x_eval)

Avec contrainte de convexité
----------------------------

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
.. _quickstart2:

Deuxième exemple - Comparaison avec/sans contrainte
===================================================

Cet exemple compare une spline cubique sans contrainte et une spline cubique avec contrainte de monotonie.

Le code complet
---------------

.. literalinclude:: ../examples/quick_start2.py
   :language: python
   :lines: 3-30
   :caption: examples/quick_start2.py

Explication
-----------

1. **Données** :
   - 30 points sur l'intervalle [0, 1]
   - La fonction cible est :math:`x(1-x)` avec du bruit

2. **Deux ajustements** :
   - **Sans contrainte** : Spline cubique standard (`SplineCubicQuant` sans paramètre de contrainte)
   - **Avec contrainte** : Spline cubique avec `monot=1` (croissante)

3. **Comparaison visuelle** :
   - Points de données en rouge
   - Spline sans contrainte en gris
   - Spline avec contrainte en noir

Résultat
--------

Le graphique montre comment la contrainte de monotonie force la courbe à rester
croissante, contrairement à la spline sans contrainte qui peut présenter des oscillations.

Modification possible
---------------------

Vous pouvez tester d'autres contraintes en modifiant le paramètre `monot` :
- `monot=-1` : décroissante
- `convex=1` : convexe
- `convex=-1` : concave
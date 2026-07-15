.. _quickstart:

Démarrage rapide - Spline cubique croissante
============================================

Ce premier exemple montre comment utiliser une spline cubique avec contrainte de monotonie.

Le code complet
---------------

.. literalinclude:: ../examples/quick_start.py
   :language: python
   :lines: 3-21
   :caption: examples/quick_start.py

Explication
-----------

1. **Importation** : On importe `SplineCubicQuant` pour la régression avec splines cubiques.

2. **Génération des données** :
   - 100 points sur l'intervalle [0, 1]
   - La fonction cible est :math:`3x + 0.2\sin(10\pi x)` avec du bruit

3. **Définition des nœuds** : 11 nœuds placés aux quantiles de x

4. **Ajustement** : Appel à `SplineCubicQuant` avec `monot=1` pour imposer une contrainte de croissance

5. **Visualisation** : Affichage des données et de la courbe ajustée

Résultat
--------

L'exécution produit un graphique montrant les données en rouge et la spline ajustée en noir,
respectant la contrainte de monotonie.

Pour essayer sans contrainte
----------------------------

Décommentez la ligne :
.. code-block:: python

   #result = SplineCubicQuant(x, y, knots, tau=0.5, monot=0)
Exemple avec la fonction logistique
===================================

Cet exemple montre comment appliquer différentes contraintes sur une fonction logistique.

Contraintes testées
-------------------

1. Sans contrainte
2. Croissante
3. Convexité mixte (concave puis convexe)
4. Croissante + convexité mixte
5. Dérivée troisième négative

Utilisation (on peut choisir degree=1..4)
--------------------------------------------

.. code-block:: python

   from BsplineQuantRegpy.examples import run_logistic_example
   run_logistic_example(degree=3)

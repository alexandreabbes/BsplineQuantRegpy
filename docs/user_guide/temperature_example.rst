Exemple avec les données de température
=======================================

Cet exemple analyse les données de température avec différentes contraintes.

Utilisation
-----------

.. code-block:: python

   from BsplineQuantRegpy.examples import run_temperature_analysis
   run_temperature_analysis(degree=3, tau=[0.1, 0.25, 0.5, 0.75, 0.9])

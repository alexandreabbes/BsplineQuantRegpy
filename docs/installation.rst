Installation
============

Prérequis
---------

- Python 3.8 ou supérieur
- Pip (gestionnaire de paquets Python)

Dépendances
-----------

Le packge nécessite les bibliothèques suivantes :

- numpy >= 1.20.0
- scipy >= 1.7.0
- cvxpy >= 1.2.0
- matplotlib >= 3.5.0
- pandas >= 1.3.0
- tkinter (inclus avec Python)

Installation depuis PyPI
------------------------

.. code-block:: bash

    pip install BsplineQuantRegpy

Installation depuis les sources
-------------------------------

.. code-block:: bash

    git clone https://github.com/username/BsplineQuantRegpy.git
    cd BsplineQuantRegpy
    pip install -e .

Installation des dépendances
----------------------------

.. code-block:: bash

    pip install -r requirements.txt

Vérification de l'installation
-------------------------------

.. code-block:: python

    import BsplineQuantRegpy
    print(BsplineQuantRegpy.__version__)

Solveurs SOCP supportés
-----------------------

Le package supporte plusieurs solveurs pour l'optimisation SOCP :

- **CLARABEL** : Solveur par défaut, open-source
- **ECOS** : Solveur open-source, rapide pour les petits problèmes
- **SCS** : Solveur open-source, adapté aux grands problèmes
- **MOSEK** : Solveur commercial, très performant (nécessite une licence)
- **GUROBI** : ne permet pas de gérer les SOCP. Uniquement utilisable pour les splines de degré 1 ou 2.
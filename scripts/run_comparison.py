#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour exécuter la comparaison des degrés indépendamment.
"""

import sys
import os

# Ajouter les chemins
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
EXAMPLES_PATH = os.path.join(PROJECT_ROOT, 'examples')

for path in [SRC_PATH, EXAMPLES_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Importer et exécuter l'exemple
from comparison_example import main

if __name__ == "__main__":
    main()
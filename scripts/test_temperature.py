#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour exécuter le test de température.
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from examples.example_temperature import run_temperature_example

if __name__ == "__main__":
    print("=" * 60)
    print("ANALYSE DES TEMPÉRATURES AVEC SPLINES")
    print("=" * 60)
    run_temperature_example()

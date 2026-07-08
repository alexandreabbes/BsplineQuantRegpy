#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour lancer l'interface graphique.
"""

import sys
import os

# Ajouter le chemin du projet
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# Importer et lancer la GUI
from PysplineQuantReg import run_gui

if __name__ == "__main__":
    print("=" * 60)
    print("SPLINEQUANT - Régression Quantile avec Splines Contraintes")
    print("=" * 60)
    run_gui()

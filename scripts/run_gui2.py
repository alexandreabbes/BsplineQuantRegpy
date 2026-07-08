#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de lancement de l'interface graphique SplineQuant.
"""

import sys
import os

# Ajouter le chemin du projet pour les imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    missing = []
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import cvxpy
    except ImportError:
        missing.append("cvxpy")
    
    try:
        import scipy
    except ImportError:
        missing.append("scipy")
    
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter")
    
    if missing:
        print("⚠️ Dépendances manquantes:")
        for m in missing:
            print(f"  - {m}")
        print("\nInstallez-les avec:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Lance l'interface graphique."""
    print("=" * 60)
    print("SPLINEQUANT - Régression Quantile avec Splines Contraintes")
    print(f"Version: {getattr(sys.modules.get('splinequant'), '__version__', 'dev')}")
    print("=" * 60)
    
    # Vérification des dépendances
    if not check_dependencies():
        return 1
    
    try:
        # Tentative d'import du package
        from splinequant.gui.main_window import main as gui_main
        print("✓ Module splinequant chargé")
        gui_main()
    except ImportError:
        # Fallback sur le fichier direct
        print("ℹ️ Utilisation du fichier direct")
        try:
            sys.path.insert(0, PROJECT_ROOT)
            from Quant_reg_tk import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"❌ Erreur: impossible de charger la GUI: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

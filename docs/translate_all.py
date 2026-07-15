#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script complet pour traduire toute la documentation :
- Docstrings du code Python
- README.md
- Fichiers .po (déjà fait)
"""

import os
import sys
import subprocess
from pathlib import Path

def translate_all():
    """Lance tous les scripts de traduction."""
    print("=" * 70)
    print("🔄 TRADUCTION COMPLÈTE")
    print("=" * 70)
    
    # 1. Traduction des docstrings
    print("\n1. Traduction des docstrings...")
    subprocess.run(["python3", "translate_docstrings.py"])
    
    # 2. Traduction du README
    print("\n2. Traduction du README...")
    subprocess.run(["python3", "translate_readme.py"])
    
    # 3. Traduction des fichiers .po (si nécessaire)
    print("\n3. Traduction des fichiers .po...")
    subprocess.run(["python3", "fill_empty_translations.py"])
    
    # 4. Compilation
    print("\n4. Compilation de la documentation...")
    subprocess.run(["sphinx-intl", "build"])
    subprocess.run(["sphinx-build", "-b", "html", "-D", "language=en", ".", "_build/html/en"])
    
    print("\n" + "=" * 70)
    print("✅ TRADUCTION COMPLÈTE TERMINÉE")
    print("=" * 70)

if __name__ == "__main__":
    # Se placer dans le bon répertoire
    os.chdir(Path(__file__).parent)
    translate_all()

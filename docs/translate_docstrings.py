#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour traduire les docstrings des fonctions Python en utilisant DeepSeek.
"""

import os
import re
import sys
import time
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("❌ Installez requests: pip install requests")
    sys.exit(1)

# ============ CONFIGURATION ============
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Répertoire source
SRC_DIR = Path("../src/BsplineQuantRegpy")
# Fichier de cache pour éviter de retraduire
CACHE_FILE = "docstring_translation_cache.json"

# ============ CACHE ============

def load_cache() -> Dict[str, str]:
    """Charge le cache des docstrings traduites."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: Dict[str, str]):
    """Sauvegarde le cache."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except:
        pass

# ============ FONCTIONS DE TRADUCTION ============

def translate_docstring(text: str, cache: Dict[str, str]) -> str:
    """
    Traduit une docstring avec DeepSeek.
    """
    if not text or not text.strip():
        return text
    
    # Vérifier le cache
    if text in cache:
        return cache[text]
    
    if not DEEPSEEK_API_KEY:
        print("❌ Clé API non configurée")
        return text
    
    # Traduire la docstring
    prompt = f"""Traduis la docstring suivante du français vers l'anglais.
C'est une docstring Python pour un package de régression quantile.
Garde le format (paramètres, returns, examples, etc.) en anglais.

Docstring à traduire:

{text}
"""
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu es un traducteur technique spécialisé en documentation Python."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translated = result['choices'][0]['message']['content']
        
        # Nettoyer la traduction
        # Enlever les guillemets de début/fin si présents
        translated = translated.strip()
        if translated.startswith('"') and translated.endswith('"'):
            translated = translated[1:-1]
        
        # Mettre en cache
        cache[text] = translated
        save_cache(cache)
        
        return translated
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return text

def extract_and_translate_docstrings(file_path: Path, cache: Dict[str, str]) -> bool:
    """
    Extrait et traduit les docstrings d'un fichier Python.
    """
    print(f"\n📝 {file_path.name}")
    
    # Lire le fichier
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erreur de lecture: {e}")
        return False
    
    # Analyser le code source
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"⚠️  Erreur de syntaxe: {e}")
        return False
    
    # Trouver toutes les docstrings
    docstrings = []
    
    # Fonction pour extraire les docstrings des noeuds AST
    def extract_docstrings(node):
        docstring = ast.get_docstring(node)
        if docstring and docstring.strip():
            # Vérifier si la docstring est en français (contient des accents ou mots français)
            french_markers = ['é', 'è', 'ê', 'à', 'ô', 'ç', 'ï', 'ù', 'Régression', 'Quantile', 'Contrainte', 'Spline']
            if any(marker in docstring for marker in french_markers):
                docstrings.append((node, docstring))
    
    # Parcourir l'AST
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            extract_docstrings(node)
    
    if not docstrings:
        print("   Aucune docstring française trouvée")
        return True
    
    print(f"   {len(docstrings)} docstrings à traduire")
    
    # Traduire chaque docstring
    modified = False
    for node, original_docstring in docstrings:
        translated = translate_docstring(original_docstring, cache)
        if translated != original_docstring:
            # Mettre à jour le code
            # Note: Cette approche est simplifiée; pour une solution robuste,
            # il faudrait utiliser un module comme 'astor' pour régénérer le code
            content = content.replace(original_docstring, translated)
            modified = True
            time.sleep(0.5)  # Pause pour l'API
    
    if modified:
        # Écrire le fichier modifié
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ {file_path.name} mis à jour")
        return True
    else:
        print("   Aucune modification nécessaire")
        return True

def process_all_python_files():
    """Traite tous les fichiers Python du projet."""
    print("=" * 70)
    print("🔄 TRADUCTION DES DOCSTRINGS")
    print("=" * 70)
    
    if not DEEPSEEK_API_KEY:
        print("❌ Définissez DEEPSEEK_API_KEY")
        sys.exit(1)
    
    # Charger le cache
    cache = load_cache()
    print(f"📦 Cache: {len(cache)} entrées chargées")
    
    # Trouver tous les fichiers Python
    python_files = list(SRC_DIR.rglob("*.py"))
    print(f"📂 {len(python_files)} fichiers Python trouvés")
    
    for py_file in python_files:
        extract_and_translate_docstrings(py_file, cache)
        time.sleep(1)
    
    save_cache(cache)
    print("\n" + "=" * 70)
    print("✅ TRADUCTION DES DOCSTRINGS TERMINÉE")
    print("=" * 70)

if __name__ == "__main__":
    process_all_python_files()

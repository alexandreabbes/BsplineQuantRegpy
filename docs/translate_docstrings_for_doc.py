#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour traduire les docstrings des fichiers Python en anglais
UNIQUEMENT pour la génération de la documentation Sphinx.
Ne modifie pas les fichiers sources.
"""

import os
import sys
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("❌ Installez requests: pip install requests")
    sys.exit(1)

# ============ CONFIGURATION ============
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'DEEPSEEK_API_KEY = sk-3a3362b9ab1544fbbe75bc7e63da7b1c')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Chemins
SRC_DIR = Path("../src/BsplineQuantRegpy")
OUTPUT_DIR = Path("../docs/_docstrings_en")  # Dossier temporaire
CACHE_FILE = "docstring_en_cache.json"

# ============ CACHE ============

def load_cache() -> Dict[str, str]:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: Dict[str, str]):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except:
        pass

# ============ FONCTIONS ============

def is_french(text: str) -> bool:
    """Détecte si un texte est en français."""
    markers = ['é', 'è', 'ê', 'à', 'ô', 'ç', 'ï', 'ù', 'â', 'î', 'û']
    words = ['Régression', 'Quantile', 'Contrainte', 'Spline', 'Package', 
             'Fonction', 'Paramètres', 'Retourne', 'Exécute']
    
    if any(m in text for m in markers):
        return True
    if any(w in text for w in words):
        return True
    return False

def translate_docstring(text: str, cache: Dict[str, str]) -> str:
    """Traduit une docstring avec DeepSeek."""
    if not text or not text.strip() or not is_french(text):
        return text
    
    # Vérifier le cache
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in cache:
        return cache[cache_key]
    
    if not DEEPSEEK_API_KEY:
        return text
    
    prompt = f"""Traduis la docstring suivante du français vers l'anglais.
C'est une docstring Python pour un package de régression quantile.
Garde le format (paramètres, returns, examples).

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
            {"role": "system", "content": "Tu es un traducteur technique."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        translated = result['choices'][0]['message']['content'].strip()
        cache[cache_key] = translated
        save_cache(cache)
        return translated
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return text

def translate_file(file_path: Path, cache: Dict[str, str], output_dir: Path) -> bool:
    """Traduit les docstrings d'un fichier Python et écrit une copie."""
    print(f"📝 {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si le fichier contient du français
    if not is_french(content):
        return True
    
    # Analyser le code
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"⚠️  Erreur de syntaxe: {e}")
        return False
    
    # Extraire les docstrings
    docstrings = []
    
    def extract(node):
        doc = ast.get_docstring(node)
        if doc and is_french(doc):
            docstrings.append((doc, node.lineno))
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            extract(node)
    
    if not docstrings:
        return True
    
    print(f"   {len(docstrings)} docstrings à traduire")
    
    # Traduire
    translations = {}
    for doc, _ in docstrings:
        translations[doc] = translate_docstring(doc, cache)
    
    # Créer une copie avec les docstrings traduites
    for original, translated in translations.items():
        if translated != original:
            content = content.replace(original, translated, 1)
    
    # Écrire la copie
    output_path = output_dir / file_path.relative_to(SRC_DIR)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔄 PRÉPARATION DES DOCSTRINGS POUR LA DOC ANGLAISE")
    print("=" * 70)
    
    if not DEEPSEEK_API_KEY:
        print("❌ Définissez DEEPSEEK_API_KEY")
        sys.exit(1)
    
    # Créer le dossier de sortie
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    cache = load_cache()
    
    # Traiter tous les fichiers Python
    python_files = list(SRC_DIR.rglob("*.py"))
    print(f"📂 {len(python_files)} fichiers trouvés")
    
    for py_file in python_files:
        translate_file(py_file, cache, OUTPUT_DIR)
    
    save_cache(cache)
    print("✅ Terminé")

if __name__ == "__main__":
    main()

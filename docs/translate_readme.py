#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour traduire le README.md en anglais.
"""

import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ Installez requests: pip install requests")
    sys.exit(1)

# ============ CONFIGURATION ============
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# ============ FONCTIONS ============

def translate_text(text: str) -> str:
    """Traduit un texte avec DeepSeek."""
    if not text.strip():
        return text
    
    prompt = f"""Traduis le texte suivant du français vers l'anglais.
C'est un README.md pour un package Python de régression quantile.
Garde un ton professionnel et technique.

Texte à traduire:

{text}
"""
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu es un traducteur professionnel."},
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
        return translated
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return text

def translate_readme():
    """Traduit le README.md."""
    print("\n📝 Traduction du README.md")
    
    readme_path = Path("../README.md")
    if not readme_path.exists():
        print("❌ README.md non trouvé")
        return
    
    # Lire le README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Séparer le contenu en sections (pour éviter de traduire les blocs de code)
    sections = []
    current_section = ""
    in_code_block = False
    
    for line in content.split('\n'):
        if line.startswith('```'):
            in_code_block = not in_code_block
            current_section += line + '\n'
        elif in_code_block:
            current_section += line + '\n'
        else:
            if line.strip():
                current_section += line + '\n'
            else:
                if current_section:
                    sections.append(current_section)
                    current_section = ""
    
    if current_section:
        sections.append(current_section)
    
    # Traduire chaque section
    translated_sections = []
    for section in sections:
        if section.strip():
            # Vérifier si la section contient du code (ne pas traduire)
            if '```' in section:
                translated_sections.append(section)
            else:
                # Traduire la section
                translated = translate_text(section)
                translated_sections.append(translated)
                time.sleep(0.5)  # Pause pour l'API
    
    # Écrire le README traduit
    output_path = Path("../README.en.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(translated_sections))
    
    print(f"✅ README.en.md créé")

if __name__ == "__main__":
    if not DEEPSEEK_API_KEY:
        print("❌ Définissez DEEPSEEK_API_KEY")
        sys.exit(1)
    
    translate_readme()

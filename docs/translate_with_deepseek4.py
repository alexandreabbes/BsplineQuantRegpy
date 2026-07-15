#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour forcer la traduction de TOUTES les chaînes d'un fichier .po
en utilisant l'API DeepSeek.
"""

import os
import re
import sys
import time
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
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-3a3362b9ab1544fbbe75bc7e63da7b1c')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

LOCALE_DIR = Path("locale")
TARGET_LANG = "en"

# ============ FONCTIONS ============

def extract_all_strings(po_content: str) -> List[Tuple[str, int]]:
    """
    Extrait TOUTES les chaînes à traduire d'un fichier .po.
    
    Returns:
        List of (msgid, line_number_of_msgstr)
    """
    strings = []
    lines = po_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid_match = re.search(r'msgid "(.*)"', line)
            if msgid_match:
                msgid = msgid_match.group(1)
                
                # Ne pas traduire les métadonnées (msgid vide)
                if msgid and msgid != '""':
                    # Chercher le msgstr correspondant
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('msgstr "'):
                        j += 1
                    
                    if j < len(lines):
                        # Récupérer la ligne du msgstr (même si elle est vide)
                        strings.append((msgid, j))
        i += 1
    
    return strings

def translate_batch(texts: List[str]) -> Dict[str, str]:
    """Traduit un lot de textes avec DeepSeek."""
    if not texts:
        return {}
    
    # Construire le prompt
    prompt = f"""Traduis les textes suivants du français vers l'anglais.
Ce sont des extraits de documentation technique sur un package Python.
Garde un ton professionnel.

Textes à traduire:

"""
    for i, text in enumerate(texts, 1):
        prompt += f"{i}. {text}\n"
    
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
        print(f"🔄 Traduction de {len(texts)} textes...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translation_text = result['choices'][0]['message']['content']
        
        # Extraire les traductions
        translations = {}
        lines = translation_text.strip().split('\n')
        current_num = 0
        current_text = ""
        
        for line in lines:
            num_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if num_match:
                num = int(num_match.group(1))
                text = num_match.group(2).strip()
                
                if current_num > 0 and current_text and current_num <= len(texts):
                    translations[texts[current_num - 1]] = current_text
                
                current_num = num
                current_text = text
            elif current_num > 0 and line.strip():
                current_text += " " + line.strip()
        
        if current_num > 0 and current_text and current_num <= len(texts):
            translations[texts[current_num - 1]] = current_text
        
        print(f"✅ {len(translations)} traductions")
        return translations
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {}

def translate_po_file(po_file_path: Path) -> bool:
    """Traduit TOUTES les chaînes d'un fichier .po."""
    print(f"\n📝 {po_file_path.name}")
    
    # Lire le fichier
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire toutes les chaînes
    all_strings = extract_all_strings(content)
    
    if not all_strings:
        print("   Aucune chaîne trouvée")
        return True
    
    print(f"   {len(all_strings)} chaînes à traduire")
    
    # Préparer les textes
    texts_to_translate = [msgid for msgid, _ in all_strings]
    
    # Traduire par lots
    batch_size = 30
    all_translations = {}
    
    for i in range(0, len(texts_to_translate), batch_size):
        batch = texts_to_translate[i:i+batch_size]
        translations = translate_batch(batch)
        all_translations.update(translations)
        time.sleep(0.5)  # Pause pour l'API
    
    # Mettre à jour le fichier
    lines = content.split('\n')
    
    for msgid, line_num in all_strings:
        if msgid in all_translations and all_translations[msgid]:
            new_msgstr = all_translations[msgid].replace('"', '\\"')
            lines[line_num] = f'msgstr "{new_msgstr}"'
        else:
            # Si pas de traduction, utiliser le texte original
            lines[line_num] = f'msgstr "{msgid}"'
    
    # Écrire le fichier
    new_content = '\n'.join(lines)
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✅ {po_file_path.name} mis à jour")
    return True

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔄 TRADUCTION FORCÉE AVEC DEEPSEEK")
    print("=" * 70)
    
    if not DEEPSEEK_API_KEY:
        print("❌ Définissez DEEPSEEK_API_KEY")
        print("   export DEEPSEEK_API_KEY='votre_cle'")
        sys.exit(1)
    
    po_dir = LOCALE_DIR / TARGET_LANG / "LC_MESSAGES"
    
    if not po_dir.exists():
        print(f"❌ {po_dir} n'existe pas")
        print("   Exécutez d'abord: sphinx-intl update -p locale/pot -l en")
        sys.exit(1)
    
    po_files = list(po_dir.glob("*.po"))
    print(f"📂 {len(po_files)} fichiers trouvés")
    
    for po_file in po_files:
        translate_po_file(po_file)
        time.sleep(1)  # Pause entre les fichiers
    
    print("\n" + "=" * 70)
    print("✅ TERMINÉ")
    print("=" * 70)
    print("\n📝 Compilez:")
    print("   sphinx-intl build")
    print("   sphinx-build -b html -D language=en . _build/html/en")

if __name__ == "__main__":
    main()

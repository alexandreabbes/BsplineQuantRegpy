#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour remplir les traductions vides en gérant les msgid sur plusieurs lignes.
"""

import os
import re
import sys
import time
import json
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

def extract_empty_translations(po_content: str) -> List[Tuple[str, int]]:
    """
    Extrait les chaînes avec msgstr vide.
    Gère CORRECTEMENT les msgid sur plusieurs lignes.
    """
    empty = []
    lines = po_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Détecter le début d'un msgid
        if line.startswith('msgid "'):
            # Construire le msgid complet (peut être sur plusieurs lignes)
            msgid_parts = []
            
            # Si le msgid est sur une seule ligne
            if line.endswith('"') and not line.endswith('""'):
                msgid = line.replace('msgid "', '').rstrip('"')
                msgid_parts = [msgid]
                i += 1
            else:
                # msgid sur plusieurs lignes
                # Enlever le 'msgid "' du début
                current_line = line.replace('msgid "', '')
                if current_line.endswith('"'):
                    current_line = current_line.rstrip('"')
                if current_line:
                    msgid_parts.append(current_line)
                i += 1
                
                # Lire les lignes suivantes jusqu'au msgstr
                while i < len(lines) and not lines[i].startswith('msgstr "'):
                    current_line = lines[i].strip()
                    if current_line and current_line != '"':
                        # Enlever les guillemets si présents
                        current_line = current_line.strip('"')
                        if current_line:
                            msgid_parts.append(current_line)
                    i += 1
            
            # Maintenant chercher le msgstr
            # Si on a dépassé le msgstr, on recule
            while i < len(lines) and not lines[i].startswith('msgstr "'):
                i += 1
            
            if i < len(lines):
                msgstr_line = lines[i]
                msgstr_match = re.search(r'msgstr "(.*)"', msgstr_line)
                if msgstr_match:
                    current_msgstr = msgstr_match.group(1)
                    # Si le msgstr est vide, c'est à traduire
                    if not current_msgstr.strip():
                        msgid = ' '.join(msgid_parts).strip()
                        if msgid:
                            empty.append((msgid, i))
        i += 1
    
    return empty

def translate_batch(texts: List[str]) -> Dict[str, str]:
    """Traduit un lot de textes avec DeepSeek."""
    if not texts or not DEEPSEEK_API_KEY:
        return {}
    
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
            {"role": "system", "content": "Tu es un traducteur professionnel spécialisé en documentation technique Python."},
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
        
        print(f"✅ {len(translations)} textes traduits")
        return translations
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return {}

def translate_po_file(po_file_path: Path) -> bool:
    """Traduit les chaînes vides dans un fichier .po."""
    print(f"\n📝 {po_file_path.name}")
    
    # Lire le fichier
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les chaînes vides
    empty_strings = extract_empty_translations(content)
    
    if not empty_strings:
        print("   ✅ Aucune chaîne vide à traduire")
        return True
    
    print(f"   📊 {len(empty_strings)} chaînes vides trouvées")
    
    # Afficher les premières pour vérification
    print("   Premières chaînes à traduire:")
    for msgid, _ in empty_strings[:3]:
        preview = msgid[:60] + "..." if len(msgid) > 60 else msgid
        print(f"      - {preview}")
    
    # Traduire par lots
    texts_to_translate = [msgid for msgid, _ in empty_strings]
    batch_size = 30
    all_translations = {}
    
    for i in range(0, len(texts_to_translate), batch_size):
        batch = texts_to_translate[i:i+batch_size]
        translations = translate_batch(batch)
        all_translations.update(translations)
        time.sleep(0.5)
    
    # Mettre à jour le fichier
    lines = content.split('\n')
    
    for msgid, line_num in empty_strings:
        if msgid in all_translations and all_translations[msgid]:
            new_msgstr = all_translations[msgid].replace('"', '\\"')
            lines[line_num] = f'msgstr "{new_msgstr}"'
    
    # Écrire le fichier
    new_content = '\n'.join(lines)
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✅ {po_file_path.name} mis à jour")
    return True

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔄 TRADUCTION DES CHAÎNES VIDES (MULTI-LIGNES SUPPORTÉES)")
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
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ TERMINÉ")
    print("=" * 70)
    print("\n📝 Compilez: sphinx-intl build")
    print("   sphinx-build -b html -D language=en . _build/html/en")

if __name__ == "__main__":
    main()

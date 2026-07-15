#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour remplir TOUTES les chaînes vides dans les fichiers .po.
Il ne touche pas aux chaînes déjà traduites.
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

def extract_empty_translations(po_content: str) -> List[Tuple[str, int]]:
    """
    Extrait les chaînes qui ont un msgstr vide.
    Gère correctement les msgid sur plusieurs lignes.
    """
    empty = []
    lines = po_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Détecter le début d'un msgid
        if line.startswith('msgid "'):
            # Construire le msgid complet (peut être sur plusieurs lignes)
            msgid = line.replace('msgid "', '').rstrip('"')
            
            # Si le msgid se termine par " mais la ligne continue
            if not line.endswith('"') or '"""' in line:
                i += 1
                while i < len(lines):
                    line = lines[i]
                    if line.startswith('msgstr "'):
                        break
                    if line.strip():
                        msgid += ' ' + line.strip()
                    i += 1
            else:
                i += 1
            
            # Maintenant chercher le msgstr
            while i < len(lines) and not lines[i].startswith('msgstr "'):
                i += 1
            
            if i < len(lines):
                msgstr_line = lines[i]
                msgstr_match = re.search(r'msgstr "(.*)"', msgstr_line)
                if msgstr_match:
                    current_msgstr = msgstr_match.group(1)
                    # Si le msgstr est vide, c'est à traduire
                    if not current_msgstr.strip():
                        # Nettoyer le msgid des guillemets
                        clean_msgid = msgid.replace('"', '').strip()
                        if clean_msgid:
                            empty.append((clean_msgid, i))
        i += 1
    
    return empty

def translate_batch(texts: List[str]) -> Dict[str, str]:
    """Traduit un lot de textes avec DeepSeek."""
    if not texts:
        return {}
    
    if not DEEPSEEK_API_KEY:
        print("❌ Clé API non configurée")
        return {}
    
    prompt = f"""Traduis les textes suivants du français vers l'anglais.
Ce sont des extraits de documentation technique.
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
    
    # Afficher les 5 premières pour vérification
    print("   Premieres chaînes à traduire:")
    for msgid, _ in empty_strings[:5]:
        print(f"      - {msgid[:60]}...")
    
    # Préparer les textes
    texts_to_translate = [msgid for msgid, _ in empty_strings]
    
    # Traduire par lots
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
        else:
            print(f"      ⚠️ Pas de traduction pour: {msgid[:40]}...")
    
    # Écrire le fichier
    new_content = '\n'.join(lines)
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✅ {po_file_path.name} mis à jour")
    return True

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔄 REMPLISSAGE DES TRADUCTIONS VIDES AVEC DEEPSEEK")
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
    print("\n📝 Vérifiez les traductions dans locale/en/LC_MESSAGES/")
    print("   Puis compilez: sphinx-intl build")
    print("   sphinx-build -b html -D language=en . _build/html/en")

if __name__ == "__main__":
    main()

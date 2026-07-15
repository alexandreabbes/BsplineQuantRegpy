#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour compléter les traductions manquantes dans les fichiers .po
en utilisant l'API DeepSeek.
"""

import os
import re
import sys
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import requests
except ImportError:
    print("❌ Le module 'requests' est requis. Installez-le avec: pip install requests")
    sys.exit(1)

# ============ CONFIGURATION ============
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY',  'sk-3a3362b9ab1544fbbe75bc7e63da7b1c')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

LOCALE_DIR = Path("locale")
TARGET_LANG = "en"
CACHE_FILE = "translation_cache.json"

# ============ CACHE ============

def load_cache() -> Dict[str, str]:
    """Charge le cache des traductions."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache: Dict[str, str]):
    """Sauvegarde le cache des traductions."""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except:
        pass

def get_cache_key(text: str) -> str:
    """Génère une clé de cache."""
    clean_text = ' '.join(text.split())
    return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

# ============ FONCTIONS DE TRADUCTION ============

def extract_missing_translations(po_content: str) -> List[Tuple[str, int]]:
    """
    Extrait les chaînes qui n'ont PAS encore été traduites.
    
    Returns:
        List of (msgid, line_number)
    """
    missing = []
    lines = po_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid_match = re.search(r'msgid "(.*)"', line)
            if msgid_match:
                msgid = msgid_match.group(1)
                
                # Ignorer les chaînes vides ou les métadonnées
                if msgid and msgid != '""':
                    # Chercher le msgstr correspondant
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('msgstr "'):
                        j += 1
                    
                    if j < len(lines) and lines[j].startswith('msgstr "'):
                        msgstr_match = re.search(r'msgstr "(.*)"', lines[j])
                        if msgstr_match:
                            current_msgstr = msgstr_match.group(1)
                            # Si msgstr est vide ou égale à msgid, c'est à traduire
                            if not current_msgstr or current_msgstr == msgid:
                                missing.append((msgid, j))
        i += 1
    
    return missing

def translate_batch_with_deepseek(texts: List[str], cache: Dict[str, str]) -> Dict[str, str]:
    """
    Traduit un lot de textes avec l'API DeepSeek.
    """
    if not texts:
        return {}
    
    # Vérifier le cache
    translations = {}
    texts_to_translate = []
    
    for text in texts:
        cache_key = get_cache_key(text)
        if cache_key in cache:
            translations[text] = cache[cache_key]
        else:
            texts_to_translate.append(text)
    
    if not texts_to_translate:
        return translations
    
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'VOTRE_CLE_API_ICI':
        print("❌ Clé API DeepSeek non configurée")
        return translations
    
    # Construire le prompt pour la traduction
    prompt = f"""Traduis les textes suivants du français vers l'anglais.
Ce sont des extraits de documentation technique sur un package Python de régression quantile.
Garde un ton professionnel et technique.

Textes à traduire:

"""
    for i, text in enumerate(texts_to_translate, 1):
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
        print(f"🔄 Traduction de {len(texts_to_translate)} textes...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translation_text = result['choices'][0]['message']['content']
        
        # Extraire les traductions
        lines = translation_text.strip().split('\n')
        current_num = 0
        current_text = ""
        
        for line in lines:
            num_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if num_match:
                num = int(num_match.group(1))
                text = num_match.group(2).strip()
                
                if current_num > 0 and current_text and current_num <= len(texts_to_translate):
                    original = texts_to_translate[current_num - 1]
                    translations[original] = current_text
                    cache[get_cache_key(original)] = current_text
                
                current_num = num
                current_text = text
            elif current_num > 0 and line.strip():
                current_text += " " + line.strip()
        
        if current_num > 0 and current_text and current_num <= len(texts_to_translate):
            original = texts_to_translate[current_num - 1]
            translations[original] = current_text
            cache[get_cache_key(original)] = current_text
        
        print(f"✅ {len(translations)} textes traduits")
        return translations
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return translations

def translate_po_file(po_file_path: Path) -> bool:
    """
    Traduit les chaînes manquantes dans un fichier .po.
    """
    print(f"\n📝 Traduction de {po_file_path.name}")
    
    # Lire le fichier
    try:
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erreur de lecture: {e}")
        return False
    
    # Extraire les chaînes manquantes
    missing = extract_missing_translations(content)
    
    if not missing:
        print("✅ Aucune traduction manquante")
        return True
    
    print(f"📊 {len(missing)} traductions manquantes")
    
    # Charger le cache
    cache = load_cache()
    
    # Préparer les textes à traduire
    texts_to_translate = [msgid for msgid, _ in missing]
    
    # Traduire par lots
    batch_size = 30
    all_translations = {}
    
    for i in range(0, len(texts_to_translate), batch_size):
        batch = texts_to_translate[i:i+batch_size]
        translations = translate_batch_with_deepseek(batch, cache)
        all_translations.update(translations)
        save_cache(cache)
        time.sleep(0.5)
    
    # Mettre à jour le fichier
    lines = content.split('\n')
    
    for msgid, line_num in missing:
        if msgid in all_translations and all_translations[msgid]:
            new_msgstr = all_translations[msgid]
            # Échapper les guillemets
            new_msgstr = new_msgstr.replace('"', '\\"')
            lines[line_num] = f'msgstr "{new_msgstr}"'
    
    # Écrire le fichier
    try:
        new_content = '\n'.join(lines)
        with open(po_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ {po_file_path.name} mis à jour")
        return True
    except Exception as e:
        print(f"❌ Erreur d'écriture: {e}")
        return False

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔧 COMPLÉTION DES TRADUCTIONS MANQUANTES")
    print("=" * 70)
    
    # Vérifier la clé API
    if DEEPSEEK_API_KEY == 'VOTRE_CLE_API_ICI':
        print("⚠️  Clé API DeepSeek non configurée")
        print("   export DEEPSEEK_API_KEY='votre_cle_api'")
        sys.exit(1)
    
    # Trouver les fichiers .po
    po_dir = LOCALE_DIR / TARGET_LANG / "LC_MESSAGES"
    
    if not po_dir.exists():
        print(f"❌ Répertoire {po_dir} non trouvé")
        return
    
    po_files = list(po_dir.glob("*.po"))
    
    if not po_files:
        print("❌ Aucun fichier .po trouvé")
        return
    
    print(f"📂 {len(po_files)} fichiers trouvés")
    
    # Traduire chaque fichier
    for po_file in po_files:
        translate_po_file(po_file)
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("✅ TRADUCTION TERMINÉE")
    print("=" * 70)
    print("\n📝 Compilez maintenant les fichiers avec:")
    print("   sphinx-intl build")
    print("   sphinx-build -b html -D language=en . _build/html/en")

if __name__ == "__main__":
    main()

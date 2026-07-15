#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de traduction automatique de la documentation avec l'API DeepSeek.

Ce script lit les fichiers .po générés par Sphinx, les traduit en anglais
en utilisant l'API DeepSeek, et met à jour les fichiers .po avec les traductions.
"""

import os
import re
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import pour l'appel API
try:
    import requests
except ImportError:
    print("❌ Le module 'requests' est requis. Installez-le avec: pip install requests")
    sys.exit(1)

# ============ CONFIGURATION ============
# Configuration de l'API DeepSeek
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-3a3362b9ab1544fbbe75bc7e63da7b1c')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Configuration des langues
SOURCE_LANG = "fr"      # Langue source (français)
TARGET_LANG = "en"      # Langue cible (anglais)
LOCALE_DIR = Path("locale")

# ============ FONCTIONS ============

def setup_directories():
    """Crée la structure de répertoires nécessaire."""
    # Créer le répertoire pour la langue cible s'il n'existe pas
    target_dir = LOCALE_DIR / TARGET_LANG / "LC_MESSAGES"
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Répertoire cible: {target_dir}")

def extract_translatable_strings(po_content: str) -> List[Tuple[str, str, int]]:
    """
    Extrait les chaînes à traduire d'un fichier .po.
    
    Returns:
        List of (msgid, msgstr, line_number)
    """
    strings = []
    lines = po_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Chercher les msgid
        if line.startswith('msgid "'):
            # Extraire le msgid
            msgid_match = re.search(r'msgid "(.*)"', line)
            if msgid_match:
                msgid = msgid_match.group(1)
                
                # Ignorer les chaînes vides ou les métadonnées
                if msgid and not msgid.startswith('_'):  # Ignorer les messages internes
                    # Chercher le msgstr correspondant
                    i += 1
                    while i < len(lines) and not lines[i].startswith('msgstr "'):
                        i += 1
                    
                    if i < len(lines) and lines[i].startswith('msgstr "'):
                        msgstr_match = re.search(r'msgstr "(.*)"', lines[i])
                        if msgstr_match:
                            # Vérifier si déjà traduit (msgstr non vide et non égale à msgid)
                            current_msgstr = msgstr_match.group(1)
                            if not current_msgstr or current_msgstr == msgid:
                                strings.append((msgid, current_msgstr, i))
        i += 1
    
    return strings

def translate_with_deepseek(texts: List[str], source_lang: str = "fr", target_lang: str = "en") -> Dict[str, str]:
    """
    Traduit une liste de textes avec l'API DeepSeek.
    
    Args:
        texts: Liste des textes à traduire
        source_lang: Langue source
        target_lang: Langue cible
    
    Returns:
        Dictionnaire {texte_source: texte_traduit}
    """
    if not texts:
        return {}
    
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'VOTRE_CLE_API_ICI':
        print("❌ Veuillez configurer votre clé API DeepSeek")
        print("   Soit en modifiant DEEPSEEK_API_KEY dans le script")
        print("   Soit en définissant la variable d'environnement DEEPSEEK_API_KEY")
        return {}
    
    # Construire le prompt
    prompt = f"""Traduis les textes suivants du {source_lang} vers l'anglais.
Pour chaque texte, garde le même sens et un ton professionnel.
Ne traduis pas les termes techniques comme B-spline, quantile, SOCP.

Textes à traduire:

"""
    for i, text in enumerate(texts, 1):
        prompt += f"{i}. {text}\n"
    
    # Appel API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu es un traducteur professionnel spécialisé en documentation technique."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        print(f"🔄 Traduction de {len(texts)} textes avec DeepSeek...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translation_text = result['choices'][0]['message']['content']
        
        # Extraire les traductions du texte de réponse
        translations = {}
        lines = translation_text.strip().split('\n')
        
        current_text = ""
        current_num = 0
        
        for line in lines:
            # Chercher les numéros de ligne (1., 2., etc.)
            num_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if num_match:
                num = int(num_match.group(1))
                text = num_match.group(2).strip()
                
                if current_num > 0 and current_text:
                    # Enregistrer la traduction précédente
                    if current_num <= len(texts):
                        translations[texts[current_num - 1]] = current_text
                
                current_num = num
                current_text = text
            elif current_num > 0:
                # Continuer le texte sur plusieurs lignes
                current_text += " " + line.strip()
        
        # Enregistrer la dernière traduction
        if current_num > 0 and current_text and current_num <= len(texts):
            translations[texts[current_num - 1]] = current_text
        
        print(f"✅ {len(translations)} textes traduits")
        return translations
        
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API: {e}")
        return {}

def translate_file(po_file_path: Path) -> bool:
    """
    Traduit un fichier .po avec l'API DeepSeek.
    
    Returns:
        True si succès, False sinon
    """
    print(f"\n📝 Traduction de {po_file_path.name}")
    
    # Lire le fichier .po
    try:
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erreur de lecture: {e}")
        return False
    
    # Extraire les chaînes à traduire
    strings_to_translate = extract_translatable_strings(content)
    
    if not strings_to_translate:
        print("ℹ️  Aucune chaîne à traduire dans ce fichier")
        return True
    
    # Préparer les textes à traduire
    texts_to_translate = [msgid for msgid, _, _ in strings_to_translate if msgid]
    
    if not texts_to_translate:
        print("ℹ️  Aucun texte valide à traduire")
        return True
    
    print(f"📊 {len(texts_to_translate)} textes à traduire")
    
    # Traduire par lots (DeepSeek peut gérer jusqu'à 4000 tokens)
    batch_size = 20
    all_translations = {}
    
    for i in range(0, len(texts_to_translate), batch_size):
        batch = texts_to_translate[i:i+batch_size]
        translations = translate_with_deepseek(batch)
        all_translations.update(translations)
        
        # Pause pour respecter les limites de l'API
        if i + batch_size < len(texts_to_translate):
            time.sleep(0.5)
    
    # Vérifier les traductions manquantes
    missing = [t for t in texts_to_translate if t not in all_translations]
    if missing:
        print(f"⚠️  {len(missing)} textes non traduits")
        # Pour les textes non traduits, utiliser le texte original
        for text in missing:
            all_translations[text] = text
    
    # Mettre à jour le fichier .po
    lines = content.split('\n')
    for msgid, current_msgstr, line_num in strings_to_translate:
        if msgid in all_translations and all_translations[msgid]:
            new_msgstr = all_translations[msgid]
            # Échapper les guillemets
            new_msgstr = new_msgstr.replace('"', '\\"')
            # Mettre à jour la ligne
            lines[line_num] = f'msgstr "{new_msgstr}"'
    
    # Écrire le fichier mis à jour
    try:
        new_content = '\n'.join(lines)
        with open(po_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Fichier traduit: {po_file_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur d'écriture: {e}")
        return False

def process_all_po_files():
    """Traite tous les fichiers .po pour la langue cible."""
    po_dir = LOCALE_DIR / TARGET_LANG / "LC_MESSAGES"
    
    if not po_dir.exists():
        print(f"❌ Le répertoire {po_dir} n'existe pas")
        print("   Exécutez d'abord: sphinx-intl update -p locale/pot -l en")
        return
    
    po_files = list(po_dir.glob("*.po"))
    if not po_files:
        print(f"❌ Aucun fichier .po trouvé dans {po_dir}")
        return
    
    print(f"📂 {len(po_files)} fichiers .po trouvés")
    
    success_count = 0
    for po_file in po_files:
        if translate_file(po_file):
            success_count += 1
        # Pause pour éviter de dépasser les limites de l'API
        time.sleep(0.5)
    
    print(f"\n✅ {success_count}/{len(po_files)} fichiers traduits avec succès")

    
# Ajouter un cache pour ne pas retraduire les mêmes textes
import hashlib
CACHE_FILE = "translation_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)    
    
def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔄 TRADUCTION AUTOMATIQUE AVEC DEEPSEEK")
    print("=" * 70)
    print(f"Langue source: {SOURCE_LANG}")
    print(f"Langue cible: {TARGET_LANG}")
    print()
    
    # Vérifier la clé API
    if DEEPSEEK_API_KEY == 'VOTRE_CLE_API_ICI':
        print("⚠️  Clé API DeepSeek non configurée")
        print("   Modifiez DEEPSEEK_API_KEY dans le script")
        print("   ou définissez la variable d'environnement:")
        print("   export DEEPSEEK_API_KEY='votre_cle_api'")
        sys.exit(1)
    # Dans translate_with_deepseek, avant l'appel API:
    cache = load_cache()
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in cache:
        return cache[cache_key]

    # Créer la structure de répertoires
    setup_directories()
    
    if len(sys.argv) > 1:
     # Traduire un fichier spécifique
     specific_file = Path(sys.argv[1])
     if specific_file.exists():
        translate_file(specific_file)
     else:
        print(f"❌ Fichier non trouvé: {specific_file}")
    else:
     process_all_po_files()
    # Traduire tous les fichiers
    #process_all_po_files()
    
    print("\n" + "=" * 70)
    print("✅ TRADUCTION TERMINÉE")
    print("=" * 70)
    print("\n📝 Prochaines étapes:")
    print("   1. Vérifier les traductions dans locale/en/LC_MESSAGES/")
    print("   2. Compiler les fichiers .po en .mo:")
    print("      sphinx-intl build")
    print("   3. Générer la documentation en anglais:")
    print("      sphinx-build -b html -D language=en . _build/html/en")

if __name__ == "__main__":
    main()

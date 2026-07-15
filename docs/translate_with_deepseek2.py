#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de traduction automatique de la documentation avec l'API DeepSeek.
Version avec cache pour économiser les tokens.
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
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-3a3362b9ab1544fbbe75bc7e63da7b1c')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

SOURCE_LANG = "fr"
TARGET_LANG = "en"
LOCALE_DIR = Path("locale")

# Cache
CACHE_FILE = "translation_cache.json"
USE_CACHE = True  # Mettre à False pour forcer une nouvelle traduction

# ============ CACHE ============

def load_cache() -> Dict[str, str]:
    """Charge le cache des traductions depuis un fichier JSON."""
    if not USE_CACHE:
        return {}
    
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                print(f"✅ Cache chargé: {len(cache)} entrées")
                return cache
        except Exception as e:
            print(f"⚠️  Erreur de lecture du cache: {e}")
            return {}
    return {}

def save_cache(cache: Dict[str, str]):
    """Sauvegarde le cache des traductions."""
    if not USE_CACHE:
        return
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        print(f"✅ Cache sauvegardé: {len(cache)} entrées")
    except Exception as e:
        print(f"⚠️  Erreur d'écriture du cache: {e}")

def get_cache_key(text: str) -> str:
    """
    Génère une clé de cache pour un texte.
    
    Args:
        text: Le texte original à traduire
        
    Returns:
        Une clé MD5 du texte normalisé
    """
    # Nettoyer le texte (enlever les espaces superflus)
    clean_text = ' '.join(text.split())
    return hashlib.md5(clean_text.encode('utf-8')).hexdigest()

# ============ FONCTIONS DE TRADUCTION ============

def setup_directories():
    """Crée la structure de répertoires nécessaire."""
    target_dir = LOCALE_DIR / TARGET_LANG / "LC_MESSAGES"
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Répertoire cible: {target_dir}")

def extract_translatable_strings(po_content: str) -> List[Tuple[str, int, int]]:
    """
    Extrait les chaînes à traduire d'un fichier .po.
    
    Returns:
        List of (msgid, line_number, next_line_index)
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
                
                # Ignorer les chaînes vides, les métadonnées et les msgid avec _
                if msgid and not msgid.startswith('_') and msgid != '""':
                    # Chercher le msgstr correspondant
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('msgstr "'):
                        j += 1
                    
                    if j < len(lines) and lines[j].startswith('msgstr "'):
                        msgstr_match = re.search(r'msgstr "(.*)"', lines[j])
                        if msgstr_match:
                            current_msgstr = msgstr_match.group(1)
                            # Traduire si msgstr est vide ou égale à msgid
                            if not current_msgstr or current_msgstr == msgid:
                                strings.append((msgid, i, j))
        i += 1
    
    return strings

def translate_with_deepseek(texts: List[str], cache: Dict[str, str]) -> Dict[str, str]:
    """
    Traduit une liste de textes avec l'API DeepSeek.
    Utilise le cache pour éviter les appels redondants.
    
    Args:
        texts: Liste des textes à traduire
        cache: Dictionnaire du cache
    
    Returns:
        Dictionnaire {texte_source: texte_traduit}
    """
    if not texts:
        return {}
    
    # Vérifier le cache
    translations = {}
    texts_to_translate = []
    
    for text in texts:
        cache_key = get_cache_key(text)
        if USE_CACHE and cache_key in cache:
            translations[text] = cache[cache_key]
        else:
            texts_to_translate.append(text)
    
    if not texts_to_translate:
        print(f"✅ Tous les textes sont dans le cache")
        return translations
    
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'VOTRE_CLE_API_ICI':
        print("❌ Veuillez configurer votre clé API DeepSeek")
        return translations
    
    # Construire le prompt
    prompt = f"""Traduis les textes suivants du français vers l'anglais.
Pour chaque texte, garde le même sens et un ton professionnel.
Ne traduis pas les termes techniques comme B-spline, quantile, SOCP, CVXPY.

Textes à traduire:

"""
    for i, text in enumerate(texts_to_translate, 1):
        prompt += f"{i}. {text}\n"
    
    # Appel API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Tu es un traducteur professionnel spécialisé en documentation technique en Python."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        print(f"🔄 Traduction de {len(texts_to_translate)} textes avec DeepSeek...")
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translation_text = result['choices'][0]['message']['content']
        
        # Extraire les traductions du texte de réponse
        lines = translation_text.strip().split('\n')
        
        current_num = 0
        current_text = ""
        
        for line in lines:
            # Chercher les numéros de ligne (1., 2., etc.)
            num_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if num_match:
                num = int(num_match.group(1))
                text = num_match.group(2).strip()
                
                # Enregistrer la traduction précédente
                if current_num > 0 and current_text and current_num <= len(texts_to_translate):
                    original = texts_to_translate[current_num - 1]
                    translations[original] = current_text
                    # Mettre à jour le cache
                    cache_key = get_cache_key(original)
                    cache[cache_key] = current_text
                
                current_num = num
                current_text = text
            elif current_num > 0 and line.strip():
                # Continuer le texte sur plusieurs lignes
                current_text += " " + line.strip()
        
        # Enregistrer la dernière traduction
        if current_num > 0 and current_text and current_num <= len(texts_to_translate):
            original = texts_to_translate[current_num - 1]
            translations[original] = current_text
            cache_key = get_cache_key(original)
            cache[cache_key] = current_text
        
        print(f"✅ {len(translations)} textes traduits (dont {len(texts_to_translate)} nouveaux)")
        return translations
        
    except requests.exceptions.Timeout:
        print("❌ Timeout de l'API DeepSeek")
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    return translations

def translate_file(po_file_path: Path, cache: Dict[str, str]) -> bool:
    """
    Traduit un fichier .po avec l'API DeepSeek.
    
    Args:
        po_file_path: Chemin du fichier .po
        cache: Dictionnaire du cache
    
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
    batch_size = 30
    all_translations = {}
    
    for i in range(0, len(texts_to_translate), batch_size):
        batch = texts_to_translate[i:i+batch_size]
        translations = translate_with_deepseek(batch, cache)
        all_translations.update(translations)
        
        # Sauvegarder le cache après chaque lot
        save_cache(cache)
        
        # Pause pour respecter les limites de l'API
        if i + batch_size < len(texts_to_translate):
            time.sleep(0.5)
    
    # Pour les textes non traduits, garder le texte original
    for text in texts_to_translate:
        if text not in all_translations:
            all_translations[text] = text
    
    # Mettre à jour le fichier .po
    lines = content.split('\n')
    
    # Créer un dictionnaire des msgid -> nouveaux msgstr
    update_lines = {}
    for msgid, line_num, str_line_num in strings_to_translate:
        if msgid in all_translations and all_translations[msgid]:
            new_msgstr = all_translations[msgid]
            # Échapper les guillemets
            new_msgstr = new_msgstr.replace('"', '\\"')
            update_lines[str_line_num] = f'msgstr "{new_msgstr}"'
    
    # Appliquer les mises à jour
    for line_num, new_line in update_lines.items():
        lines[line_num] = new_line
    
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
    
    # Charger le cache
    cache = load_cache()
    
    success_count = 0
    for po_file in po_files:
        if translate_file(po_file, cache):
            success_count += 1
        # Pause entre les fichiers
        time.sleep(1)
    
    # Sauvegarder le cache
    save_cache(cache)
    
    print(f"\n✅ {success_count}/{len(po_files)} fichiers traduits avec succès")

def main():
    """Fonction principale."""
    print("=" * 70)
    print("🔄 TRADUCTION AUTOMATIQUE AVEC DEEPSEEK")
    print("=" * 70)
    print(f"Langue source: {SOURCE_LANG}")
    print(f"Langue cible: {TARGET_LANG}")
    print(f"Cache: {'Activé' if USE_CACHE else 'Désactivé'}")
    print()
    
    # Vérifier la clé API
    if DEEPSEEK_API_KEY == 'VOTRE_CLE_API_ICI':
        print("⚠️  Clé API DeepSeek non configurée")
        print("   Modifiez DEEPSEEK_API_KEY dans le script")
        print("   ou définissez la variable d'environnement:")
        print("   export DEEPSEEK_API_KEY='votre_cle_api'")
        sys.exit(1)
    
    # Créer la structure de répertoires
    setup_directories()
    
    # Traduire tous les fichiers
    process_all_po_files()
    
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

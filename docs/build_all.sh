#!/bin/bash
# build_all.sh - Compile la documentation en français et anglais

set -e

echo "=== 📚 COMPILATION DE LA DOCUMENTATION ==="

# 1. Nettoyer
rm -rf _build/
rm -rf _docstrings_en/

# 2. Générer les docstrings en anglais (si nécessaire)
if [ -n "$DEEPSEEK_API_KEY" ]; then
    echo "📝 Génération des docstrings en anglais..."
    python3 translate_docstrings_for_doc.py
else
    echo "⚠️  DEEPSEEK_API_KEY non définie, docstrings en français uniquement"
fi

# 3. Compiler en français (avec les docstrings françaises)
echo "📚 Compilation en français..."
sphinx-build -b html . _build/html/fr

# 4. Compiler en anglais
echo "📚 Compilation en anglais..."

# Si les docstrings traduites existent, les utiliser
if [ -d "_docstrings_en" ]; then
    echo "   Utilisation des docstrings traduites en anglais"
    # Copier le code source traduit temporairement
    cp -r _docstrings_en/* ../src/BsplineQuantRegpy/
    # Compiler
    sphinx-build -b html -D language=en . _build/html/en
    # Restaurer le code source original
    git checkout ../src/BsplineQuantRegpy/
else
    # Compiler avec les docstrings françaises (pas idéal mais fonctionnel)
    sphinx-build -b html -D language=en . _build/html/en
fi

echo "✅ Documentation générée dans _build/html/"
echo "   🇫🇷 Français: _build/html/fr/index.html"
echo "   🇬🇧 Anglais: _build/html/en/index.html"
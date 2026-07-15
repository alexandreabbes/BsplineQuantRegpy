#!/bin/bash
echo "=== Test de la structure de traduction ==="

# Créer les fichiers .po pour l'anglais
sphinx-intl update -p locale/pot -l en

# Compiler les fichiers .po
sphinx-intl build

# Générer la documentation en anglais
sphinx-build -b html -D language=en . _build/html/en_test

echo "Documentation de test générée dans _build/html/en_test/"


#!/bin/bash
# init_docs.sh - Initialisation complète de la documentation Sphinx

set -e

cd "$(dirname "$0")"

# Nettoyer
rm -rf api/ _build/ conf.py index.rst

# Générer conf.py
cat > conf.py << 'EOF'
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'BsplineQuantRegpy'
copyright = '2026, Alexandre Abbes'
author = 'Alexandre Abbes'
release = '1.0.1'
version = '1.0.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

html_theme = 'sphinx_rtd_theme'

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}
EOF

# Générer les fichiers .rst
sphinx-apidoc -o api/ ../src/BsplineQuantRegpy/ -f -M

# Créer index.rst
cat > index.rst << 'EOF'
BsplineQuantRegpy
=================

Package pour la régression quantile avec B-splines sous contraintes de forme.

.. toctree::
   :maxdepth: 2
   :caption: Contenu:

   api/modules

Indices et tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
EOF

echo "✅ Documentation initialisée"
echo "   Pour construire : sphinx-build -b html . _build/html"
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Ajouter le chemin vers le code source
sys.path.insert(0, os.path.abspath('../src'))

# ============ LANGUES ============
# Langue par défaut
language = 'fr'

# Dossiers des traductions
locale_dirs = ['locale/']
gettext_compact = False  # Pour une structure de dossiers plus propre

# ============ EXTENSIONS ============
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    #'sphinx_intl',  # Pour les traductions
]

# ============ THEME ============
html_theme = 'sphinx_rtd_theme'

# ============ NAPOLEON ============
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# ============ PROJECT INFO ============
project = 'BsplineQuantRegpy'
copyright = f'{datetime.now().year}, Alexandre Abbes'
author = 'Alexandre Abbes'
release = '1.0.1'

# ============ AUTODOC ============
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': False,
    'special-members': '__call__',
    'inherited-members': False,
    'show-inheritance': True,
}

# ============ INTERSPHINX ============
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'cvxpy': ('https://www.cvxpy.org/en/latest', None),
}

# ============ EXCLUSIONS ============
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# ============ HTML OPTIONS ============
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'includehidden': False,
    'titles_only': False,
}

# ============ LANGUES DISPONIBLES ============
# Les langues supportées
languages = {
    'fr': 'Français',
    'en': 'English',
}

# Menu de sélection des langues (pour l'affichage)
html_context = {
    'languages': languages,
    'current_language': language,
}

# ============ MÉTA-DONNÉES ============
# Pour améliorer le référencement
html_meta = {
    'description': 'Quantile Regression with Constrained B-Splines',
    'keywords': 'quantile regression, B-splines, shape constraints, SOCP',
    'author': 'Alexandre Abbes',
}


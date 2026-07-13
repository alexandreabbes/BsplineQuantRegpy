# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# ============ LANGUES ============
language = 'fr'
locale_dirs = ['locale/']
gettext_compact = False

# ============ EXTENSIONS ============
extensions = [
    'sphinx.ext.autodoc',      # Génère la doc à partir des docstrings
    'sphinx.ext.napoleon',     # Support des docstrings Google/NumPy
    'sphinx.ext.viewcode',     # Ajoute des liens vers le code source
    'sphinx.ext.autosummary',  # Génère des résumés automatiques
    'sphinx.ext.intersphinx',  # Liens vers d'autres documentations
    'sphinx.ext.githubpages',  # Pour GitHub Pages
]

# ============ THEME ============
try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except ImportError:
    html_theme = 'alabaster'

# ============ AUTODOC ============
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
}

# ============ NAPOLEON ============
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

# ============ PROJECT INFO ============
project = 'BsplineQuantRegpy'
copyright = '2026, Alexandre Abbes'
author = 'Alexandre Abbes'
release = '1.0.1'

# ============ INTERSPHINX ============
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}

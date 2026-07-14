# -*- coding: utf-8 -*-

import os
import sys

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.abspath('../src'))

# ============ PROJECT INFO ============
project = 'BsplineQuantRegpy'
copyright = '2026, Alexandre Abbes'
author = 'Alexandre Abbes'
release = '1.0.1'
version = '1.0.1'

# ============ EXTENSIONS ============
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

# ============ THEME ============
html_theme = 'sphinx_rtd_theme'

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

# ============ AUTODOC ============
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
}

# ============ INTERSPHINX ============
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
}

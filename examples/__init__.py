#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemples d'utilisation du package PysplineQuantReg.
"""

from .example_temperature import run_temperature_example
from .comparison_example import generate_comparison_data, run_comparison_analysis

__all__ = [
    "run_temperature_example",
    "generate_comparison_data",
    "run_comparison_analysis",
]

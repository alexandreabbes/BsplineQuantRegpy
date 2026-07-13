#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemples pour l'utilisation du package BsplineQuantRegpy.
"""



from .logistic_example import run_logistic_example

def run_basic_example():
    """Lance l'exemple basique."""
    from example_basic import test_all_degrees
    test_all_degrees()


    """Lance l'analyse des données de température."""

from .example_temperature import run_temperature_analysis

from .comparison_example import main as run_comparison_example

__all__ = [
    "run_logistic_example",
    "run_basic_example",
    "run_temperature_analysis",
    "run_comparison_example",
    "quick_start",
    "quick_start2",
]

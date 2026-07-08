#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exemple d'utilisation des splines avec les données de température.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from splinequant import SplineCubicQuantile, quantile_spline


def load_temperature_data(data_path=None):
    """Charge les données de température."""
    if data_path is None:
        # Chercher dans le dossier data
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'temp.xls')
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Fichier non trouvé: {data_path}")
    
    temp = pd.read_excel(data_path)
    return temp


def run_temperature_example():
    """Exécute l'analyse des données de température."""
    
    # Chargement des données
    temp = load_temperature_data()
    temp_val = temp.values
    year = temp_val[:, 0]
    ytab = temp_val[:, 1]
    
    # Normalisation
    xtab = (year - year[0]) / (year[-1] - year[0])
    
    # Nœuds spécifiques pour l'étude des tendances
    year_knots = np.array([1880, 1889, 1900, 1910, 1930, 1940, 1965, 1992])
    knots = (year_knots - 1880) / (1992 - 1880)
    kn = len(knots) - 1
    
    def yr(x):
        return 1880 + x * (1992 - 1880)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    x_eval = np.linspace(0, 1, 200)
    
    # Configuration des axes
    for ax, title in zip(axes, ['Avec contrainte croissante', 'Sans contrainte', 'Contrainte partielle']):
        ax.set_xlabel('Année')
        ax.set_ylabel('Diff. Temp. (°C)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
    
    colors = ['blue', 'red', 'green']
    tau_values = [0.1, 0.5, 0.9]
    
    # Cas 1: Contrainte croissante partout
    for tau, color in zip(tau_values, colors):
        spline_result = SplineCubicQuantile(xtab, ytab, knots, tau, 
                                            monot=1, cv=0, der3=0,
                                            solver='CLARABEL')
        if spline_result is not None:
            y_eval = spline_result(x_eval)
            axes[0].plot(yr(x_eval), y_eval, color=color, linewidth=1, 
                        label=f'τ={tau}')
    
    # Cas 2: Sans contrainte
    for tau, color in zip(tau_values, colors):
        spline_result = SplineCubicQuantile(xtab, ytab, knots, tau, 
                                            monot=0, cv=0, der3=0,
                                            solver='CLARABEL')
        if spline_result is not None:
            y_eval = spline_result(x_eval)
            axes[1].plot(yr(x_eval), y_eval, color=color, linewidth=1,
                        label=f'τ={tau}')
    
    # Cas 3: Contrainte partielle (décroissante sur l'intervalle 1940-1965)
    monot = [0, 0, 0, 0, 0, -1, 0]
    for tau, color in zip(tau_values, colors):
        spline_result = SplineCubicQuantile(xtab, ytab, knots, tau, 
                                            monot=monot, cv=0, der3=0,
                                            solver='CLARABEL')
        if spline_result is not None:
            y_eval = spline_result(x_eval)
            axes[2].plot(yr(x_eval), y_eval, color=color, linewidth=1,
                        label=f'τ={tau}')
    
    # Données
    for ax in axes:
        ax.scatter(yr(xtab), ytab, alpha=0.5, s=20, color='gray', label='Données')
        ax.legend()
    
    plt.tight_layout()
    plt.show()
    
    return temp


if __name__ == "__main__":
    run_temperature_example()
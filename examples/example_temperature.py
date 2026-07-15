#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script d'analyse des données de température avec différentes contraintes et quantiles.
Peut être exécuté indépendamment ou appelé depuis la GUI.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Ajouter le chemin du projet si exécuté indépendamment
#if __name__ == "__main__":
#    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#    SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
#    if SRC_PATH not in sys.path:
#        sys.path.insert(0, SRC_PATH)

from BsplineQuantRegpy import quantile_spline




def load_temperature_data(data_path=None):
    """Charge les données de température."""
    if data_path is None:
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'temp.xls'),
            os.path.join(os.path.dirname(__file__), '..', 'data', 'temp.xls'),
            'temp.xls',
        ]
        for p in possible_paths:
            if os.path.exists(p):
                data_path = p
                break
    
    if data_path is None or not os.path.exists(data_path):
        raise FileNotFoundError(f"Fichier temp.xls non trouvé")
    
    temp = (pd.read_excel(data_path)).values
    
    return temp


def run_temperature_analysis(degree=3, tau = [0.1, 0.25, 0.5, 0.75, 0.9], solver='CLARABEL'):
    """
    Lance une analyse complète des données de température avec différentes contraintes
    pour plusieurs quantiles.
    
    Parameters
    ----------
    degree : int
        Degré de la spline (1, 2, 3, 4)
    tau : list of floats
        Les quantiles à évaluer. 
    solver : str
        Solveur à utiliser
    """
    print("=" * 70)
    print("ANALYSE DES TEMPÉRATURES - RÉGRESSION QUANTILE CONTRAINTE")
    print("=" * 70)
    print(f"Degré: {degree}, Solveur: {solver}")
    print("Quantiles: 0.1, 0.25, 0.5, 0.75, 0.9")
    print("=" * 70)
    
    # Charger les données
    try:
        temp_val = load_temperature_data()
    except FileNotFoundError as e:
        print(f"❌ Erreur: {e}")
        return
    

    year = temp_val[:, 0]
    ytab = temp_val[:, 1]
    
    # Normalisation
    xtab = (year - year[0]) / (year[-1] - year[0])
    
    # Nœuds spécifiques pour l'étude des tendances
    year_knots = np.array([1880, 1889, 1900, 1910, 1930, 1940, 1965, 1992])
    knots = (year_knots - 1880) / (1992 - 1880)
    
    def yr(x):
        return 1880 + x * (1992 - 1880)
    
    # Quantiles à afficher defaut
    quantiles = tau
    
    colors = ['blue', 'cyan', 'green', 'orange', 'red']
    
    # Créer la figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    x_eval = np.linspace(0, 1, 500)
    
    # Vérifier que les modules sont disponibles
    if quantile_spline is None:
        print("❌ Module quantile_spline non disponible")
        return
    
    # ============================================
    # 1. Sans contraintes
    # ============================================
    ax = axes[0, 0]
    ax.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
    ax.set_title('1. Sans contraintes')
    ax.set_xlabel('Année')
    ax.set_ylabel('Δ Température (°C)')
    
    for tau, color in zip(quantiles, colors):
        try:
            res = quantile_spline(xtab, ytab, knots, tau, degree=degree,
                                  monot=0, cv=0, der3=0, solver=solver)
            if res is not None:
                ax.plot(yr(x_eval), res(x_eval), color=color, linewidth=1.5, 
                       label=f'τ={tau}')
        except Exception as e:
            print(f"Erreur sans contrainte τ={tau}: {e}")
    
    ax.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=6, label='Nœuds')
    ax.legend(fontsize='small', ncol=2)
    ax.grid(True, alpha=0.3)
    
    # ============================================
    # 2. Contrainte croissante partout
    # ============================================
    ax = axes[0, 1]
    ax.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
    ax.set_title('2. Contrainte croissante')
    ax.set_xlabel('Année')
    ax.set_ylabel('Δ Température (°C)')
    
    for tau, color in zip(quantiles, colors):
        try:
            res = quantile_spline(xtab, ytab, knots, tau, degree=degree,
                                  monot=1, cv=0, der3=0, solver=solver)
            if res is not None:
                ax.plot(yr(x_eval), res(x_eval), color=color, linewidth=1.5, 
                       label=f'τ={tau}')
        except Exception as e:
            print(f"Erreur croissante τ={tau}: {e}")
    
    ax.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=6, label='Nœuds')
    ax.legend(fontsize='small', ncol=2)
    ax.grid(True, alpha=0.3)
    
    # ============================================
    # 3. Contrainte décroissante (contre-nature)
    # ============================================
    ax = axes[0, 2]
    ax.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
    ax.set_title('3. Contrainte décroissante')
    ax.set_xlabel('Année')
    ax.set_ylabel('Δ Température (°C)')
    
    for tau, color in zip(quantiles, colors):
        try:
            res = quantile_spline(xtab, ytab, knots, tau, degree=degree,
                                  monot=-1, cv=0, der3=0, solver=solver)
            if res is not None:
                ax.plot(yr(x_eval), res(x_eval), color=color, linewidth=1.5, 
                       label=f'τ={tau}')
        except Exception as e:
            print(f"Erreur décroissante τ={tau}: {e}")
    
    ax.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=6, label='Nœuds')
    ax.legend(fontsize='small', ncol=2)
    ax.grid(True, alpha=0.3)
    
    # ============================================
    # 4. Contrainte croissante + convexe
    # ============================================
    ax = axes[1, 0]
    ax.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
    ax.set_title('4. Croissante + Convexe')
    ax.set_xlabel('Année')
    ax.set_ylabel('Δ Température (°C)')
    
    for tau, color in zip(quantiles, colors):
        try:
            res = quantile_spline(xtab, ytab, knots, tau, degree=degree,
                                  monot=1, cv=1, der3=0, solver=solver)
            if res is not None:
                ax.plot(yr(x_eval), res(x_eval), color=color, linewidth=1.5, 
                       label=f'τ={tau}')
        except Exception as e:
            print(f"Erreur croissante+convexe τ={tau}: {e}")
    
    ax.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=6, label='Nœuds')
    ax.legend(fontsize='small', ncol=2)
    ax.grid(True, alpha=0.3)
    
    # ============================================
    # 5. Contrainte partielle (décroissante sur 1940-1965)
    # ============================================
    ax = axes[1, 1]
    ax.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
    ax.set_title('5. Contrainte partielle croissante \n sauf 1940-1965: décroissante)')
    ax.set_xlabel('Année')
    ax.set_ylabel('Δ Température (°C)')
    
    # Contrainte: décroissante sur l'intervalle 1940-1965
    monot_partiel = [1, 1, 1, 1, 1, -1, 1]
    
    # Colorier la zone 1940-1965 (une fois)
    ax.axvspan(1940, 1965, alpha=0.15, color='yellow', label='Zone décroissante')
    
    for tau, color in zip(quantiles, colors):
        try:
            res = quantile_spline(xtab, ytab, knots, tau, degree=degree,
                                  monot=monot_partiel, cv=0, der3=0, solver=solver)
            if res is not None:
                ax.plot(yr(x_eval), res(x_eval), color=color, linewidth=1.5, 
                       label=f'τ={tau}')
        except Exception as e:
            print(f"Erreur partielle τ={tau}: {e}")
    
    ax.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=6, label='Nœuds')
    ax.legend(fontsize='small', ncol=2)
    ax.grid(True, alpha=0.3)
    
    # ============================================
    # 6. Comparaison des contraintes (τ=0.5)
    # ============================================
    ax = axes[1, 2]
    ax.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
    ax.set_title('6. Comparaison des contraintes (τ=0.5)')
    ax.set_xlabel('Année')
    ax.set_ylabel('Δ Température (°C)')
    
    tau_mid = 0.5
    configs = [
        (0, 0, 'blue', 'Sans contrainte'),
        (1, 0, 'green', 'Croissante'),
        (-1, 0, 'red', 'Décroissante'),
        (1, 1, 'magenta', 'C+Convexe'),
        (monot_partiel, 0, 'cyan', 'Partielle'),
    ]
    
    for monot, cv_val, color, label in configs:
        try:
            res = quantile_spline(xtab, ytab, knots, tau_mid, degree=degree,
                                  monot=monot, cv=cv_val, der3=0, solver=solver)
            if res is not None:
                ax.plot(yr(x_eval), res(x_eval), color=color, linewidth=2, label=label)
        except Exception as e:
            print(f"Erreur pour {label}: {e}")
    
    ax.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=6, label='Nœuds')
    ax.legend(fontsize='small')
    ax.grid(True, alpha=0.3)
    
    # Titre général
    fig.suptitle(f'Analyse des températures - Régression quantile (degré {degree})', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "=" * 70)
    print("ANALYSE TERMINÉE")
    print("=" * 70)


def main():
    """Fonction principale pour exécution indépendante."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyse des températures avec splines contraintes')
    parser.add_argument('--degree', type=int, default=3, choices=[1, 2, 3, 4],
                        help='Degré de la spline (1, 2, 3, 4)')
    parser.add_argument('--solver', type=str, default='CLARABEL',
                        help='Solveur à utiliser')
    parser.add_argument('--tau ', type=str, default=[0.1,0.3,0.5,0.7,0.9],
                        help='quantiles à afficher')
    args = parser.parse_args()
    
    run_temperature_analysis(degree=args.degree, solver=args.solver)


if __name__ == "__main__":
    main()

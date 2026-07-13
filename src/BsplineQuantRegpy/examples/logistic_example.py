#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test avec la fonction logistique et différentes contraintes.
Peut être exécuté indépendamment ou appelé depuis la GUI.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
"""
Script de test pour degrés 1
"""


# Ajouter le chemin du projet si exécuté indépendamment
if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
    if SRC_PATH not in sys.path:
        sys.path.insert(0, SRC_PATH)



from BsplineQuantRegpy import (
    SplineLinearQuant,
    SplineQuadraticQuant,
    SplineCubicQuant,
    SplineQuarticQuant,
    quantile_spline
)




def run_logistic_example(show_plots=True, return_data=False,degree=3):
    """
    Exécute le test avec la fonction logistique.
    
    Parameters
    ----------
    show_plots : bool
        Afficher les graphiques
    return_data : bool
        Retourner les données générées
    
    Returns
    -------
    dict or None
        Données si return_data=True
    """
    print("=" * 70)
    print("TEST FONCTION LOGISTIQUE - RÉGRESSION QUANTILE CONTRAINTE")
    print("=" * 70)
    
    np.random.seed(42)
    n_points = 100
    xtab =np.linspace(0, 1, n_points)
    
    # Fonction logistique: f(x) = exp(-5+10x) / (1 + exp(-5+10x))
    ytab = np.exp(-5 + 10*xtab) / (1 + np.exp(-5 + 10*xtab)) + 0.2 * np.random.randn(n_points)
    
    kn = 12
    knots = np.quantile(xtab, np.linspace(0, 1, kn + 1))
    print(f"degré: {degree}")
    print(f"Nombre de points: {n_points}")
    print(f"Nombre de nœuds: {kn}")
    print(f"Point d'inflexion: 0.5")
    
    
    # Quantiles à tester
    quantiles = [0.1, 0.5, 0.9]
    solver = 'CLARABEL'
    
    # Définition des contraintes
    monot_uniform = 1  # Croissante partout
    
    # Convexité: concave puis convexe (point d'inflexion à 0.5)
    cv_mixed = np.zeros(kn + 1)
    for i in range(kn + 1):
        x_pos = knots[i] if i < len(knots) else knots[-1]
        if x_pos < 0.5:
            cv_mixed[i] = 1  # Concave avant 0.5
        else:
            cv_mixed[i] = -1   # Convexe après 0.5
    
    der3 = -1
    
    results = {
        'x': xtab,
        'y': ytab,
        'knots': knots,
        'quantiles': quantiles,
        'results': {}
    }
    
    # Exécuter les régressions pour chaque quantile
    for tau in quantiles:
        results['results'][tau] = {}
        
        # Sans contrainte
        try:
            res = quantile_spline(xtab, ytab, knots, tau, monot=0, cv=0, der3=0, solver=solver,degree=degree)
            results['results'][tau]['none'] = res
            print(f"✓ τ={tau}: Sans contrainte OK")
        except Exception as e:
            print(f"✗ τ={tau}: Sans contrainte {e}")
            results['results'][tau]['none'] = None
        
        # Croissante
        try:
            res = quantile_spline(xtab, ytab, knots, tau, monot=monot_uniform, cv=0, der3=0, solver=solver,degree=degree)
            results['results'][tau]['monot'] = res
            print(f"✓ τ={tau}: Croissante OK")
        except Exception as e:
            print(f"✗ τ={tau}: Croissante {e}")
            results['results'][tau]['monot'] = None
        
        # Convexité mixte
        try:
            res = quantile_spline(xtab, ytab, knots, tau, monot=0, cv=cv_mixed, der3=0, solver=solver,degree=degree)
            results['results'][tau]['cv_mixed'] = res
            print(f"✓ τ={tau}: Convexité mixte OK")
        except Exception as e:
            print(f"✗ τ={tau}: Convexité mixte {e}")
            results['results'][tau]['cv_mixed'] = None
        
        # Croissante + Convexité mixte
        try:
            res = quantile_spline(xtab, ytab, knots, tau, monot=monot_uniform, cv=cv_mixed, der3=0, solver=solver,degree=degree)
            results['results'][tau]['monot_cv'] = res
            print(f"✓ τ={tau}: Croissante+Convexité OK")
        except Exception as e:
            print(f"✗ τ={tau}: Croissante+Convexité {e}")
            results['results'][tau]['monot_cv'] = None
        
        # Contraintes derivee 3e négative
        try:
            res = quantile_spline(xtab, ytab, knots, tau, monot=0, cv=0, der3=der3, solver=solver,degree=degree)
            results['results'][tau]['all'] = res
            print(f"✓ τ={tau}: Contrainte dérivée 3e négative")
        except Exception as e:
            print(f"✗ τ={tau}: Contrainte Dérivée 3e {e}")
            results['results'][tau]['all'] = None
    
    if show_plots:
        # Créer la figure
        fig, axes = plt.subplots(2, 3, figsize=(16, 12))
        x_eval = np.linspace(0, 1, 500)
        colors = ['blue', 'green', 'red']
        
        # 1. Sans contraintes
        ax = axes[0, 0]
        ax.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        for tau, color in zip(quantiles, colors):
            res = results['results'][tau]['none']
            if res is not None:
                ax.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
        ax.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax.set_title('1. Sans contraintes')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.legend(fontsize='small')
        ax.grid(True, alpha=0.3)
        
        # 2. Contrainte croissante
        ax = axes[0, 1]
        ax.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax.set_title('2. Contrainte croissante')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        for tau, color in zip(quantiles, colors):
            res = results['results'][tau]['monot']
            if res is not None:
                ax.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
        ax.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax.legend(fontsize='small')
        ax.grid(True, alpha=0.3)
        
        # 3. Convexité mixte
        ax = axes[0, 2]
        ax.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax.set_title('3. Convexité mixte (concave puis convexe)')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.axvspan(0, 0.5, alpha=0.1, color='red', label='Concave')
        ax.axvspan(0.5, 1, alpha=0.1, color='blue', label='Convexe')
        for tau, color in zip(quantiles, colors):
            res = results['results'][tau]['cv_mixed']
            if res is not None:
                ax.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
        ax.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax.legend(fontsize='small')
        ax.grid(True, alpha=0.3)
        
        # 4. Croissante + Convexité mixte
        ax = axes[1, 0]
        ax.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax.set_title('4. Croissante + Convexité mixte')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.axvspan(0, 0.5, alpha=0.1, color='red')
        ax.axvspan(0.5, 1, alpha=0.1, color='blue')
        for tau, color in zip(quantiles, colors):
            res = results['results'][tau]['monot_cv']
            if res is not None:
                ax.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
        ax.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax.legend(fontsize='small')
        ax.grid(True, alpha=0.3)
        
        # 5. Toutes les contraintes
        ax = axes[1, 1]
        ax.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax.set_title('5. Dérivée 3e négative')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.axvspan(0, 0.5, alpha=0.1, color='red')
        ax.axvspan(0.5, 1, alpha=0.1, color='blue')
        for tau, color in zip(quantiles, colors):
            res = results['results'][tau]['all']
            if res is not None:
                ax.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
        ax.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax.legend(fontsize='small')
        ax.grid(True, alpha=0.3)
        
        # 6. Comparaison des contraintes (τ=0.5)
        ax = axes[1, 2]
        ax.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax.set_title('6. Comparaison des contraintes (τ=0.5)')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        
        configs = [
            ('none', 'blue', 'Sans contrainte'),
            ('monot', 'green', 'Croissante'),
            ('cv_mixed', 'orange', 'Convexité mixte'),
            ('monot_cv', 'purple', 'Croiss.+Cvx mixte'),
            ('all', 'red', 'Dérivée 3e'),
        ]
        
        tau_mid = 0.5
        for key, color, label in configs:
            res = results['results'][tau_mid][key]
            if res is not None:
                ax.plot(x_eval, res(x_eval), color=color, linewidth=2, label=label)
        
        ax.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax.legend(fontsize='small')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    print("\n" + "=" * 70)
    print("TEST TERMINÉ")
    print("=" * 70)
    
    if return_data:
        return results
    else:
        return None


def main():
    """Fonction principale pour exécution indépendante."""
    run_logistic_example(show_plots=True,degree=1)


if __name__ == "__main__":
    main()

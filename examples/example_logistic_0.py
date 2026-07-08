#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de comparaison des différents degrés de splines avec contraintes.
Peut être exécuté indépendamment ou appelé depuis la GUI.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os



# Ajouter le chemin du projet si exécuté indépendamment
if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
    if SRC_PATH not in sys.path:
        sys.path.insert(0, SRC_PATH)

try:
    from PysplineQuantReg import (
        SplineLinearQuant,
        SplineQuadraticQuant,
        SplineCubicQuant,
        SplineQuarticQuant
    )
except ImportError:
    # Fallback pour les imports relatifs
    from ..src.PysplineQuantReg import (
        SplineLinearQuant,
        SplineQuadraticQuant,
        SplineCubicQuant,
        SplineQuarticQuant
    )

def run_logistic_example(self):
    """Lance un test avec la fonction logistique et différentes contraintes pour plusieurs quantiles."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        np.random.seed(42)
        n_points = 200
        xtab = np.linspace(0, 1, n_points)
        
        # Fonction logistique: f(x) = exp(-5+10x) / (1 + exp(-5+10x))
        # Point d'inflexion à x = 0.5
        ytab = np.exp(-5 + 10*xtab) / (1 + np.exp(-5 + 10*xtab)) + 0.05 * np.random.randn(n_points)
        
        kn = 10
        knots = np.quantile(xtab, np.linspace(0, 1, kn + 1))
        
        # Quantiles à tester
        quantiles = [0.1, 0.5, 0.9]
        
        # Définition des contraintes
        # La fonction logistique est croissante partout
        monot_uniform = 1  # Croissante partout
        
        # Convexité: concave puis convexe (point d'inflexion à 0.5)
        # Pour une spline cubique: cv > 0 = convexe, cv < 0 = concave
        cv_mixed = np.zeros(kn + 1)
        for i in range(kn + 1):
            x_pos = knots[i] if i < len(knots) else knots[-1]
            if x_pos < 0.5:
                cv_mixed[i] = -1  # Concave avant 0.5
            else:
                cv_mixed[i] = 1   # Convexe après 0.5
        
        # Dérivée 3: positive (car la dérivée seconde est croissante)
        der3_positive = 1
        
        # Créer la figure
        fig = Figure(figsize=(16, 12), dpi=100)
        x_eval = np.linspace(0, 1, 500)
        solver = 'CLARABEL'
        
        # ============================================
        # 1. Sans contraintes
        # ============================================
        ax1 = fig.add_subplot(2, 3, 1)
        ax1.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        
        for tau, color in zip(quantiles, ['blue', 'green', 'red']):
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau, monot=0, cv=0, der3=0, solver=solver)
                if res is not None:
                    ax1.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
            except Exception as e:
                print(f"Erreur sans contrainte τ={tau}: {e}")
        
        ax1.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax1.set_title('1. Sans contraintes')
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.legend(fontsize='small')
        ax1.grid(True, alpha=0.3)
        
        # ============================================
        # 2. Contrainte de monotonie (croissante)
        # ============================================
        ax2 = fig.add_subplot(2, 3, 2)
        ax2.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax2.set_title('2. Contrainte croissante')
        ax2.set_xlabel('x')
        ax2.set_ylabel('y')
        
        for tau, color in zip(quantiles, ['blue', 'green', 'red']):
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau, monot=monot_uniform, cv=0, der3=0, solver=solver)
                if res is not None:
                    ax2.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
            except Exception as e:
                print(f"Erreur croissante τ={tau}: {e}")
        
        ax2.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax2.legend(fontsize='small')
        ax2.grid(True, alpha=0.3)
        
        # ============================================
        # 3. Contrainte de convexité mixte (concave puis convexe)
        # ============================================
        ax3 = fig.add_subplot(2, 3, 3)
        ax3.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax3.set_title('3. Convexité mixte\n(concave avant 0.5, convexe après)')
        ax3.set_xlabel('x')
        ax3.set_ylabel('y')
        
        # Colorier les zones concave/convexe
        ax3.axvspan(0, 0.5, alpha=0.1, color='red', label='Concave')
        ax3.axvspan(0.5, 1, alpha=0.1, color='blue', label='Convexe')
        
        for tau, color in zip(quantiles, ['blue', 'green', 'red']):
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau, monot=0, cv=cv_mixed, der3=0, solver=solver)
                if res is not None:
                    ax3.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
            except Exception as e:
                print(f"Erreur convexité mixte τ={tau}: {e}")
        
        ax3.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax3.legend(fontsize='small')
        ax3.grid(True, alpha=0.3)
        
        # ============================================
        # 4. Contrainte croissante + convexité mixte
        # ============================================
        ax4 = fig.add_subplot(2, 3, 4)
        ax4.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax4.set_title('4. Croissante + Convexité mixte')
        ax4.set_xlabel('x')
        ax4.set_ylabel('y')
        
        ax4.axvspan(0, 0.5, alpha=0.1, color='red')
        ax4.axvspan(0.5, 1, alpha=0.1, color='blue')
        
        for tau, color in zip(quantiles, ['blue', 'green', 'red']):
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau, monot=monot_uniform, cv=cv_mixed, der3=0, solver=solver)
                if res is not None:
                    ax4.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
            except Exception as e:
                print(f"Erreur croissante+convexe τ={tau}: {e}")
        
        ax4.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax4.legend(fontsize='small')
        ax4.grid(True, alpha=0.3)
        
        # ============================================
        # 5. Toutes les contraintes (croissante + convexité mixte + dérivée 3)
        # ============================================
        ax5 = fig.add_subplot(2, 3, 5)
        ax5.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax5.set_title('5. Toutes les contraintes\n(croissante + convexité mixte + d3 positive)')
        ax5.set_xlabel('x')
        ax5.set_ylabel('y')
        
        ax5.axvspan(0, 0.5, alpha=0.1, color='red')
        ax5.axvspan(0.5, 1, alpha=0.1, color='blue')
        
        for tau, color in zip(quantiles, ['blue', 'green', 'red']):
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau, 
                                      monot=monot_uniform, cv=cv_mixed, der3=der3_positive, solver=solver)
                if res is not None:
                    ax5.plot(x_eval, res(x_eval), color=color, linewidth=2, label=f'τ={tau}')
            except Exception as e:
                print(f"Erreur toutes contraintes τ={tau}: {e}")
        
        ax5.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax5.legend(fontsize='small')
        ax5.grid(True, alpha=0.3)
        
        # ============================================
        # 6. Comparaison des contraintes (τ=0.5)
        # ============================================
        ax6 = fig.add_subplot(2, 3, 6)
        ax6.scatter(xtab, ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax6.set_title('6. Comparaison des contraintes (τ=0.5)')
        ax6.set_xlabel('x')
        ax6.set_ylabel('y')
        
        tau_mid = 0.5
        configs = [
            (0, 0, 0, 'blue', 'Sans contrainte'),
            (monot_uniform, 0, 0, 'green', 'Croissante'),
            (0, cv_mixed, 0, 'orange', 'Convexité mixte'),
            (monot_uniform, cv_mixed, 0, 'purple', 'Croiss.+Cvx mixte'),
            (monot_uniform, cv_mixed, der3_positive, 'red', 'Toutes contraintes'),
        ]
        
        for monot, cv, der3, color, label in configs:
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau_mid, monot=monot, cv=cv, der3=der3, solver=solver)
                if res is not None:
                    ax6.plot(x_eval, res(x_eval), color=color, linewidth=2, label=label)
            except Exception as e:
                print(f"Erreur {label}: {e}")
        
        ax6.plot(knots, np.ones_like(knots)*max(ytab)*0.95, 'k|', markersize=8, label='Nœuds')
        ax6.legend(fontsize='small')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Créer une fenêtre Tkinter pour la figure
        fig_window = tk.Toplevel(self.root)
        fig_window.title("Test fonction logistique - Régression quantile contrainte")
        fig_window.geometry("1400x1000")
        
        canvas = FigureCanvasTkAgg(fig, master=fig_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2Tk(canvas, fig_window)
        toolbar.update()
        
        btn_frame = ttk.Frame(fig_window)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Fermer", command=fig_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bouton pour charger les données dans la GUI
        def load_data_to_gui():
            self.xtab = xtab
            self.ytab = ytab
            self.knots = knots
            self.clear_all()
            self.plot_data()
            self.plot_knots()
            self.ax.set_title('Fonction logistique - Données')
            self.data_info.set(f"{len(xtab)} points (logistique)")
            self.status_var.set("Données logistique chargées")
            self.canvas.draw()
            fig_window.destroy()
        
        ttk.Button(btn_frame, text="Charger ces données dans la GUI", 
                  command=load_data_to_gui).pack(side=tk.LEFT, padx=5)
        
        self.status_var.set("Test logistique terminé")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
def main():
    """Fonction principale pour exécution indépendante."""
    print("=" * 70)
    print("Exemple de Regression Quantile avec une fonction logistique bruitée ")
    print("=" * 70)
    
   
    # Exécuter l'analyse
    run_logistic_example()
    
    print("\n" + "=" * 70)
    print("FIN DE LA COMPARAISON")
    print("=" * 70)
    
if __name__ == "__main__":
    main()

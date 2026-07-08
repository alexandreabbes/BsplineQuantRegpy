#!/usr/bin/env python

__author__ = "Alexandre Abbes"
__copyright__ = "Copyright 2026, Alexandre Adel Abbes"
__credits__ = ["Alexandre Abbes"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Alexandre Abbes"
__email__ = "alexandre.abbes@proton.me"


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import warnings
warnings.filterwarnings('ignore')

import sys
import os

# Ajouter les chemins
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
EXAMPLES_PATH = os.path.join(PROJECT_ROOT, 'examples')

for path in [PROJECT_ROOT, SRC_PATH, EXAMPLES_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Imports
try:
    from PysplineQuantReg import (
        SplineLinearQuantile,
        SplineQuadraticQuantile,
        SplineCubicQuantile,
        SplineQuarticQuantile
    )
    print("✓ Tous les modules spline chargés")
except ImportError as e:
    print(f"✗ Erreur chargement: {e}")
    SplineLinearQuantile = None
    SplineQuadraticQuantile = None
    SplineCubicQuantile = None
    SplineQuarticQuantile = None


class QuantileSplineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Régression Quantile avec Splines Contraintes")
        self.root.geometry("1400x800")
        
        # Données
        self.xtab = None
        self.ytab = None
        self.knots = None
        self.manual_knots_mode = False
        self.temp_knots = []
        self.knot_lines = []
        self.spline_result = None
        self.degree = 3
        self.constraints_mode = "uniform"
        self.regions = []
        self.region_patches = []
        self.temperature_years = None  # Pour les données température
        
        # Solveurs disponibles
        self.solvers = [
            'CLARABEL',
            'ECOS',
            'SCS',
            'CVXOPT',
            'GUROBI',
            'MOSEK'
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration des poids
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)
        
        # ============ MENU ============
        self.setup_menu()
        
        # ============ NOTEBOOK avec onglets ============
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # ... RESTE DU CODE IDENTIQUE ...
        # (Continuer avec les onglets comme avant)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # ============ Onglet 1: Données et paramètres spline ============
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="1. Données & Spline")
        
        # ... etc ... (le reste du code est identique)
        # Je ne réécris pas tout pour éviter la duplication
        
        # Continuer avec le code existant...
        # ... (toute la suite de setup_ui)
        
    def setup_menu(self):
        """Configure le menu de l'application."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Charger CSV", command=self.load_csv)
        file_menu.add_command(label="Charger Excel", command=self.load_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Exemples
        examples_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exemples", menu=examples_menu)
        examples_menu.add_command(label="Données de test (sinus)", command=self.generate_test_data)
        examples_menu.add_command(label="Données de test personnalisées", command=self.show_custom_test_dialog)
        examples_menu.add_separator()
        examples_menu.add_command(label="📊 Données température", command=self.load_temperature_example)
        examples_menu.add_command(label="📈 Comparaison des degrés", command=self.run_comparison_example)
    
    def show_custom_test_dialog(self):
        """Affiche un dialogue pour générer des données de test personnalisées."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Données de test personnalisées")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Fonction f(x):").grid(row=0, column=0, padx=5, pady=5)
        func_entry = ttk.Entry(dialog, width=40)
        func_entry.grid(row=0, column=1, padx=5, pady=5)
        func_entry.insert(0, "2*x + 0.2*sin(10*pi*x)")
        
        ttk.Label(dialog, text="Bruit:").grid(row=1, column=0, padx=5, pady=5)
        noise_entry = ttk.Entry(dialog, width=20)
        noise_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        noise_entry.insert(0, "0.05")
        
        ttk.Label(dialog, text="Nombre de points:").grid(row=2, column=0, padx=5, pady=5)
        npoints_entry = ttk.Entry(dialog, width=20)
        npoints_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        npoints_entry.insert(0, "200")
        
        def generate():
            try:
                func_str = func_entry.get()
                noise = float(noise_entry.get())
                n = int(npoints_entry.get())
                
                x = np.linspace(0, 1, n)
                
                # Évaluer la fonction
                func_str = func_str.replace('sin', 'np.sin')
                func_str = func_str.replace('cos', 'np.cos')
                func_str = func_str.replace('exp', 'np.exp')
                func_str = func_str.replace('pi', 'np.pi')
                
                y = eval(func_str) + noise * np.random.randn(n)
                
                self.xtab = x
                self.ytab = y
                self.clear_all()
                self.plot_data()
                self.data_info.set(f"{n} points (test personnalisé)")
                self.status_var.set("Données test générées")
                
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur dans la fonction: {str(e)}")
        
        ttk.Button(dialog, text="Générer", command=generate).grid(row=3, column=0, columnspan=2, pady=20)
    
    def run_comparison_example(self):
        """Lance un exemple comparant les différents degrés."""
        try:
            np.random.seed(42)
            n = 200
            x = np.linspace(0, 1, n)
            y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.05*np.random.randn(n)
            knots = np.quantile(x, np.linspace(0, 1, 11))
            
            self.xtab = x
            self.ytab = y
            self.knots = knots
            self.clear_all()
            self.plot_data()
            self.plot_knots()
            self.data_info.set(f"{n} points (exemple comparaison)")
            self.status_var.set("Données chargées pour comparaison des degrés")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def load_temperature_example(self):
        """Charge l'exemple des données de température."""
        try:
            import os
            
            # Chercher le fichier temp.xls
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'examples', 'temp.xls'),
                os.path.join(os.path.dirname(__file__), '..', '..', 'examples', 'temp.xls'),
                os.path.join(os.path.dirname(__file__), '..', 'examples', 'temp.xls'),
                'examples/temp.xls',
                'temp.xls',
            ]
            
            file_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    file_path = p
                    break
            
            if file_path is None:
                file_path = filedialog.askopenfilename(
                    title="Sélectionner le fichier temp.xls",
                    filetypes=[("Excel files", "*.xls *.xlsx")]
                )
                if not file_path:
                    return
            
            # Charger les données
            temp = pd.read_excel(file_path)
            temp_val = temp.values
            year = temp_val[:, 0]
            ytab = temp_val[:, 1]
            
            # Normalisation
            xtab = (year - year[0]) / (year[-1] - year[0])
            
            # Nœuds spécifiques
            year_knots = np.array([1880, 1889, 1900, 1910, 1930, 1940, 1965, 1992])
            knots = (year_knots - 1880) / (1992 - 1880)
            
            self.xtab = xtab
            self.ytab = ytab
            self.knots = knots
            self.temperature_years = year
            
            self.clear_all()
            self.plot_data()
            self.plot_knots()
            
            self.ax.set_title('Températures globales (1880-1992)')
            self.data_info.set(f"{len(xtab)} points (température)")
            self.status_var.set("Données température chargées avec nœuds spécifiques")
            self.canvas.draw()
            
            messagebox.showinfo("Succès", 
                "Données de température chargées!\n\n"
                "Nœuds aux années: 1880, 1889, 1900, 1910, 1930, 1940, 1965, 1992")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'exemple: {str(e)}")
    
    def process_dataframe(self, df):
        """Traite le DataFrame (CORRIGÉ)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            messagebox.showerror("Erreur", "Besoin de 2 colonnes numériques")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Sélection colonnes")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Colonne X:").grid(row=0, column=0, padx=5, pady=5)
        x_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(dialog, textvariable=x_var, values=numeric_cols, 
                    state="readonly").grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Colonne Y:").grid(row=1, column=0, padx=5, pady=5)
        y_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
        ttk.Combobox(dialog, textvariable=y_var, values=numeric_cols,
                    state="readonly").grid(row=1, column=1, padx=5, pady=5)
        
        # CORRECTION : confirm() est une fermeture qui capture les variables
        def confirm():
            try:
                self.xtab = df[x_var.get()].values.astype(float)
                self.ytab = df[y_var.get()].values.astype(float)
                
                x_min, x_max = self.xtab.min(), self.xtab.max()
                if x_min != x_max:
                    self.xtab = (self.xtab - x_min) / (x_max - x_min)
                
                dialog.destroy()
                self.clear_all()
                self.plot_data()
                self.data_info.set(f"{len(self.xtab)} points")
                self.status_var.set("Données chargées")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        
        ttk.Button(dialog, text="Confirmer", command=confirm).grid(row=2, column=0, columnspan=2, pady=20)
    
    # Le reste des méthodes (load_csv, load_excel, generate_test_data, etc.) 
    # reste inchangé

def main():
    root = tk.Tk()
    app = QuantileSplineApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

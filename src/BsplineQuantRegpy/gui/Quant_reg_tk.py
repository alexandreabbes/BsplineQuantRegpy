#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import sys
import os

warnings.filterwarnings('ignore')


# ============ CONFIGURATION DES CHEMINS ============
def get_project_paths():
    """Retourne les chemins du projet de manière robuste."""
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    
    # Remonter jusqu'à la racine du projet (3 niveaux)
    project_root = current_dir
    for _ in range(3):
        project_root = os.path.dirname(project_root)
    
    # Vérifier avec un fichier signature
    signature_files = ['pyproject.toml', 'setup.py', 'README.md']
    found = False
    for sig in signature_files:
        if os.path.exists(os.path.join(project_root, sig)):
            found = True
            break
    
    if not found:
        alt_root = os.path.dirname(os.path.dirname(current_dir))
        for sig in signature_files:
            if os.path.exists(os.path.join(alt_root, sig)):
                project_root = alt_root
                found = True
                break
    
    src_path = os.path.join(project_root, 'src')
    examples_path = os.path.join(project_root, 'examples')
    scripts_path = os.path.join(project_root, 'scripts')
    data_path = os.path.join(project_root, 'data')
    
    paths_to_add = [project_root, src_path, examples_path, scripts_path]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return project_root, src_path, examples_path, scripts_path, data_path


# Initialiser les chemins
PROJECT_ROOT, SRC_PATH, EXAMPLES_PATH, SCRIPTS_PATH, DATA_PATH = get_project_paths()

print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"EXAMPLES_PATH: {EXAMPLES_PATH}")


# ============ IMPORTS ============
try:
    from BsplineQuantRegpy import (
        SplineLinearQuant,
        SplineQuadraticQuant,
        SplineCubicQuant,
        SplineQuarticQuant
    )
    print("✓ Module spline chargé")
except ImportError as e:
    print(f"✗ Erreur chargement: {e}")
    SplineLinearQuant = None
    SplineQuadraticQuant = None
    SplineCubicQuant = None
    SplineQuarticQuant = None


# ============ CLASSE PRINCIPALE ============
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
        self.temperature_years = None
        
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
    def quit_app(self):
     """Quitte l'application proprement."""
     if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
        self.root.quit()
        self.root.destroy()
        
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

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Onglets
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="1. Données & Spline")

        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="2. Contraintes")

        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="3. Exécution & Export")

        # ============================================================
        # ONGLET 1: DONNÉES & SPLINE
        # ============================================================

        # Section Import des données
        import_frame = ttk.LabelFrame(tab1, text="1. Import des données", padding="10")
        import_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        ttk.Button(import_frame, text="Charger CSV", command=self.load_csv).grid(row=0, column=0, padx=2)
        ttk.Button(import_frame, text="Charger Excel", command=self.load_excel).grid(row=0, column=1, padx=2)
        ttk.Button(import_frame, text="Données test", command=self.generate_test_data).grid(row=0, column=2, padx=2)

        self.data_info = tk.StringVar(value="Aucune donnée")
        ttk.Label(import_frame, textvariable=self.data_info).grid(row=1, column=0, columnspan=3, pady=5)

        # Fonction test personnalisée
        test_frame = ttk.Frame(import_frame)
        test_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        ttk.Label(test_frame, text="Fonction test (x):").grid(row=0, column=0, sticky=tk.W)
        self.test_function_var = tk.StringVar(value="2*x + 0.2*sin(10*pi*x) + 0.2*randn(n)")
        test_entry = ttk.Entry(test_frame, textvariable=self.test_function_var, width=40)
        test_entry.grid(row=1, column=0, padx=2, pady=2, sticky=(tk.W, tk.E))

        ttk.Button(test_frame, text="Générer test", command=self.generate_custom_test).grid(row=1, column=1, padx=2)

        ttk.Label(test_frame, text="Nb points:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.test_npoints_var = tk.IntVar(value=200)
        test_npoints_spin = ttk.Spinbox(test_frame, from_=10, to=1000, textvariable=self.test_npoints_var, width=8)
        test_npoints_spin.grid(row=2, column=1, sticky=tk.W, pady=2)

        # Section Paramètres spline
        spline_frame = ttk.LabelFrame(tab1, text="2. Paramètres spline", padding="10")
        spline_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Degré
        ttk.Label(spline_frame, text="Degré:").grid(row=0, column=0, sticky=tk.W)
        self.degree_var = tk.IntVar(value=3)
        ttk.Radiobutton(spline_frame, text="1 (Linéaire)", variable=self.degree_var, value=1, command=self.update_degree).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(spline_frame, text="2 (Quadratique)", variable=self.degree_var, value=2, command=self.update_degree).grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(spline_frame, text="3 (Cubique)", variable=self.degree_var, value=3, command=self.update_degree).grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(spline_frame, text="4 (Quartique)", variable=self.degree_var, value=4, command=self.update_degree).grid(row=1, column=2, sticky=tk.W)

        # Mode nœuds
        ttk.Label(spline_frame, text="Nœuds:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.knot_mode = tk.StringVar(value="auto")
        ttk.Radiobutton(spline_frame, text="Auto (quantiles)", variable=self.knot_mode, value="auto", command=self.knot_mode_changed).grid(row=2, column=1, columnspan=2, sticky=tk.W)
        ttk.Radiobutton(spline_frame, text="Manuel (clics)", variable=self.knot_mode, value="manual", command=self.knot_mode_changed).grid(row=3, column=1, columnspan=2, sticky=tk.W)

        ttk.Label(spline_frame, text="Nombre:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.knot_count = tk.IntVar(value=11)
        self.knot_spinbox = ttk.Spinbox(spline_frame, from_=4, to=30, textvariable=self.knot_count, width=5)
        self.knot_spinbox.grid(row=4, column=1, sticky=tk.W)

        # Boutons nœuds
        knot_btn_frame = ttk.Frame(spline_frame)
        knot_btn_frame.grid(row=5, column=0, columnspan=3, pady=5)

        self.define_knots_btn = ttk.Button(knot_btn_frame, text="Définir nœuds", command=self.define_knots)
        self.define_knots_btn.pack(side=tk.LEFT, padx=2)

        self.validate_knots_btn = ttk.Button(knot_btn_frame, text="Valider nœuds", command=self.validate_manual_knots)
        self.validate_knots_btn.pack(side=tk.LEFT, padx=2)
        self.validate_knots_btn.config(state='disabled')

        ttk.Button(knot_btn_frame, text="Effacer nœuds", command=self.clear_knots).pack(side=tk.LEFT, padx=2)

        # Section Ajustement des axes (dans l'onglet 1)
        axes_frame = ttk.LabelFrame(tab1, text="3. Ajustement des axes", padding="10")
        axes_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        # X min/max
        ttk.Label(axes_frame, text="X min:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.xmin_var = tk.DoubleVar(value=0.0)
        xmin_entry = ttk.Entry(axes_frame, textvariable=self.xmin_var, width=10)
        xmin_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(axes_frame, text="X max:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.xmax_var = tk.DoubleVar(value=1.0)
        xmax_entry = ttk.Entry(axes_frame, textvariable=self.xmax_var, width=10)
        xmax_entry.grid(row=0, column=3, padx=5, pady=5)

        btn_axes_frame = ttk.Frame(axes_frame)
        btn_axes_frame.grid(row=1, column=0, columnspan=4, pady=5)

        ttk.Button(btn_axes_frame, text="Appliquer", command=self.apply_axes_limits).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_axes_frame, text="Auto", command=self.adjust_axes).pack(side=tk.LEFT, padx=5)

        # ============================================================
        # ONGLET 2: CONTRAINTES
        # ============================================================

        constraint_frame = ttk.LabelFrame(tab2, text="Contraintes de forme", padding="10")
        constraint_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=5, padx=5)

        self.constraint_mode_var = tk.StringVar(value="uniform")
        ttk.Radiobutton(constraint_frame, text="Uniformes", variable=self.constraint_mode_var, 
                       value="uniform", command=self.toggle_constraint_mode).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(constraint_frame, text="Par région", variable=self.constraint_mode_var, 
                       value="region", command=self.toggle_constraint_mode).grid(row=0, column=1, sticky=tk.W)

        self.uniform_frame = ttk.Frame(constraint_frame)
        self.uniform_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Monotonie
        ttk.Label(self.uniform_frame, text="Monotonie:").grid(row=0, column=0, sticky=tk.W)
        self.monot_var = tk.IntVar(value=0)
        ttk.Radiobutton(self.uniform_frame, text="↗", variable=self.monot_var, value=1).grid(row=0, column=1)
        ttk.Radiobutton(self.uniform_frame, text="↘", variable=self.monot_var, value=-1).grid(row=0, column=2)
        ttk.Radiobutton(self.uniform_frame, text="✗", variable=self.monot_var, value=0).grid(row=0, column=3)

        # Convexité
        self.convex_frame = ttk.Frame(self.uniform_frame)
        self.convex_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(self.convex_frame, text="Convexité:").grid(row=0, column=0, sticky=tk.W)
        self.convex_var = tk.IntVar(value=0)
        ttk.Radiobutton(self.convex_frame, text="∪", variable=self.convex_var, value=1).grid(row=0, column=1)
        ttk.Radiobutton(self.convex_frame, text="∩", variable=self.convex_var, value=-1).grid(row=0, column=2)
        ttk.Radiobutton(self.convex_frame, text="✗", variable=self.convex_var, value=0).grid(row=0, column=3)

        # Dérivée 3
        self.der3_frame = ttk.Frame(self.uniform_frame)
        self.der3_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(self.der3_frame, text="Dérivée 3e:").grid(row=0, column=0, sticky=tk.W)
        self.der3_var = tk.IntVar(value=0)
        ttk.Radiobutton(self.der3_frame, text="+", variable=self.der3_var, value=1).grid(row=0, column=1)
        ttk.Radiobutton(self.der3_frame, text="-", variable=self.der3_var, value=-1).grid(row=0, column=2)
        ttk.Radiobutton(self.der3_frame, text="✗", variable=self.der3_var, value=0).grid(row=0, column=3)

        # Régions
        self.region_frame = ttk.Frame(constraint_frame)
        self.region_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.region_frame.grid_remove()

        ttk.Button(self.region_frame, text="Ajouter région", command=self.start_region_selection).pack(pady=2)
        ttk.Button(self.region_frame, text="Effacer régions", command=self.clear_regions).pack(pady=2)
        self.region_listbox = tk.Listbox(self.region_frame, height=4, width=35)
        self.region_listbox.pack(pady=5, fill=tk.X)

        # ============================================================
        # ONGLET 3: EXÉCUTION & EXPORT
        # ============================================================

        # Section Solveur
        solver_frame = ttk.LabelFrame(tab3, text="Solveur", padding="10")
        solver_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        ttk.Label(solver_frame, text="Solveur CVXPY:").grid(row=0, column=0, sticky=tk.W)
        self.solver_var = tk.StringVar(value='CLARABEL')
        solver_combo = ttk.Combobox(solver_frame, textvariable=self.solver_var, 
                                   values=self.solvers, state='readonly', width=15)
        solver_combo.grid(row=0, column=1, padx=5, pady=5)

        # Section Exécution
        exec_frame = ttk.LabelFrame(tab3, text="Exécution", padding="10")
        exec_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Tau
        ttk.Label(exec_frame, text="τ:").grid(row=0, column=0)
        self.tau_var = tk.DoubleVar(value=0.5)
        tau_scale = ttk.Scale(exec_frame, from_=0.01, to=0.99, variable=self.tau_var,
                            orient=tk.HORIZONTAL, length=150)
        tau_scale.grid(row=0, column=1, padx=5)
        self.tau_label = ttk.Label(exec_frame, text="0.50")
        self.tau_label.grid(row=0, column=2)
        tau_scale.configure(command=lambda x: self.tau_label.configure(text=f"{float(x):.2f}"))

        # Boutons d'exécution
        btn_frame = ttk.Frame(exec_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="▶ Lancer", command=self.run_regression).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Effacer tout", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        # Barre de progression
        self.progress = ttk.Progressbar(tab3, mode='indeterminate')
        self.progress.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10, padx=5)

        # Statut
        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(tab3, textvariable=self.status_var, foreground="blue").grid(row=3, column=0, pady=5, padx=5)

        # Section Gestion des courbes
        curve_frame = ttk.LabelFrame(tab3, text="Gestion des courbes", padding="10")
        curve_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        color_frame = ttk.Frame(curve_frame)
        color_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Label(color_frame, text="Couleur:").grid(row=0, column=0, padx=2)
        self.color_var = tk.StringVar(value='blue')
        colors = ['blue', 'red', 'black', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        color_combo = ttk.Combobox(color_frame, textvariable=self.color_var, 
                          values=colors, state='readonly', width=10)
        color_combo.grid(row=0, column=1, padx=2)
        ttk.Button(color_frame, text="Appliquer", command=self.apply_color).grid(row=0, column=2, padx=5)

        curve_btn_frame = ttk.Frame(curve_frame)
        curve_btn_frame.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(curve_btn_frame, text="Effacer dernière courbe", command=self.clear_last_curve).pack(side=tk.LEFT, padx=2)
        ttk.Button(curve_btn_frame, text="Effacer toutes les courbes", command=self.clear_all_curves).pack(side=tk.LEFT, padx=2)

        self.curve_count = 0
        self.curve_lines = []
        self.curve_count_var = tk.StringVar(value="Courbes: 0")
        ttk.Label(curve_frame, textvariable=self.curve_count_var).grid(row=2, column=0, columnspan=2, pady=5)

        # Section Export
        export_frame = ttk.LabelFrame(tab3, text="Export", padding="10")
        export_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        export_btn_frame = ttk.Frame(export_frame)
        export_btn_frame.grid(row=0, column=0, pady=5)

        ttk.Button(export_btn_frame, text="📤 Exporter code autonome", 
                  command=self.export_standalone_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_btn_frame, text="📥 Exporter données CSV", 
                  command=self.export_data_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_btn_frame, text="📊 Exporter PNG", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)

        # ============================================================
        # VISUALISATION
        # ============================================================

        viz_frame = ttk.LabelFrame(main_frame, text="Visualisation", padding="10")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Régression quantile avec splines contraintes')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim([0, 1])

        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(self.canvas, viz_frame)
        toolbar.update()

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.press = None
        self.current_line = None

        # Initialisation
        self.toggle_constraint_mode()
        self.update_degree()
        self.knot_mode_changed()
        self.check_modules()



        


    # ============ MENU ============
    def setup_menu(self):
        """Configure le menu de l'application."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Charger CSV", command=self.load_csv)
        file_menu.add_command(label="Charger Excel", command=self.load_excel)
        file_menu.add_command(label="Exporter les résultats(png)", command=self.export_results)
        # Dans l'onglet 3, après btn_frame
        
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app)
        
        
        # Menu Exemples
        
        examples_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exemples", menu=examples_menu)
        examples_menu.add_command(label="Basic", command=self.load_basic_example)
        examples_menu.add_command(label="Exemple courbe logistique (degré du menu) ", command=self.run_logistic_example)

        examples_menu.add_separator()
        examples_menu.add_command(label="Load global temperature data ", command=self.load_temperature_example)
        examples_menu.add_command(label="Analysis  température data (contraints)", command=self.run_temperature_analysis)
        
        
        
        # Menu Scripts
        scripts_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Scripts", menu=scripts_menu)
#        scripts_menu.add_command(label="Exécuter example_basic.py", command=self.load_basic_example)
#        scripts_menu.add_command(label="Exécuter comparison_example.py", command=self.run_comparison_example)
    
    # ============ MÉTHODES ============
    
    def check_modules(self):
        if SplineCubicQuant is None:
            messagebox.showwarning("Attention", "Module spline cubique non trouvé.")
        if SplineQuarticQuant is None:
            messagebox.showwarning("Attention", "Module spline quartique non trouvé.")
        if SplineQuadraticQuant is None:
            messagebox.showwarning("Attention", "Module spline quadratique non trouvé.")
        if SplineLinearQuant is None:
            messagebox.showwarning("Attention", "Module spline linéaire non trouvé.")
    
    def toggle_constraint_mode(self):
        mode = self.constraint_mode_var.get()
        if mode == "uniform":
            self.uniform_frame.grid()
            self.region_frame.grid_remove()
            self.constraints_mode = "uniform"
        else:
            self.uniform_frame.grid_remove()
            self.region_frame.grid()
            self.constraints_mode = "region"
    
    def update_degree(self):
        self.degree = self.degree_var.get()
        if self.degree >= 2:
            self.convex_frame.grid()
        else:
            self.convex_frame.grid_remove()
            self.convex_var.set(0)
        if self.degree >= 3:
            self.der3_frame.grid()
        else:
            self.der3_frame.grid_remove()
            self.der3_var.set(0)
    
    def knot_mode_changed(self):
        mode = self.knot_mode.get()
        if mode == "auto":
            self.knot_spinbox.config(state='normal')
            self.define_knots_btn.config(text="Définir nœuds", state='normal')
            self.validate_knots_btn.config(state='disabled')
            self.manual_knots_mode = False
        else:
            self.knot_spinbox.config(state='disabled')
            self.define_knots_btn.config(text="Démarrer saisie", state='normal')
            self.validate_knots_btn.config(state='normal')
            self.manual_knots_mode = False
    
    # ============ Import données ============
    def load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if filename:
            try:
                df = pd.read_csv(filename)
                df_val=df.values
                self.xtab=df_val[:,0]
                self.ytab=df_val[:,1]
                x_min=min(self.xtab)
                x_max = max(self.xtab)
                self.ax.set_xlim([x_min, x_max])
                # Mettre à jour les informations
                self.data_info.set(f"{len(self.xtab)} points")
                self.status_var.set("Données chargées avec succès")
                self.canvas.draw()
                self.clear_all()
                self.plot_data()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    
    def load_excel(self):
        filename = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx *.xls")])
        if filename:
            try:
                df = pd.read_excel(filename)
                df_val=df.values
                self.xtab=df_val[:,0]
                self.ytab=df_val[:,1]
                x_min, x_max = self.xtab.min(), self.xtab.max()
                self.ax.set_xlim([x_min, x_max])
                # Mettre à jour les informations
                self.data_info.set(f"{len(self.xtab)} points")
                self.status_var.set("Données chargées avec succès")
                self.canvas.draw()
                self.clear_all()
                self.plot_data()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))


    
    def generate_test_data(self):
        np.random.seed(42)
        n = 200
        self.xtab = np.linspace(0, 1, n)
        self.ytab = 2*self.xtab + 0.2*np.sin(10*np.pi*self.xtab) + 0.05*np.random.randn(n)
        self.clear_all()
        self.plot_data()
        self.data_info.set(f"{n} points (test)")
        self.status_var.set("Données test générées")
    
    # ============ Nœuds ============
    def define_knots(self):
        if self.xtab is None:
            messagebox.showwarning("Attention", "Chargez d'abord des données")
            return
        if self.knot_mode.get() == "auto":
            kn = self.knot_count.get()
            self.knots = np.quantile(self.xtab, np.linspace(0, 1, kn + 1))
            self.plot_knots()
            self.status_var.set(f"{len(self.knots)} nœuds auto (quantiles)")
        else:
            self.manual_knots_mode = True
            self.temp_knots = []
            self.status_var.set("Mode manuel: cliquez sur le graphique pour ajouter des nœuds")
            self.define_knots_btn.config(state='disabled')
    
    def validate_manual_knots(self):
        if len(self.temp_knots) < 2:
            messagebox.showwarning("Attention", "Ajoutez au moins 2 nœuds")
            return
        self.knots = np.array(sorted(self.temp_knots))
        self.manual_knots_mode = False
        self.define_knots_btn.config(state='normal')
        self.plot_knots()
        self.status_var.set(f"{len(self.knots)} nœuds manuels validés")
    
    def clear_knots(self):
        self.knots = None
        self.temp_knots = []
        self.manual_knots_mode = False
        self.define_knots_btn.config(state='normal')
        for line in self.knot_lines:
            try:
                line.remove()
            except:
                pass
        self.knot_lines = []
        self.canvas.draw()
        self.status_var.set("Nœuds effacés")
    
    def plot_knots(self):
        for line in self.knot_lines:
            try:
                line.remove()
            except:
                pass
        self.knot_lines = []
        if self.knots is not None:
            ylim = self.ax.get_ylim()
            y_pos = ylim[1] * 0.95
            for k in self.knots:
                line = self.ax.axvline(x=k, color='red', linestyle='--', alpha=0.5)
                self.knot_lines.append(line)
            markers = self.ax.plot(self.knots, np.ones_like(self.knots) * y_pos, 'r|', markersize=10, label='Nœuds')
            self.knot_lines.extend(markers)
            self.ax.legend()
            self.canvas.draw()
    
    # ============ Régions ============
    def start_region_selection(self):
        self.constraint_mode_var.set("region")
        self.toggle_constraint_mode()
        self.status_var.set("Mode région: cliquez-glissez pour définir une zone")
    
    def clear_regions(self):
        self.regions = []
        self.region_listbox.delete(0, tk.END)
        for patch in self.region_patches:
            try:
                patch.remove()
            except:
                pass
        self.region_patches = []
        self.canvas.draw()
        self.status_var.set("Régions effacées")
    
    # ============ Résultats ============
    def clear_results(self):
        self.spline_result = None
        self.plot_data()
        if self.knots is not None:
            self.plot_knots()
    
    def clear_all(self):
        self.clear_knots()
        self.clear_regions()
        self.clear_results()
        self.plot_data()
        self.status_var.set("Tout effacé")
    
    # ============ Visualisation ============
    def adjust_axes(self):
        """Ajuste les axes en fonction des données."""
        if self.xtab is None or self.ytab is None:
            return

        # Axe X
        x_min, x_max = self.xtab.min(), self.xtab.max()
        margin_x = 0.05 * (x_max - x_min) if x_max > x_min else 0.1
        self.ax.set_xlim([x_min - margin_x, x_max + margin_x])

        # Axe Y
        y_min, y_max = self.ytab.min(), self.ytab.max()
        margin_y = 0.1 * (y_max - y_min) if y_max > y_min else 0.1
        self.ax.set_ylim([y_min - margin_y, y_max + margin_y])

        self.canvas.draw()
    def apply_axes_limits(self):
        """Applique les limites d'axes définies par l'utilisateur."""
        try:
            xmin = self.xmin_var.get()
            xmax = self.xmax_var.get()

            if xmin >= xmax:
                messagebox.showwarning("Attention", "X min doit être inférieur à X max.")
                return

            self.ax.set_xlim([xmin, xmax])
            self.canvas.draw()
            self.status_var.set(f"Axes ajustés: [{xmin:.3f}, {xmax:.3f}]")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")

    def adjust_axes(self):
        """Ajuste automatiquement les axes en fonction des données."""
        if self.xtab is None or self.ytab is None:
            messagebox.showwarning("Attention", "Aucune donnée pour ajuster les axes.")
            return

        # Axe X
        x_min, x_max = self.xtab.min(), self.xtab.max()
        margin_x = 0.05 * (x_max - x_min) if x_max > x_min else 0.1
        xlim_min = x_min - margin_x
        xlim_max = x_max + margin_x

        # Axe Y
        y_min, y_max = self.ytab.min(), self.ytab.max()
        margin_y = 0.1 * (y_max - y_min) if y_max > y_min else 0.1
        ylim_min = y_min - margin_y
        ylim_max = y_max + margin_y

        self.ax.set_xlim([xlim_min, xlim_max])
        self.ax.set_ylim([ylim_min, ylim_max])

        # Mettre à jour les champs
        self.xmin_var.set(xlim_min)
        self.xmax_var.set(xlim_max)

        self.canvas.draw()
        self.status_var.set(f"Axes auto: X=[{xlim_min:.3f}, {xlim_max:.3f}]")
        
    def plot_data(self):
        """Affiche les données avec les bons axes."""
        self.ax.clear()
        if self.xtab is not None and self.ytab is not None:
            self.ax.scatter(self.xtab, self.ytab, alpha=0.5, s=20, label='Données')

            # === RÉGLER LES AXES EN FONCTION DES DONNÉES ===
            # Axe X
            x_min, x_max = self.xtab.min(), self.xtab.max()
            margin_x = 0.05 * (x_max - x_min) if x_max > x_min else 0.1
            self.ax.set_xlim([x_min - margin_x, x_max + margin_x])

            # Axe Y
            y_min, y_max = self.ytab.min(), self.ytab.max()
            margin_y = 0.1 * (y_max - y_min) if y_max > y_min else 0.1
            self.ax.set_ylim([y_min - margin_y, y_max + margin_y])

        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Régression quantile avec splines contraintes')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.canvas.draw()
        
    def plot_data_back(self):
        self.ax.clear()
        if self.xtab is not None and self.ytab is not None:
            self.ax.scatter(self.xtab, self.ytab, alpha=0.5, s=20, label='Données')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Régression quantile avec splines contraintes')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim([0, 1])
        self.ax.legend()
        self.canvas.draw()
    
    def plot_result(self):
        if self.spline_result is not None:
            x_eval = np.linspace(self.xtab[0], self.xtab[-1], 500)
            y_eval = self.spline_result(x_eval)
            color = self.color_var.get()
            line = self.ax.plot(x_eval, y_eval, color=color, linewidth=2, label=f'τ={self.tau_var.get():.2f}')
            self.curve_lines.append(line[0])
            self.curve_count = len(self.curve_lines)
            self.curve_count_var.set(f"Courbes: {self.curve_count}")
            self.ax.legend()
            self.canvas.draw()
    
    def apply_color(self):
        self.status_var.set(f"Couleur changée: {self.color_var.get()}")
    
    def clear_last_curve(self):
        if self.curve_lines:
            last_line = self.curve_lines.pop()
            try:
                last_line.remove()
            except:
                pass
            self.curve_count = len(self.curve_lines)
            self.curve_count_var.set(f"Courbes: {self.curve_count}")
            self.canvas.draw()
            self.status_var.set("Dernière courbe effacée")
    
    def clear_all_curves(self):
        for line in self.curve_lines:
            try:
                line.remove()
            except:
                pass
        self.curve_lines = []
        self.curve_count = 0
        self.curve_count_var.set("Courbes: 0")
        self.plot_data()
        if self.knots is not None:
            self.plot_knots()
        self.status_var.set("Toutes les courbes effacées")
    
    # ============ Événements souris ============
    def on_click(self, event):
        if event.inaxes != self.ax or self.xtab is None:
            return
        if self.manual_knots_mode:
            x = event.xdata
            if 0 <= x <= 1:
                self.temp_knots.append(x)
                line = self.ax.axvline(x=x, color='orange', linestyle=':', alpha=0.7)
                self.knot_lines.append(line)
                self.canvas.draw()
                self.status_var.set(f"Nœud temporaire: {x:.3f} ({len(self.temp_knots)})")
        elif self.constraints_mode == "region" and self.knots is not None:
            self.press = event.xdata
            if self.current_line:
                self.current_line.remove()
            self.current_line = self.ax.axvline(x=self.press, color='green', alpha=0.5)
            self.canvas.draw()
    
    def on_motion(self, event):
        if self.press is None or event.inaxes != self.ax:
            return
        if self.constraints_mode == "region" and self.current_line:
            self.current_line.set_xdata([self.press, event.xdata])
            self.canvas.draw()
    
    def on_release(self, event):
        if self.press is None or event.inaxes != self.ax:
            return
        if self.constraints_mode == "region" and self.knots is not None:
            x1, x2 = self.press, event.xdata
            if x1 < x2 and 0 <= x1 <= 1 and 0 <= x2 <= 1:
                self.show_region_dialog(x1, x2)
            if self.current_line:
                self.current_line.remove()
                self.current_line = None
            self.press = None
            self.canvas.draw()
    
    def show_region_dialog(self, xmin, xmax):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Région [{xmin:.2f}, {xmax:.2f}]")
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        row = 0
        ttk.Label(dialog, text="Monotonie:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        monot_var = tk.IntVar(value=0)
        ttk.Radiobutton(dialog, text="↗", variable=monot_var, value=1).grid(row=row, column=1)
        ttk.Radiobutton(dialog, text="↘", variable=monot_var, value=-1).grid(row=row, column=2)
        ttk.Radiobutton(dialog, text="✗", variable=monot_var, value=0).grid(row=row, column=3)
        row += 1
        
        convex_var = tk.IntVar(value=0)
        der3_var = tk.IntVar(value=0)
        if self.degree >= 2:
            ttk.Label(dialog, text="Convexité:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Radiobutton(dialog, text="∪", variable=convex_var, value=1).grid(row=row, column=1)
            ttk.Radiobutton(dialog, text="∩", variable=convex_var, value=-1).grid(row=row, column=2)
            ttk.Radiobutton(dialog, text="✗", variable=convex_var, value=0).grid(row=row, column=3)
            row += 1
        if self.degree >= 3:
            ttk.Label(dialog, text="Dérivée 3e:").grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Radiobutton(dialog, text="+", variable=der3_var, value=1).grid(row=row, column=1)
            ttk.Radiobutton(dialog, text="-", variable=der3_var, value=-1).grid(row=row, column=2)
            ttk.Radiobutton(dialog, text="✗", variable=der3_var, value=0).grid(row=row, column=3)
            row += 1
        
        def add():
            region = [xmin, xmax, monot_var.get(), convex_var.get(), der3_var.get()]
            self.regions.append(region)
            m = {1:"↗", -1:"↘", 0:"-"}[monot_var.get()]
            c = {1:"∪", -1:"∩", 0:"-"}[convex_var.get()] if self.degree >= 2 else "-"
            d = {1:"+", -1:"-", 0:"-"}[der3_var.get()] if self.degree >= 3 else "-"
            self.region_listbox.insert(tk.END, f"[{xmin:.2f}, {xmax:.2f}]  M:{m} C:{c} D3:{d}")
            patch = self.ax.axvspan(xmin, xmax, alpha=0.2, color='yellow')
            self.region_patches.append(patch)
            self.canvas.draw()
            dialog.destroy()
            self.status_var.set(f"Région ajoutée [{xmin:.2f}, {xmax:.2f}]")
        
        ttk.Button(dialog, text="Ajouter", command=add).grid(row=row, column=0, columnspan=4, pady=20)
        ttk.Button(dialog, text="Annuler", command=dialog.destroy).grid(row=row+1, column=0, columnspan=4)
    
    # ============ Contraintes ============
    def build_constraints_arrays(self, kn):
        monot = np.zeros(kn)
        cv = np.zeros(kn + 1)
        der3 = np.zeros(kn + 1)
        if self.constraints_mode == "uniform":
            monot = np.ones(kn) * self.monot_var.get()
            if self.degree >= 2:
                cv = np.ones(kn + 1) * self.convex_var.get()
            if self.degree >= 3:
                der3 = np.ones(kn + 1) * self.der3_var.get()
        else:
            for i in range(kn):
                x1, x2 = self.knots[i], self.knots[i + 1]
                for r in self.regions:
                    if r[1] > x1 and r[0] < x2:
                        if r[2] != 0:
                            monot[i] = r[2]
                        if self.degree >= 2 and r[3] != 0:
                            cv[i] = r[3]
                            cv[i + 1] = r[3]
                        if self.degree >= 3 and r[4] != 0:
                            der3[i] = r[4]
                            der3[i + 1] = r[4]
        return monot, cv, der3
    
    # ============ Exécution ============
    def run_regression(self):
        if self.xtab is None:
            messagebox.showwarning("Attention", "Chargez des données")
            return
        if self.knots is None:
            messagebox.showwarning("Attention", "Définissez les nœuds")
            return
        if self.degree == 1 and SplineLinearQuant is None:
            messagebox.showerror("Erreur", "Module spline linéaire non disponible")
            return
        if self.degree == 2 and SplineQuadraticQuant is None:
            messagebox.showerror("Erreur", "Module spline quadratique non disponible")
            return
        if self.degree == 3 and SplineCubicQuant is None:
            messagebox.showerror("Erreur", "Module spline cubique non disponible")
            return
        if self.degree == 4 and SplineQuarticQuant is None:
            messagebox.showerror("Erreur", "Module spline quartique non disponible")
            return
        
        self.progress.start()
        self.status_var.set("Calcul en cours...")
        self.root.update()
        
        try:
            kn = len(self.knots) - 1
            monot, cv, der3 = self.build_constraints_arrays(kn)
            tau = self.tau_var.get()
            solver = self.solver_var.get()
            
            print(f"Lancement avec solveur: {solver}")
            print(f"Degré: {self.degree}")
            print(f"Monotonie: {monot}")
            if self.degree >= 2:
                print(f"Convexité: {cv}")
            if self.degree >= 3:
                print(f"Dérivée 3: {der3}")
            
            if self.degree == 1:
                self.spline_result = SplineLinearQuant(self.xtab, self.ytab, self.knots, tau, monot=monot, solver=solver)
            elif self.degree == 2:
                self.spline_result = SplineQuadraticQuant(self.xtab, self.ytab, self.knots, tau, monot=monot, cv=cv, solver=solver)
            elif self.degree == 3:
                self.spline_result = SplineCubicQuant(self.xtab, self.ytab, self.knots, tau, monot, cv, der3, solver=solver)
            else:
                self.spline_result = SplineQuarticQuant(self.xtab, self.ytab, self.knots, tau, monot, cv, der3, solver=solver)
            
            self.progress.stop()
            if self.spline_result is not None:
                self.plot_result()
                ##=== AJUSTER LES AXES APRÈS LE TRACÉ ===
                self.adjust_axes()
                self.status_var.set(f"Réussi! τ={tau:.2f} (solveur: {solver})")
            else:
                self.status_var.set("Échec - non convergence")
        except Exception as e:
            self.progress.stop()
            self.status_var.set(f"Erreur: {str(e)[:50]}...")
            messagebox.showerror("Erreur", str(e))
            import traceback
            traceback.print_exc()
    
    # ============ Export ============
    def export_results(self):
        if self.spline_result is None:
            messagebox.showwarning("Attention", "Aucun résultat")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg"), ("CSV", "*.csv"), ("NumPy", "*.npy")]
        )
        if filename:
            try:
                if filename.endswith('.csv'):
                    x = np.linspace(0, 1, 500)
                    y = self.spline_result(x)
                    pd.DataFrame({'x': x, 'y': y}).to_csv(filename, index=False)
                elif filename.endswith('.npy'):
                    np.save(filename, self.spline_result.c)
                else:
                    self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                self.status_var.set(f"Exporté: {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def export_data_csv(self):
        """Exporte les données et la spline en CSV."""
        try:
            if self.xtab is None or self.ytab is None:
                messagebox.showwarning("Attention", "Aucune donnée à exporter.")
                return

            filename = filedialog.asksaveasfilename(
                title="Exporter les données CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])

            if not filename:
                return

            import pandas as pd

            # Créer le DataFrame
            data = {'x': self.xtab, 'y': self.ytab}

            # Ajouter les valeurs de la spline si disponible
            #if self.spline_result is not None:
            #    x_eval = np.linspace(self.xtab.min(), self.xtab.max(), 500)
            #    y_eval = self.spline_result(x_eval)
            #    data['spline_x'] = x_eval
            #    data['spline_y'] = y_eval

            df = pd.DataFrame(data)

            # Ajouter des métadonnées en commentaire
            with open(filename, 'w') as f:
                #f.write(f"# Généré par SplineQuantReg GUI\n")
                #f.write(f"# Degré: {self.degree}\n")
                #f.write(f"# τ: {self.tau_var.get()}\n")
                #f.write(f"# Monotonie: {self.monot_var.get()}\n")
                #f.write(f"# Convexité: {self.convex_var.get()}\n")
                #f.write(f"# Nœuds: {self.knots.tolist() if self.knots is not None else []}\n")
                #f.write("#\n")
                df.to_csv(f, index=False)

            self.status_var.set(f" Données exportées: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    # ============ EXEMPLES ============
    #def run_logistic_example1(self):
        
    def run_logistic_example(self):
     """Lance le test avec la fonction logistique."""
     try:
        import subprocess
        import os
        
        # Chercher le script example_logistic.py
        possible_paths = [
            os.path.join(PROJECT_ROOT, 'examples', 'logistic_example.py'),
            os.path.join(EXAMPLES_PATH, 'logistic_example.py'),
            'examples/logistic_example.py',
        ]
        
        script_path = None
        for p in possible_paths:
            if os.path.exists(p):
                script_path = p
                break
        
        if script_path is None:
            messagebox.showerror("Erreur", 
                "Fichier example_logistic.py non trouvé.\n\n"
                "Assurez-vous que le fichier existe dans le dossier examples/")
            return
        
        # Lancer le script
        self.status_var.set("Lancement du test logistique...")
        self.root.update()
        #Entrer la fonction logistique dans le champ de variables"
        
        self.test_function_var.set("exp(-5 + 10*x) / (1 + exp(-5 + 10*x)) + 0.2 * randn(n)")
        
        # Mettre à jour le nombre de points
        self.test_npoints_var.set(100)
        
        # Générer les données automatiquement
        self.generate_custom_test()
        
        # Mettre à jour le titre du graphique
        self.ax.set_title('Fonction logistique avec bruit')
        self.canvas.draw()
        
        #Charger le test tout fait
        
        #import sys #méthode subprocess
        #subprocess.Popen([sys.executable, script_path])
        
        import logistic_example # methode directe
        deg=self.degree
        logistic_example.run_logistic_example(degree=deg)
        self.status_var.set("Test logistique lancé")

     except Exception as e:
        messagebox.showerror("Erreur", f"Erreur: {e}")
        import traceback
        traceback.print_exc()
            
    def load_basic_example(self):
        """Charge et exécute l'exemple basic depuis un script externe."""
        try:
            import subprocess
            import os
            
            # Chercher le script example_basic.py
            possible_paths = [
                os.path.join(PROJECT_ROOT, 'examples', 'example_basic.py'),
                os.path.join(EXAMPLES_PATH, 'example_basic.py'),
                'examples/example_basic.py',
            ]
            
            script_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    script_path = p
                    break
            
            if script_path is None:
                messagebox.showerror("Erreur", 
                    "Fichier example_basic.py non trouvé.\n\n"
                    "Assurez-vous que le fichier existe dans le dossier examples/")
                return
            
            # Lancer le script
            self.status_var.set("Lancement de l'exemple basic...")
            self.root.update()
            
            import sys
            subprocess.Popen([sys.executable, script_path])
            
            self.status_var.set("Exemple basic lancé")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    def load_temperature_example(self):
        """Charge l'exemple des données de température."""
        try:
            import os
            import pandas as pd
            
            possible_paths = [
                os.path.join(PROJECT_ROOT, 'examples', 'temp.xls'),
                os.path.join(PROJECT_ROOT, 'data', 'temp.xls'),
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'examples', 'temp.xls'),
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
            
            temp = pd.read_excel(file_path)
            temp_val = temp.values
            year = temp_val[:, 0]
            ytab = temp_val[:, 1]
            
            xtab = (year - year[0]) / (year[-1] - year[0])
            
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
            import traceback
            traceback.print_exc()
    def run_temperature_analysis(self):
     """Lance une analyse complète des données de température avec différentes contraintes."""
     try:
        import os
        import pandas as pd
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # Chercher le fichier temp.xls
        possible_paths = [
            os.path.join(PROJECT_ROOT, 'examples', 'temp.xls'),
            os.path.join(PROJECT_ROOT, 'data', 'temp.xls'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'examples', 'temp.xls'),
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
        
        # Nœuds spécifiques pour l'étude des tendances
        year_knots = np.array([1880, 1889, 1900, 1910, 1930, 1940, 1965, 1992])
        knots = (year_knots - 1880) / (1992 - 1880)
        kn = len(knots) - 1
        
        def yr(x):
            return 1880 + x * (1992 - 1880)
        
        # Créer la figure
        fig = Figure(figsize=(16, 10), dpi=100)
        x_eval = np.linspace(0, 1, 500)
        tau = 0.5
        solver = 'CLARABEL'
        
        # ============================================
        # 1. Sans contraintes
        # ============================================
        ax1 = fig.add_subplot(2, 3, 1)
        ax1.scatter(yr(xtab), ytab, alpha=0.5, s=15, color='gray', label='Données')
        ax1.set_title('1. Sans contraintes')
        ax1.set_xlabel('Année')
        ax1.set_ylabel('Δ Température (°C)')
        
        try:
            res = SplineCubicQuant(xtab, ytab, knots, tau, monot=0, cv=0, der3=0, solver=solver)
            if res is not None:
                ax1.plot(yr(x_eval), res(x_eval), 'b-', linewidth=2, label=f'τ={tau}')
        except Exception as e:
            print(f"Erreur: {e}")
        
        ax1.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'r|', markersize=8, label='Nœuds')
        ax1.legend(fontsize='small')
        ax1.grid(True, alpha=0.3)
        
        # ============================================
        # 2. Contrainte croissante partout
        # ============================================
        ax2 = fig.add_subplot(2, 3, 2)
        ax2.scatter(yr(xtab), ytab, alpha=0.5, s=15, color='gray', label='Données')
        ax2.set_title('2. Contrainte croissante')
        ax2.set_xlabel('Année')
        ax2.set_ylabel('Δ Température (°C)')
        
        try:
            res = SplineCubicQuant(xtab, ytab, knots, tau, monot=1, cv=0, der3=0, solver=solver)
            if res is not None:
                ax2.plot(yr(x_eval), res(x_eval), 'g-', linewidth=2, label='Croissante')
        except Exception as e:
            print(f"Erreur: {e}")
        
        ax2.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'r|', markersize=8, label='Nœuds')
        ax2.legend(fontsize='small')
        ax2.grid(True, alpha=0.3)
        
        # ============================================
        # 3. Contrainte décroissante (contre-nature)
        # ============================================
        ax3 = fig.add_subplot(2, 3, 3)
        ax3.scatter(yr(xtab), ytab, alpha=0.5, s=15, color='gray', label='Données')
        ax3.set_title('3. Contrainte décroissante')
        ax3.set_xlabel('Année')
        ax3.set_ylabel('Δ Température (°C)')
        
        try:
            res = SplineCubicQuant(xtab, ytab, knots, tau, monot=-1, cv=0, der3=0, solver=solver)
            if res is not None:
                ax3.plot(yr(x_eval), res(x_eval), 'r-', linewidth=2, label='Décroissante')
        except Exception as e:
            print(f"Erreur: {e}")
        
        ax3.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'r|', markersize=8, label='Nœuds')
        ax3.legend(fontsize='small')
        ax3.grid(True, alpha=0.3)
        
        # ============================================
        # 4. Contrainte croissante + convexe
        # ============================================
        ax4 = fig.add_subplot(2, 3, 4)
        ax4.scatter(yr(xtab), ytab, alpha=0.5, s=15, color='gray', label='Données')
        ax4.set_title('4. Croissante + Convexe')
        ax4.set_xlabel('Année')
        ax4.set_ylabel('Δ Température (°C)')
        
        try:
            res = SplineCubicQuant(xtab, ytab, knots, tau, monot=1, cv=1, der3=0, solver=solver)
            if res is not None:
                ax4.plot(yr(x_eval), res(x_eval), 'm-', linewidth=2, label='Croissante+Convexe')
        except Exception as e:
            print(f"Erreur: {e}")
        
        ax4.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'r|', markersize=8, label='Nœuds')
        ax4.legend(fontsize='small')
        ax4.grid(True, alpha=0.3)
        
        # ============================================
        # 5. Contrainte partielle (décroissante sur 1940-1965)
        # ============================================
        ax5 = fig.add_subplot(2, 3, 5)
        ax5.scatter(yr(xtab), ytab, alpha=0.5, s=15, color='gray', label='Données')
        ax5.set_title('5. Contrainte partielle\n(croissante sauf 1940-1965)')
        ax5.set_xlabel('Année')
        ax5.set_ylabel('Δ Température (°C)')
        
        # Contrainte: décroissante sur l'intervalle 1940-1965
        monot_partiel = [1, 1, 1, 1, 1, -1, 1]  # 7 intervalles
        # correspond aux années: 1880-1889, 1889-1900, 1900-1910, 1910-1930, 
        # 1930-1940, 1940-1965, 1965-1992
        
        try:
            res = SplineCubicQuant(xtab, ytab, knots, tau, monot=monot_partiel, cv=0, der3=0, solver=solver)
            if res is not None:
                ax5.plot(yr(x_eval), res(x_eval), 'c-', linewidth=2, label='Partielle')
                
                # Colorier la zone 1940-1965
                ax5.axvspan(1940, 1965, alpha=0.2, color='yellow', label='Zone décroissante')
        except Exception as e:
            print(f"Erreur: {e}")
        
        ax5.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'r|', markersize=8, label='Nœuds')
        ax5.legend(fontsize='small')
        ax5.grid(True, alpha=0.3)
        
        # ============================================
        # 6. Comparaison de toutes les contraintes
        # ============================================
        ax6 = fig.add_subplot(2, 3, 6)
        ax6.scatter(yr(xtab), ytab, alpha=0.3, s=10, color='gray', label='Données')
        ax6.set_title('6. Comparaison des approches')
        ax6.set_xlabel('Année')
        ax6.set_ylabel('Δ Température (°C)')
        
        colors = ['blue', 'green', 'red', 'magenta', 'cyan']
        labels = ['Sans', 'Croissante', 'Décroissante', 'C+Convexe', 'Partielle']
        
        # Tracer les 5 courbes
        for i, (monot, cv_val, color, label) in enumerate(zip(
            [0, 1, -1, 1, monot_partiel],
            [0, 0, 0, 1, 0],
            colors, labels
        )):
            try:
                res = SplineCubicQuant(xtab, ytab, knots, tau, monot=monot, cv=cv_val, der3=0, solver=solver)
                if res is not None:
                    ax6.plot(yr(x_eval), res(x_eval), color=color, linewidth=1.5, label=label)
            except Exception as e:
                print(f"Erreur pour {label}: {e}")
        
        ax6.plot(yr(knots), np.ones_like(knots)*max(ytab)*0.9, 'k|', markersize=8, label='Nœuds')
        ax6.legend(fontsize='small')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Créer une fenêtre Tkinter pour la figure
        fig_window = tk.Toplevel(self.root)
        fig_window.title("Analyse des températures - Régression quantile contrainte")
        fig_window.geometry("1200x800")
        
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
            self.temperature_years = year
            self.clear_all()
            self.plot_data()
            self.plot_knots()
            self.ax.set_title('Températures globales (1880-1992)')
            self.data_info.set(f"{len(xtab)} points (température)")
            self.status_var.set("Données température chargées depuis l'analyse")
            self.canvas.draw()
            fig_window.destroy()
        
        ttk.Button(btn_frame, text="Charger ces données dans la GUI", 
                  command=load_data_to_gui).pack(side=tk.LEFT, padx=5)
        
        self.status_var.set("Analyse des températures terminée")
        
     except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()
    
    
    def generate_custom_test(self):
        try:
            n = self.test_npoints_var.get()
            x = np.linspace(0, 1, n)
            func_str = self.test_function_var.get()
            func_str = func_str.replace('sin(', 'np.sin(')
            func_str = func_str.replace('cos(', 'np.cos(')
            func_str = func_str.replace('exp(', 'np.exp(')
            func_str = func_str.replace('log(', 'np.log(')
            func_str = func_str.replace('sqrt(', 'np.sqrt(')
            func_str = func_str.replace('pi', 'np.pi')
            func_str = func_str.replace('randn(', 'np.random.randn(')
            func_str = func_str.replace('rand(', 'np.random.rand(')
            y = eval(func_str, {'np': np, 'x': x, 'n': n})
            self.xtab = x
            self.ytab = y
            self.clear_all()
            self.plot_data()
            self.data_info.set(f"{n} points (test personnalisé)")
            self.status_var.set("Données test générées")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur dans la fonction: {str(e)}")
    def export_standalone_code(self):
        """
        Exporte un code Python autonome pour reproduire la courbe actuelle.
        Inclut les données (CSV), la fonction de test, et tous les paramètres.
        """
        try:
            import os
            import tempfile

            # Vérifier qu'il y a des données et un résultat
            if self.xtab is None or self.ytab is None:
                messagebox.showwarning("Attention", "Aucune donnée à exporter.")
                return

            if self.spline_result is None:
                messagebox.showwarning("Attention", "Aucune régression effectuée. Lancez d'abord la régression.")
                return

            # Demander où sauvegarder
            filename = filedialog.asksaveasfilename(
                title="Exporter le code Python autonome",
                defaultextension=".py",
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )

            if not filename:
                return

            # Récupérer les paramètres
            degree = self.degree
            tau = self.tau_var.get()
            solver = self.solver_var.get()
            monot = self.monot_var.get()
            convex = self.convex_var.get()
            der3 = self.der3_var.get()
            knots = np.array(self.knots) if self.knots is not None else []

            # Récupérer la fonction de test (si elle a été utilisée)
            test_function = self.test_function_var.get() if hasattr(self, 'test_function_var') else ""

            # Récupérer la couleur utilisée
            color = self.color_var.get() if hasattr(self, 'color_var') else 'blue'

            # Créer le code
            code = self._generate_standalone_code(
                xtab=self.xtab,
                ytab=self.ytab,
                knots=knots,
                degree=degree,
                tau=tau,
                solver=solver,
                monot=monot,
                convex=convex,
                der3=der3,
                test_function=test_function,
                color=color
            )

            # Écrire le fichier
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)

            self.status_var.set(f"✅ Code exporté: {os.path.basename(filename)}")
            messagebox.showinfo("Succès", 
                f"Code exporté avec succès vers:\n{filename}\n\n"
                "Vous pouvez exécuter ce fichier indépendamment.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
            import traceback
            traceback.print_exc()


    def _generate_standalone_code(self, xtab, ytab, knots, degree, tau, solver, 
                                   monot, convex, der3, test_function, color):
        """
        Génère le code Python autonome.
        """
        import numpy as np

        # Convertir les données en chaînes pour le code
        xtab_str = np.array2string(xtab, precision=6, separator=', ', max_line_width=100)
        ytab_str = np.array2string(ytab, precision=6, separator=', ', max_line_width=100)
        knots_str = np.array2string(knots, precision=6, separator=', ', max_line_width=100)

        # Construction du code
        code = f'''#!/usr/bin/env python
        # -*- coding: utf-8 -*-

        import numpy as np
        import matplotlib.pyplot as plt
        import sys
        import os

        # Ajouter le chemin du projet si nécessaire
        try:
            from BsplineQuantRegpy import SplineCubicQuant, SplineQuarticQuant, SplineLinearQuant, SplineQuadraticQuant
        except ImportError:
            try:
                from PysplineQuantReg import SplineCubicQuant, SplineQuarticQuant, SplineLinearQuant, SplineQuadraticQuant
            except ImportError:
                print("Erreur: impossible d'importer les modules spline.")
                print("Assurez-vous que le package est installé ou dans le PYTHONPATH.")
                sys.exit(1)

        # ============ PARAMÈTRES ============
        DEGREE = {degree}
        TAU = {tau}
        SOLVER = '{solver}'
        MONOT = {monot}
        CONVEX = {convex}
        DER3 = {der3}
        COLOR = '{color}'

        # ============ DONNÉES ============
        x = np.array({xtab_str})
        y = np.array({ytab_str})
        knots = np.array({knots_str})

        print("=" * 70)
        print("RÉGRESSION QUANTILE AVEC SPLINES CONTRAINTES")
        print("=" * 70)
        print(f"Degré: {{DEGREE}}")
        print(f"τ: {{TAU}}")
        print(f"Solveur: {{SOLVER}}")
        print(f"Monotonie: {{MONOT}}")
        print(f"Convexité: {{CONVEX}}")
        print(f"Dérivée 3: {{DER3}}")
        print(f"Nombre de points: {{len(x)}}")
        print(f"Nombre de nœuds: {{len(knots)}}")

        # ============ RÉGRESSION ============
        # Sélectionner la fonction appropriée selon le degré
        if DEGREE == 1:
            from BsplineQuantRegpy import SplineLinearQuant as spline_func
        elif DEGREE == 2:
            from BsplineQuantRegpy import SplineQuadraticQuant as spline_func
        elif DEGREE == 3:
            from BsplineQuantRegpy import SplineCubicQuant as spline_func
        else:
            from BsplineQuantRegpy import SplineQuarticQuant as spline_func

        print("\\nLancement de la régression...")

        try:
            result = spline_func(
                x, y, knots, 
                tau=TAU, 
                monot=MONOT, 
                cv=CONVEX, 
                der3=DER3,
                solver=SOLVER
            )
        except TypeError:
            # Fallback pour les fonctions qui n'acceptent pas der3
            try:
                result = spline_func(
                    x, y, knots, 
                    tau=TAU, 
                    monot=MONOT, 
                    cv=CONVEX, 
                    solver=SOLVER
                )
            except:
                result = spline_func(
                    x, y, knots, 
                    tau=TAU, 
                    monot=MONOT, 
                    solver=SOLVER
                )

        if result is None:
            print("❌ La régression n'a pas convergé.")
            sys.exit(1)

        print("✅ Régression réussie !")

        # ============ ÉVALUATION ============
        x_eval = np.linspace(min(x), max(x), 500)
        y_eval = result(x_eval)

        # ============ VISUALISATION ============
        fig, ax = plt.subplots(figsize=(10, 6))

        # Données
        ax.scatter(x, y, alpha=0.5, s=20, color='gray', label='Données')

        # Spline
        ax.plot(x_eval, y_eval, color=COLOR, linewidth=2, 
                label=f'Spline degré {{DEGREE}}, τ={{TAU}}')

        # Nœuds
        ax.plot(knots, np.ones_like(knots)*max(y)*0.95, 'r|', 
                markersize=10, label='Nœuds')

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'Régression quantile avec splines (degré {{DEGREE}}, τ={{TAU}})')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        print("\\n" + "=" * 70)
        print("EXÉCUTION TERMINÉE")
        print("=" * 70)
        '''

        return code


    def _get_timestamp(self):
        """Retourne la date et l'heure actuelles."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    root = tk.Tk()
    app = QuantileSplineApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

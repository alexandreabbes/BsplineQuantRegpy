def run_comparison_example(self):
    """Lance un exemple comparant les différents degrés avec différentes contraintes."""
    try:
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        np.random.seed(42)
        n = 300
        x = np.linspace(0, 1, n)
        
        # Fonction avec différentes formes selon les régions
        y = np.zeros(n)
        # Région 1: [0, 0.3] - croissante convexe
        idx1 = x <= 0.3
        y[idx1] = 2 * x[idx1]**2 + 0.05 * np.random.randn(np.sum(idx1))
        
        # Région 2: [0.3, 0.6] - croissante concave
        idx2 = (x > 0.3) & (x <= 0.6)
        x2 = x[idx2]
        y[idx2] = 0.18 + 0.5 * np.sqrt(x2 - 0.3) + 0.05 * np.random.randn(np.sum(idx2))
        
        # Région 3: [0.6, 1] - décroissante
        idx3 = x > 0.6
        x3 = x[idx3]
        y[idx3] = 0.7 - 0.8 * (x3 - 0.6)**2 + 0.05 * np.random.randn(np.sum(idx3))
        
        # Nœuds (plus de nœuds pour capturer les variations)
        kn = 15
        knots = np.quantile(x, np.linspace(0, 1, kn + 1))
        
        # Créer une nouvelle figure pour l'exemple
        fig = Figure(figsize=(14, 10), dpi=100)
        
        # 1. Sans contraintes - Comparaison des degrés
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.scatter(x, y, alpha=0.3, s=10, color='gray', label='Données')
        
        colors = ['blue', 'green', 'red', 'orange']
        deg_labels = ['Linéaire (deg 1)', 'Quadratique (deg 2)', 'Cubique (deg 3)', 'Quartique (deg 4)']
        
        x_eval = np.linspace(0, 1, 500)
        for d, color, label in zip([1, 2, 3, 4], colors, deg_labels):
            try:
                if d == 1:
                    res = SplineLinearQuantile(x, y, knots, tau=0.5, 
                                               monot=0, solver='CLARABEL')
                elif d == 2:
                    res = SplineQuadraticQuantile(x, y, knots, tau=0.5,
                                                  monot=0, cv=0, solver='CLARABEL')
                elif d == 3:
                    res = SplineCubicQuantile(x, y, knots, tau=0.5,
                                              monot=0, cv=0, der3=0, solver='CLARABEL')
                else:
                    res = SplineQuarticQuantile(x, y, knots, tau=0.5,
                                                monot=0, cv=0, d3=0, solver='CLARABEL')
                
                if res is not None:
                    ax1.plot(x_eval, res(x_eval), color=color, linewidth=2, label=label)
            except Exception as e:
                print(f"Erreur degré {d}: {e}")
        
        ax1.plot(knots, np.ones_like(knots)*max(y)*0.95, 'k|', markersize=8, label='Nœuds')
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.set_title('Sans contraintes - Comparaison des degrés')
        ax1.legend(fontsize='small')
        ax1.grid(True, alpha=0.3)
        
        # 2. Contrainte croissante - Comparaison des degrés
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.scatter(x, y, alpha=0.3, s=10, color='gray', label='Données')
        
        for d, color, label in zip([1, 2, 3, 4], colors, deg_labels):
            try:
                if d == 1:
                    res = SplineLinearQuantile(x, y, knots, tau=0.5, 
                                               monot=1, solver='CLARABEL')
                elif d == 2:
                    res = SplineQuadraticQuantile(x, y, knots, tau=0.5,
                                                  monot=1, cv=0, solver='CLARABEL')
                elif d == 3:
                    res = SplineCubicQuantile(x, y, knots, tau=0.5,
                                              monot=1, cv=0, der3=0, solver='CLARABEL')
                else:
                    res = SplineQuarticQuantile(x, y, knots, tau=0.5,
                                                monot=1, cv=0, d3=0, solver='CLARABEL')
                
                if res is not None:
                    ax2.plot(x_eval, res(x_eval), color=color, linewidth=2, label=label)
            except Exception as e:
                print(f"Erreur degré {d} avec contrainte croissante: {e}")
        
        ax2.plot(knots, np.ones_like(knots)*max(y)*0.95, 'k|', markersize=8, label='Nœuds')
        ax2.set_xlabel('x')
        ax2.set_ylabel('y')
        ax2.set_title('Contrainte croissante')
        ax2.legend(fontsize='small')
        ax2.grid(True, alpha=0.3)
        
        # 3. Contrainte convexe - Comparaison des degrés (2, 3, 4 seulement)
        ax3 = fig.add_subplot(2, 2, 3)
        ax3.scatter(x, y, alpha=0.3, s=10, color='gray', label='Données')
        
        deg2_labels = ['Quadratique (deg 2)', 'Cubique (deg 3)', 'Quartique (deg 4)']
        colors2 = ['green', 'red', 'orange']
        
        for d, color, label in zip([2, 3, 4], colors2, deg2_labels):
            try:
                if d == 2:
                    res = SplineQuadraticQuantile(x, y, knots, tau=0.5,
                                                  monot=0, cv=1, solver='CLARABEL')
                elif d == 3:
                    res = SplineCubicQuantile(x, y, knots, tau=0.5,
                                              monot=0, cv=1, der3=0, solver='CLARABEL')
                else:
                    res = SplineQuarticQuantile(x, y, knots, tau=0.5,
                                                monot=0, cv=1, d3=0, solver='CLARABEL')
                
                if res is not None:
                    ax3.plot(x_eval, res(x_eval), color=color, linewidth=2, label=label)
            except Exception as e:
                print(f"Erreur degré {d} avec contrainte convexe: {e}")
        
        ax3.plot(knots, np.ones_like(knots)*max(y)*0.95, 'k|', markersize=8, label='Nœuds')
        ax3.set_xlabel('x')
        ax3.set_ylabel('y')
        ax3.set_title('Contrainte convexe (deg 2, 3, 4)')
        ax3.legend(fontsize='small')
        ax3.grid(True, alpha=0.3)
        
        # 4. Contrainte croissante + convexe - Degrés 3 et 4
        ax4 = fig.add_subplot(2, 2, 4)
        ax4.scatter(x, y, alpha=0.3, s=10, color='gray', label='Données')
        
        for d, color, label in zip([3, 4], ['red', 'orange'], 
                                   ['Cubique (deg 3)', 'Quartique (deg 4)']):
            try:
                if d == 3:
                    res = SplineCubicQuantile(x, y, knots, tau=0.5,
                                              monot=1, cv=1, der3=0, solver='CLARABEL')
                else:
                    res = SplineQuarticQuantile(x, y, knots, tau=0.5,
                                                monot=1, cv=1, d3=0, solver='CLARABEL')
                
                if res is not None:
                    ax4.plot(x_eval, res(x_eval), color=color, linewidth=2, label=label)
            except Exception as e:
                print(f"Erreur degré {d} avec contrainte croissante+convexe: {e}")
        
        # Ajouter aussi le degré 1 et 2 pour comparaison (sans contrainte de convexité)
        try:
            res_lin = SplineLinearQuantile(x, y, knots, tau=0.5, monot=1, solver='CLARABEL')
            if res_lin is not None:
                ax4.plot(x_eval, res_lin(x_eval), color='blue', linewidth=1.5, 
                        linestyle='--', label='Linéaire (réf)')
        except:
            pass
        
        try:
            res_quad = SplineQuadraticQuantile(x, y, knots, tau=0.5, 
                                               monot=1, cv=0, solver='CLARABEL')
            if res_quad is not None:
                ax4.plot(x_eval, res_quad(x_eval), color='green', linewidth=1.5,
                        linestyle='--', label='Quadratique (réf)')
        except:
            pass
        
        ax4.plot(knots, np.ones_like(knots)*max(y)*0.95, 'k|', markersize=8, label='Nœuds')
        ax4.set_xlabel('x')
        ax4.set_ylabel('y')
        ax4.set_title('Contrainte croissante + convexe (deg 3, 4)')
        ax4.legend(fontsize='small')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Afficher dans la GUI
        # Créer une fenêtre Tkinter pour afficher la figure
        fig_window = tk.Toplevel(self.root)
        fig_window.title("Comparaison des degrés avec contraintes")
        fig_window.geometry("1000x800")
        
        canvas = FigureCanvasTkAgg(fig, master=fig_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Ajouter une barre d'outils
        toolbar = NavigationToolbar2Tk(canvas, fig_window)
        toolbar.update()
        
        # Ajouter un bouton pour fermer
        btn_frame = ttk.Frame(fig_window)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Fermer", command=fig_window.destroy).pack()
        
        self.status_var.set("Comparaison des degrés affichée")
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur dans la comparaison: {str(e)}")
        import traceback
        traceback.print_exc()
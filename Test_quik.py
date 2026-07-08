#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

# Importer directement depuis votre fichier
from SplineQuarticQuantBspkn4_V4 import SplineCubicQuantile

# Générer des données
np.random.seed(42)
x = np.linspace(0, 1, 100)
y = 3*x + 0.2*np.sin(10*np.pi*x) + 0.05*np.random.randn(100)
knots = np.quantile(x, np.linspace(0, 1, 11))

# Tester
print("Test de SplineCubicQuantile...")
res = SplineCubicQuantile(x, y, knots, tau=0.5, solver='CLARABEL')

if res is not None:
    x_eval = np.linspace(0, 1, 200)
    plt.scatter(x, y, alpha=0.3, s=10, color='gray')
    plt.plot(x_eval, res(x_eval), 'r-', linewidth=2)
    plt.plot(knots, np.ones_like(knots)*max(y), 'r|', markersize=10)
    plt.title('Spline cubique')
    plt.show()
else:
    print("Échec de la régression")

Introduction
============

**BsplineQuantRegpy** est un package Python pour la régression quantile
avec des B-splines sous contraintes de forme (monotonie, convexité, dérivée troisième).

Objectifs
---------

Ce package permet de :

- Ajuster des modèles de régression quantile avec des B-splines de degré 1 à 4
- Imposer des contraintes de forme exactes sur tout l'intervalle ou une partie seulement. Les contraintes sont imposées avec la caractérisation de Karlin-Studden pour le signe de polynômes de degré 2 ou 3, qui conduisent à des de contraintes problèmes quadratiques: SOCP. 
- Utiliser une gui performante.

Fonctionnalités principales
---------------------------

- **SplineLinearQuant** : Régression avec splines linéaires (degré 1)
- **SplineQuadraticQuant** : Régression avec splines quadratiques (degré 2)
- **SplineCubicQuant** : Régression avec splines cubiques (degré 3)
- **SplineQuarticQuant** : Régression avec splines quartiques (degré 4)
- **quantile_spline** : Interface unifiée pour tous les degrés
- **run_gui** : Interface graphique Tkinter

Caractéristiques de la gui
--------------------------

- générer des données
- définir les noeuds
- choisir le quantile de régression
- imposer des contraintes multiples par régions,
- définir la taille de l'intervalle
- utiliser différents degrés de spline 
- choisir les couleurs
- accéder aux exemples du module en choisissant le degré des splines de régression.
- permet l'import-export de données et de code executable python


RÉFÉRENCES BIBLIOGRAPHIQUES
---------------------------

Abbes, A. (2025). Quantile regression with cubic polynomial splines
under shape constraints with applications.
doi:10.5281/zenodo.17427913

He, X., & Shi, P. (1998). Monotone B-spline smoothing.
Journal of the American Statistical Association, 93(442), 643-650.

Karlin, S., & Studden, W.J. (1966). Tchebycheff Systems:
With Applications in Analysis and Statistics. Interscience Publishers.

Papp, D., & Alizadeh, F. (2014). Shape-Constrained Estimation
Using Nonnegative Splines. Journal of Computational and Graphical
Statistics, 23(1), 211-231.
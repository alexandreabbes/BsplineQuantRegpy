#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alexandre Abbes"
__copyright__ = "Copyright 2026, Alexandre Adel Abbes"
__license__ = "GPL"
__version__ = "1.0.1"


import numpy as np
from scipy.interpolate import BSpline, PPoly
import numpy as np
import cvxpy as cp
import warnings

from ..core.bases import build_bsplines_and_deriv
from ..core.constraints import (
    apply_karlin_constraints_cubic,
    apply_karlin_constraints_quadratic,
    apply_val_constraints
)


def rhotau(u, tau):

    """  
    Fonction de perte quantile (check function).
    
    La fonction de perte quantile, également appelée fonction de vérification,
    est définie par ρ_τ(u) = u * (τ - 1_{u < 0}). Elle est utilisée comme
    fonction objectif en régression quantile.
    
    Parameters
    ----------
    u : cvxpy.Expression
        Résidus (valeurs réelles ou expressions CVXPY)
    tau : float, 0 < tau < 1
        Paramètre quantile
    
    Returns
    -------
    cvxpy.Expression
        Somme des pertes quantiles
    
    Notes
    -----
    La fonction est convexe et linéaire par morceaux.
    Pour τ = 0.5, elle correspond à l'erreur absolue médiane.
    """
    return cp.sum(cp.maximum(tau * u, (tau - 1) * u))


def SplineLinearQuant(xtab, ytab, knots, tau, monot=0, solver='CLARABEL', weight=None):
    """
    Régression quantile avec B-splines de degré 1 (affines par morceaux)
    et contraintes de monotonie.
    
    Les splines linéaires sont des fonctions continues et linéaires sur chaque
    intervalle entre les nœuds. La monotonie est contrôlée par le signe de
    la dérivée (constante par morceaux).
    
    Parameters
    ----------
    xtab, ytab : array-like
        Données x et y
    knots : int or list
        Nombre de nœuds ou liste des nœuds
    tau : float
        Paramètre quantile (entre 0 et 1)
    monot : int or list, default=0
        Contrainte de monotonie (+1 croissant, -1 décroissant, 0 aucune)
    solver : str, default='CLARABEL'
        Solveur CVXPY à utiliser
    weight : array-like, optional
        Poids des observations
        
    Returns
    -------
    polyn : BSpline object
        Fonction spline résultante (degré 1)
    
    Examples
    --------
    >>> import numpy as np
    >>> from BsplineQuantRegpy import SplineLinearQuant
    >>> x = np.linspace(0, 1, 50)
    >>> y = 2*x + 0.1*np.random.randn(50)
    >>> knots = np.quantile(x, np.linspace(0, 1, 6))
    >>> result = SplineLinearQuant(x, y, knots, tau=0.5, monot=1)
    >>> y_pred = result(np.linspace(0, 1, 100))
    """
     
    if weight is None:
        weight = np.ones(len(xtab))
    
    # Tri des données
    sort_idx = np.argsort(xtab)
    xtab = np.array(xtab)[sort_idx]
    ytab = np.array(ytab)[sort_idx]
    weight = np.array(weight)[sort_idx]
    
    n = len(xtab)
    
    # Gestion des nœuds
    if isinstance(knots, int):
        kn = knots - 1
        knots = np.quantile(xtab, np.linspace(0, 1, kn + 1))
    
    kn = len(knots) - 1
    degree = 1
    N = kn + degree  # Nombre de fonctions de base = kn + 1
    
    # Gestion des contraintes de monotonie
    if isinstance(monot, int):
        monot = monot * np.ones(kn)  # Une contrainte par intervalle
    else:
        monot = np.array(monot)
    
    print(f"=== Régression quantile avec splines linéaires (degré 1) ===")
    print(f"Nœuds: {kn}, Fonctions de base: {N}")
    print(f"Contraintes monotonie (dérivée): {monot}")
    
    # Construction des B-splines linéaires
    List_Bsplines, Der1_array = build_bsplines_and_deriv(knots,degree)
    
    # Matrice de design
    env_array = np.zeros((n, N))
    for j in range(N):
        env_array[:, j] = List_Bsplines[j](xtab)
    
    # Variables d'optimisation
    alpha = cp.Variable(N)  # Coefficients des B-splines
    
    # Fonction objectif
    residuals = ytab - env_array @ alpha
    objective = cp.Minimize(rhotau(residuals, tau))
    
    constraints = []
    
    # Contraintes de monotonie via la dérivée (constante sur chaque intervalle)
    for i in range(kn):
        if monot[i] != 0:
            # Dérivée sur l'intervalle i = somme pondérée des dérivées constantes
            deriv_sum = alpha @ Der1_array[:, i]
            
            # Appliquer contrainte sur la constante
            deriv_constraints = apply_val_constraints(deriv_sum, monot[i])
            constraints.extend(deriv_constraints)
    
    # Alternative: contraindre directement la fonction (plus fort)
    # Mais les contraintes sur la dérivée sont plus naturelles pour la monotonie
    
    # Résolution
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=False, solver=solver)
    
    if alpha.value is None:
        warnings.warn("L'optimisation n'a pas convergé, essayer un autre solveur")
        return None
    
    print(f"Statut: {prob.status}, Valeur objectif: {prob.value:.4f}")
    
    # Construction de la spline résultante
    l_end = np.min(knots)
    r_end = np.max(knots)
    s = np.concatenate([[l_end] * degree, knots, [r_end] * degree])
    polyn = BSpline(s, alpha.value, degree)
    
    return polyn

def SplineQuadraticQuant(xtab, ytab, knots, tau, monot=0, cv=0, solver='CLARABEL', weight=None):

    """
    Régression quantile avec B-splines de degré 2 et contraintes de forme.
    
    Les splines quadratiques sont des fonctions continues, dérivables une fois,
    et quadratiques sur chaque intervalle entre les nœuds.
    
    Parameters
    ----------
    xtab, ytab : array-like
        Données x et y
    knots : int or list
        Nombre de nœuds ou liste des nœuds
    tau : float
        Paramètre quantile (entre 0 et 1)
    monot : int or list, default=0
        Contrainte de monotonie (+1 croissant, -1 décroissant, 0 aucune)
    cv : int or list, default=0
        Contrainte de convexité (+1 convexe, -1 concave, 0 aucune)
    solver : str, default='CLARABEL'
        Solveur CVXPY à utiliser
    weight : array-like, optional
        Poids des observations
        
    Returns
    -------
    polyn : BSpline object
        Fonction spline résultante (degré 2)
    
    Notes
    -----
    -Pour une spline quadratique, la monotonie sur chaque intervalle est
    implémentée par des contraintes suffisantes et nécessaires aux noeuds
    de la dérivée affine par morceaux.
    -La convexité est contrôlée par le signe d'un point quelconque de
    chaque intervalle (la dérivée seconde est constante par morceaux).
    L'ensemble des contraintes est un problème linéaire.
    
    Examples
    --------
    >>> import numpy as np
    >>> from BsplineQuantRegpy import SplineQuadraticQuant
    >>> x = np.linspace(0, 1, 50)
    >>> y = 2*x**2 + 0.1*np.random.randn(50)
    >>> knots = np.quantile(x, np.linspace(0, 1, 6))
    >>> result = SplineQuadraticQuant(x, y, knots, tau=0.5, cv=1)
    """
    
    if weight is None:
        weight = np.ones(len(xtab))
    
    # Tri des données
    sort_idx = np.argsort(xtab)
    xtab = np.array(xtab)[sort_idx]
    ytab = np.array(ytab)[sort_idx]
    weight = np.array(weight)[sort_idx]
    
    n = len(xtab)
    
    # Gestion des nœuds
    if isinstance(knots, int):
        kn = knots - 1
        knots = np.quantile(xtab, np.linspace(0, 1, kn + 1))
    
    kn = len(knots) - 1
    degree = 2
    N = kn + degree  # Nombre de fonctions de base
    
    # Gestion des contraintes
    if isinstance(monot, int):
        monot = monot * np.ones(kn)
    else:
        monot = np.array(monot)
    
    if np.isscalar(cv):
        cv_array = cv * np.ones(kn)      # Contraintes par intervalle pour la convexité
        cv_knots = cv * np.ones(kn + 1)  # Contraintes aux nœuds
    else:
        cv_array = np.array(cv)
        if len(cv_array) == kn + 1:
            cv_knots = cv_array
            cv_array = cv_array[:-1]
        else:
            cv_array = cv_array
            cv_knots = np.concatenate([cv_array, [0]])
    
    print(f"=== Régression quantile avec splines quadratiques (degré 2) ===")
    print(f"Nœuds: {kn}, Fonctions de base: {N}")
    print(f"Contraintes monotonie (dérivée 1): {monot}")
    print(f"Contraintes convexité (dérivée 2) - intervalles: {cv_array}")
    print(f"Contraintes convexité (dérivée 2) - nœuds: {cv_knots}")
    
    # Construction des B-splines quadratiques
    List_Bsplines, Der1_array, Der2_array =  build_bsplines_and_deriv(knots,degree)
    
    # Matrice de design
    env_array = np.zeros((n, N))
    for j in range(N):
        env_array[:, j] = List_Bsplines[j](xtab)
    
    # Variables d'optimisation
    alpha = cp.Variable(N)  # Coefficients des B-splines
    
    # Fonction objectif
    residuals = ytab - env_array @ alpha
    objective = cp.Minimize(rhotau(residuals, tau))
    
    constraints = []
    
    # Contraintes de monotonie (sur la dérivée première, linéaire)
    for i in range(kn): #tous les intervallesq
        if monot[i] != 0:
            # Coefficients de la dérivée première sur cet intervalle
            coeffs_sum = alpha @ Der1_array[:,  i]  # [a, b] pour a*u + b
            
            # Appliquer contraintes linéaires
            lin_constraints = apply_val_constraints(coeffs_sum, monot[i])
            constraints.extend(lin_constraints)
    
    # Contraintes de convexité (sur la dérivée seconde, constante)
    for i in range(kn):
        if cv_array[i] != 0:
            # La dérivée seconde est constante = 2*a (où a est le coeff de u^2)
            # Mais on peut utiliser directement les valeurs aux nœuds
            # Pour chaque intervalle, on peut aussi contraindre les dérivées secondes aux nœuds
            
            # Option 1: Contraindre aux nœuds (plus simple)
            # On le fait dans la boucle suivante
            pass
    
    # Contraintes de convexité sur les itervalles (derivee seconde constante par morceaux
    for j in range(kn):
        if cv_knots[j] != 0:
            # La dérivée seconde au nœud j
            const_constraints = apply_val_constraints(Der2_array[:, j] @ alpha, cv_knots[j])
            constraints.extend(const_constraints)
    
    # Résolution
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=False, solver=solver)
    
    if alpha.value is None:
        warnings.warn("L'optimisation n'a pas convergé, essayer un autre solveur")
        return None
    
    print(f"Statut: {prob.status}, Valeur objectif: {prob.value:.4f}")
    
    # Construction de la spline résultante
    l_end = np.min(knots)
    r_end = np.max(knots)
    s = np.concatenate([[l_end] * degree, knots, [r_end] * degree])
    polyn = BSpline(s, alpha.value, degree)
    
    return polyn

def SplineCubicQuant(xtab, ytab, knots, tau, monot=0, cv=0, der3=0, 
                                   solver='CLARABEL', weight=None):
    

    """
    Régression quantile avec B-splines cubiques et contraintes de forme.
    Les splines cubiques sont des fonctions continues, deux fois dérivables,
    et cubiques sur chaque intervalle entre les nœuds.    
    Parameters
    ----------
    xtab, ytab : array-like
        Données x et y
    knots : int or list
        Nombre de nœuds ou liste des nœuds
    tau : float
        Paramètre quantile
    monot : int or list, default=0
        Contrainte de monotonie (+1 croissant, -1 décroissant, 0 aucune)
    cv : int or list, default=0
        Contrainte de convexité (+1 convexe, -1 concave, 0 aucune)
    der3 : int or list, default=0
        Contrainte sur la dérivée troisième (+1 positive, -1 négative, 0 aucune)
    solver : str, default='CLARABEL'
        Solveur CVXPY à utiliser
    weight : array-like, optional
        Poids des observations
        
    Returns
    -------
    polyn : BSpline object
        Fonction spline résultante (degré 3)
    
    Notes
    -----
    - Les contraintes de monotonie sont implémentées via la caractérisation de Karlin-Studden (1966)
    du signe des polynômes positifs de degré 2.
    - Les contraintes de convexité sont implémentéee par le signe de la dérivée seconde affine
    par morceaux aux noeud.
    - Les contraintes de dérivée troisième (constante par morceaux) sont implémentées par
    le signe d'un point quelconque de chque intervalle.
    
    Exemples
    --------
    >>> import numpy as np
    >>> from BsplineQuantRegpy import SplineCubicQuant
    >>> x = np.linspace(0, 1, 50)
    >>> y = 3*x + 0.1*np.random.randn(50)
    >>> knots = np.quantile(x, np.linspace(0, 1, 6))
    >>> result = SplineCubicQuant(x, y, knots, tau=0.5, monot=1, cv=1)
    """
    
    if weight is None:
        weight = np.ones(len(xtab))
    
    # Tri des données
    sort_idx = np.argsort(xtab)
    xtab = np.array(xtab)[sort_idx]
    ytab = np.array(ytab)[sort_idx]
    weight = np.array(weight)[sort_idx]
    
    n = len(xtab)
    
    if isinstance(knots, int):
        kn = knots - 1
        knots = np.quantile(xtab, np.linspace(0, 1, kn + 1))
    
    kn = len(knots) - 1
    degree = 3
    N = kn + degree
    
    print(f"Degré: {degree}, Nœuds: {kn}, Fonctions de base: {N}")
    
    # Gestion des contraintes
    if isinstance(monot, int):
        monot = monot * np.ones(kn)
    else:
        monot = np.array(monot)
    print(f"Contraintes monotonie: {monot}")
    
    if np.isscalar(cv):
        cv = cv * np.ones(kn + 1)
    else:
        cv = np.array(cv)
    print(f"Contraintes convexité: {cv}")
    
    if isinstance(der3, int):
        der3 = der3 * np.ones(kn)
    else:
        der3 = np.array(der3)
    print(f"Contraintes dérivée 3: {der3}")
    
    # === CONSTRUCTION DES B-SPLINES ===
    # Construction des B-splines avec les dérivées
    l_end = np.min(knots)
    r_end = np.max(knots)
    s = np.concatenate([[l_end] * degree, knots, [r_end] * degree])
    
    List_Bsplines, Der1_array ,    Der2_array, Der3_array = build_bsplines_and_deriv(knots,degree)
    # === MATRICE DE DESIGN ===
    env_array = np.zeros((n, N))
    for j in range(N):
        env_array[:, j] = List_Bsplines[j](xtab)
    
    # === OPTIMISATION ===
    alpha = cp.Variable(N)
    z = cp.Variable(kn)  # Variables auxiliaires pour les contraintes
    
    residuals = ytab - env_array @ alpha
    objective = cp.Minimize(rhotau(residuals, tau))
    
    constraints = []
    
    # === CONTRAINTES DE MONOTONIE ===
    # Utilise la même approche matricielle que les quartiques
    for i in range(kn):
        if monot[i] != 0:
            # Coefficients de la dérivée première sur l'intervalle i
            # Der1_array[:, :, i] est (N, 3) : [a, b, c] pour a*u^2 + b*u + c
            coeffs_sum = alpha @ Der1_array[:, :, i]
            
            # Appliquer les contraintes de Karlin pour quadratique (comme pour les quartiques)
            quad_constraints = apply_karlin_constraints_quadratic(coeffs_sum, monot[i])
            constraints.extend(quad_constraints)
    
    # === CONTRAINTES DE CONVEXITÉ ===
    for j in range(kn + 1):
        if cv[j] != 0:
            coeffs_sum=Der2_array[:, j] @ alpha
            cv_constraints = apply_val_constraints(coeffs_sum, cv[j])
            constraints.extend(cv_constraints)
    
#            constraints.append(cv[j] * (Der2_array[:, j] @ alpha) >= 0)
    
    # === CONTRAINTES SUR DÉRIVÉE TROISIÈME ===
    for i in range(kn):
        if der3[i] != 0:
            coeffs_sum=Der3_array[:, i] @ alpha
            d3_constraints = apply_val_constraints(coeffs_sum, der3[i])
            constraints.extend(d3_constraints)
    
            #constraints.append(der3[i] * (Der3_array[:, i] @ alpha) >= 0)
    
    # === RÉSOLUTION ===
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=False, solver=solver)
    
    if alpha.value is None:
        warnings.warn("L'optimisation n'a pas convergé")
        return None
    
    print(f"Statut: {prob.status}, Valeur objectif: {prob.value:.4f}")
    
    # Construction de la spline résultante
    polyn = BSpline(s, alpha.value, degree)
    
    return polyn
    
    # Der3_array: dérivée troisième (constante par intervalle)
    Der3_array = np.zeros((N, kn))
    
    # Création des B-splines de base
    for j in range(N):
        coefs = np.zeros(N)
        coefs[j] = 1
        spline_j = BSpline(s, coefs, degree)
        List_Bsplines.append(spline_j)
        
        # Convertir en PPoly pour obtenir les coefficients
        ppoly = PPoly.from_spline(spline_j)
        ppoly_der1 = ppoly.derivative(1)
        ppoly_der2 = ppoly.derivative(2)
        ppoly_der3 = ppoly.derivative(3)
        
        # Pour chaque intervalle
        for l in range(0, degree + 1):
            nu = j - l + degree
            if (nu >= degree) and (nu < N):
                t_k, t_k1 = s[nu], s[nu + 1]
                h = t_k1 - t_k
                
                # Coefficients de la dérivée première dans la base locale
                # ppoly_der1.c[:, nu] = [c0, c1, c2] pour c0 + c1*(x-tk) + c2*(x-tk)^2
                F1 = ppoly_der1.c[:, nu]
                
                # Normalisation en u = (x-tk)/h
                # f'(x) = c0 + c1*h*u + c2*h^2*u^2
                # Coefficients dans [u^2, u, 1] : [c2*h^2, c1*h, c0]
                Der1_array[j, :, nu - degree] = np.array([F1[2] * h**2, F1[1] * h, F1[0]])
        
        # Dérivée seconde aux nœuds (pour convexité)
        Der2_array[j, :] = ppoly_der2(knots)
        
        # Dérivée troisième aux nœuds (constante par intervalle)
        for i in range(kn):
            x_mid = (knots[i] + knots[i+1]) / 2
            Der3_array[j, i] = ppoly_der3(x_mid)
    
    # === MATRICE DE DESIGN ===
    env_array = np.zeros((n, N))
    for j in range(N):
        env_array[:, j] = List_Bsplines[j](xtab)
    
    # === OPTIMISATION ===
    alpha = cp.Variable(N)
    z = cp.Variable(kn)  # Variables auxiliaires pour les contraintes
    
    residuals = ytab - env_array @ alpha
    objective = cp.Minimize(rhotau(residuals, tau))
    
    constraints = []
    
    # === CONTRAINTES DE MONOTONIE ===
    # Utilise la même approche matricielle que les quartiques
    for i in range(kn):
        if monot[i] != 0:
            # Coefficients de la dérivée première sur l'intervalle i
            # Der1_array[:, :, i] est (N, 3) : [a, b, c] pour a*u^2 + b*u + c
            coeffs_sum = alpha @ Der1_array[:, :, i]
            
            # Appliquer les contraintes de Karlin pour quadratique (comme pour les quartiques)
            quad_constraints = apply_karlin_constraints_quadratic(coeffs_sum, monot[i])
            constraints.extend(quad_constraints)
    
    # === CONTRAINTES DE CONVEXITÉ ===
    for j in range(kn + 1):
        if cv[j] != 0:
            constraints.append(cv[j] * (Der2_array[:, j] @ alpha) >= 0)
    
    # === CONTRAINTES SUR DÉRIVÉE TROISIÈME ===
    for i in range(kn):
        if der3[i] != 0:
            constraints.append(der3[i] * (Der3_array[:, i] @ alpha) >= 0)
    
    # === RÉSOLUTION ===
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=False, solver=solver)
    
    if alpha.value is None:
        warnings.warn("L'optimisation n'a pas convergé")
        return None
    
    print(f"Statut: {prob.status}, Valeur objectif: {prob.value:.4f}")
    
    # Construction de la spline résultante
    polyn = BSpline(s, alpha.value, degree)
    
    return polyn

def SplineQuarticQuant(xtab, ytab, knots, tau, monot, cv, der3=None, solver='CLARABEL', weight=None):
    """
    Régression quantile avec B-splines de degré 4 et contraintes de forme.
    
    Les splines quartiques sont des fonctions continues, trois fois dérivables,
    et quartiques sur chaque intervalle entre les nœuds.
    
    Parameters
    ----------
    xtab, ytab : array-like
        Données x et y
    knots : int or list
        Nombre de nœuds ou liste des nœuds
    tau : float
        Paramètre quantile
    monot : int or list
        Contrainte de monotonie (+1 croissant, -1 décroissant, 0 aucune)
    cv : int or list  
        Contrainte de convexité (+1 convexe, -1 concave, 0 aucune)
    der3 : int or list, optional
        Contrainte sur la dérivée troisième (+1 positive, -1 négative, 0 aucune)
    solver : str, default='CLARABEL'
        Solveur CVXPY à utiliser
    weight : array-like, optional
        Poids des observations
        
    Returns
    -------
    polyn : BSpline object
        Fonction spline résultante (degré 4)
    
    Notes
    -----
    -Les contraintes monotones (resp. convexes) sont implémentées
    via la caractérisation de Karlin-Studden (1966) pour les polynômes
    positifs de degré 3 (resp degré 2). Le problème d'optimisation est formulé comme un problème
    de programmation conique du second ordre (SOCP) et résolu avec CVXPY.

    - La dérivée troisième étant affine par morceaux, les contraintes sont
    implémentées aux noeuds (problèmes linéaire).
    
    Examples
    --------
    >>> import numpy as np
    >>> from BsplineQuantRegpy import SplineQuarticQuant
    >>> x = np.linspace(0, 1, 50)
    >>> y = 4*x**3 + 0.1*np.random.randn(50)
    >>> knots = np.quantile(x, np.linspace(0, 1, 6))
    >>> result = SplineQuarticQuant(x, y, knots, tau=0.5, monot=1, cv=1)
    """
    
    """
    Régression quantile avec B-splines de degré 4 et contraintes de forme
    incluant la dérivée troisième
    
    Parameters:
    -----------
    xtab, ytab : array-like
        Données x et y
    knots : int or list
        Nombre de nœuds ou liste des nœuds
    tau : float
        Paramètre quantile
    monot : int or list
        Contrainte de monotonie (+1 croissant, -1 décroissant, 0 aucune)
    cv : int or list  
        Contrainte de convexité (+1 convexe, -1 concave, 0 aucune)
    der3 : int or list, optional
        Contrainte sur la dérivée troisième (+1 croissante, -1 décroissante, 0 aucune)
    solver : str
        Solveur CVXPY à utiliser
    weight : array-like, optional
        Poids des observations

    Notes
    -----
    Les contraintes monotones (resp. convexes) sont implémentées
    via la caractérisation de Karlin-Studden (1966) pour les polynômes
    positifs de degré 3 (resp degré 2). Le problème d'optimisation est formulé comme un problème
    de programmation conique du second ordre (SOCP) et résolu avec CVXPY.
    Returns:
    --------
    polyn : BSpline object
        Fonction spline résultante
    """
    
    if weight is None:
        weight = np.ones(len(xtab))
    
    # Tri des données
    sort_idx = np.argsort(xtab)
    xtab = np.array(xtab)[sort_idx]
    ytab = np.array(ytab)[sort_idx]
    weight = np.array(weight)[sort_idx]
    
    n = len(xtab)
    
    if isinstance(knots, int):
        kn = knots - 1
        knots = np.quantile(xtab, np.linspace(0, 1, kn + 1))
    
    kn = len(knots) - 1
    degree = 4
    N = kn + degree  # Nombre de fonctions de base
    
    # Gestion des contraintes
    if isinstance(monot, int):
        monot = monot * np.ones(kn)
    else:
        monot = np.array(monot)
    
    if np.isscalar(cv):
        cv_array = cv * np.ones(kn)  # Contraintes par intervalle
        cv_knots = cv * np.ones(kn + 1)  # Contraintes aux nœuds
    else:
        cv_array = np.array(cv)
        # Si cv a kn+1 éléments, les premiers kn sont pour les intervalles
        if len(cv_array) == kn + 1:
            cv_knots = cv_array
            cv_array = cv_array[:-1]
        else:
            cv_array = cv_array
            cv_knots = np.concatenate([cv_array, [0]])
    
    # Gestion des contraintes de dérivée troisième
    if der3 is None:
        der3 = np.zeros(kn+1)
    elif np.isscalar(der3):
        der3 = der3 * np.ones(kn+1)
    elif len(der3)<(kn+1):
        der3 = np.array(der3+[0]*(kn+1-len(der3)))
    else:
        der3 = np.array(der3)
    
    print(f"Degré: {degree}, Nœuds: {kn}, Fonctions de base: {N}")
    print(f"Contraintes monotonie: {monot}")
    print(f"Contraintes convexité (intervalles): {cv_array}")
    print(f"Contraintes convexité (nœuds): {cv_knots}")
    print(f"Contraintes dérivée 3e: {der3}")
    
    # Construction des B-splines avec dérivée troisième
    List_Bsplines, Der1_array, Der2_array,Der3_array = build_bsplines_and_deriv(knots, degree)
    # Matrice de design
    env_array = np.zeros((n, N))
    for j in range(N):
        env_array[:, j] = List_Bsplines[j](xtab)
    
    # Variables d'optimisation
    alpha = cp.Variable(N)  # Coefficients des B-splines
    
    # Fonction objectif
    residuals = ytab - env_array @ alpha
    objective = cp.Minimize(rhotau(residuals, tau))
    
    constraints = []
    
    # Contraintes de monotonie (sur la dérivée première, cubique)
    for i in range(kn):
        if monot[i] != 0:
            # Coefficients de la dérivée première sur cet intervalle
            coeffs_sum = alpha @ Der1_array[:, :, i]
            
            # Appliquer contraintes de Karlin pour cubique
            karlin_constraints = apply_karlin_constraints_cubic(coeffs_sum, monot[i])
            constraints.extend(karlin_constraints)
    
    # Contraintes de convexité (sur la dérivée seconde, quadratique)
    for i in range(kn):
        if cv_array[i] != 0:
            # Coefficients de la dérivée seconde sur cet intervalle
            coeffs_sum2 = alpha @ Der2_array[:, :, i]
            
            # Appliquer contraintes de Karlin pour quadratique
            quad_constraints = apply_karlin_constraints_quadratic(coeffs_sum2, cv_array[i])
            constraints.extend(quad_constraints)
    
    # Contraintes sur la dérivée troisième (linéaire par morceau)
    for i in range(kn+1):
        if der3[i] != 0:
            # Coefficients de la dérivée troisième sur cet intervalle
            coeffs_sum = alpha @ Der3_array[:, i]
            
            # Appliquer contraintes linéaires à chaque noed
            #lin_constraints = apply_linear_constraints(coeffs_sum, der3[i])
            val3_constraints = apply_val_constraints(coeffs_sum, der3[i])
            constraints.extend(val3_constraints)
    
    # Contraintes de convexité aux nœuds
    #for j in range(kn + 1):
    #    if cv_knots[j] != 0:
    #        constraints.append(cv_knots[j] * (con_array[j, :] @ alpha) >= 0)
    
    # Résolution
    prob = cp.Problem(objective, constraints)
    prob.solve(verbose=False, solver=solver)
    
    if alpha.value is None:
        warnings.warn("L'optimisation n'a pas convergé, essayer un autre solveur")
        return None
    
    print(f"Statut: {prob.status}, Valeur objectif: {prob.value:.4f}")
    
    # Construction de la spline résultante
    l_end = np.min(knots)
    r_end = np.max(knots)
    s = np.concatenate([[l_end] * degree, knots, [r_end] * degree])
    polyn = BSpline(s, alpha.value, degree)    
    return polyn

def quantile_spline(xtab, ytab, knots, tau, degree=3, monot=0, cv=0, der3=0, solver='CLARABEL',weight=None):  

    """
    Cette fonction permet d'appeler la régression quantile pour tous les degrés
    de splines (1 à 4) avec une interface unique. Elle redirige vers la fonction
    appropriée selon le degré choisi.
    
    Paramètres
    ----------
    xtab : array-like, shape (n,)
        Variables indépendantes (abscisses). Doivent être dans l'intervalle [0, 1].
    
    ytab : array-like, shape (n,)
        Variables dépendantes (ordonnées).
    
    knots : array-like
        Positions des nœuds pour la base B-spline.
        Si un entier est fourni, il est interprété comme le nombre de nœuds.
    
    tau : float, 0 < tau < 1
        Quantile à estimer. Par exemple:
        - tau = 0.5 : médiane
        - tau = 0.1 : quantile inférieur
        - tau = 0.9 : quantile supérieur
    
    degree : int, default=3
        Degré de la spline :
        - 1 : linéaire (affine par morceaux)
        - 2 : quadratique
        - 3 : cubique
        - 4 : quartique
    
    monot : int ou list, default=0
        Contrainte de monotonie :
        - 1 : fonction croissante
        - -1 : fonction décroissante
        - 0 : aucune contrainte
        Si une liste est fournie, chaque élément correspond à un intervalle.
    
    cv : int ou list, default=0
        Contrainte de convexité :
        - 1 : fonction convexe
        - -1 : fonction concave
        - 0 : aucune contrainte
        Si une liste est fournie, chaque élément correspond à un intervalle.
    
    der3 : int ou list, default=0
        Contrainte sur la dérivée troisième :
        - 1 : dérivée troisième positive
        - -1 : dérivée troisième négative
        - 0 : aucune contrainte
        (Uniquement pour les splines de degré 3 et 4)
    
    solver : str, default='CLARABEL'
        Solveur CVXPY à utiliser. Options disponibles :
        - 'CLARABEL' (recommandé, gratuit)
        - 'ECOS'
        - 'SCS'
        - 'GUROBI' (payant, nécessite une licence)
        - 'MOSEK' (payant, nécessite une licence)
        - 'CVXOPT'
    
    weight : array-like, optional
        Poids des observations pour la régression pondérée.
        Si None, tous les poids sont égaux à 1.
    Raises
    ------
    ValueError
        Si le degré n'est pas compris entre 1 et 4.
    
    Returns
    -------
    callable
        Fonction spline résultante. Elle peut être évaluée en tout point x :
        >>> y_eval = spline_result(x_eval)
    
       
    Exemples
    --------
    >>> import numpy as np
    >>> from BsplineQuantRegpy import quantile_spline
    >>> 
    >>> # Générer des données
    >>> x = np.linspace(0, 1, 100)
    >>> y = 2*x + 0.2*np.sin(10*np.pi*x) + 0.05*np.random.randn(100)
    >>> knots = np.quantile(x, np.linspace(0, 1, 11))
    >>> 
    >>> # Régression avec spline cubique et contrainte croissante
    >>> result = quantile_spline(x, y, knots, tau=0.5, degree=3, monot=1)
    >>> 
    >>> # Régression avec spline quadratique et contrainte convexe
    >>> result = quantile_spline(x, y, knots, tau=0.5, degree=2, cv=1)
    >>> 
    >>> # Régression avec spline quartique et toutes les contraintes
    >>> result = quantile_spline(x, y, knots, tau=0.5, degree=4, 
    ...                          monot=1, cv=1, der3=1)
    >>> 
    >>> # Évaluer la spline
    >>> x_eval = np.linspace(0, 1, 200)
    >>> y_eval = result(x_eval)
    
    Notes
    -----
    Les contraintes de monotonie pour les degrés 3 et 4 sont implémentées
    via la caractérisation de Karlin-Studden (1966) pour les polynômes
    positifs de degrés 2 et 3, ce sont des contraintes quadratiques.
    Les autres contraintes sont lineaires.
    Le problème d'optimisation est formulé comme un problème
    de programmation conique du second ordre (SOCP) et résolu avec CVXPY.
    
    Références
    ----------
    Karlin, S., & Studden, W.J. (1966). Tchebycheff Systems:
    With Applications in Analysis and Statistics. Interscience Publishers.
    
    He, X., & Shi, P. (1998). Monotone B-spline smoothing.
    Journal of the American Statistical Association, 93(442), 643-650.

    Abbes, A. (2025). Quantile regression with cubic polynomial splines 
    under shape constraints with applications. 
    doi:10.5281/zenodo.17427913
    See Also
    --------
    SplineLinearQuant, SplineQuadraticQuant, SplineCubicQuant, SplineQuarticQuant

    statsmodels.regression.quantile_regression.QuantReg (Python)
    
    BsplineQuantReg (R) : https://cran.r-project.org/package=BsplineQuantReg
    cobs (R) : https://cran.r-project.org/package=cobs
    
    
    """
    
    if degree == 1:
        return SplineLinearQuant(xtab, ytab=ytab, knots=knots, tau=tau, 
                                 monot=monot, solver=solver, weight=weight)
    elif degree == 2:
        return SplineQuadraticQuant(xtab, ytab=ytab, knots=knots, tau=tau, 
                                    monot=monot, cv=cv, solver=solver, weight=weight)
    elif degree == 3:
        return SplineCubicQuant(xtab, ytab=ytab, knots=knots, tau=tau, 
                                monot=monot, cv=cv, der3=der3, 
                                solver=solver, weight=weight)
    elif degree == 4:
        return SplineQuarticQuant(xtab, ytab=ytab, knots=knots, tau=tau, 
                                  monot=monot, cv=cv, der3=der3, 
                                  solver=solver, weight=weight)
    else:
        raise ValueError(f"Le degré doit être compris entre 1 et 4. Reçu: {degree}")


    if degree==1:
           return SplineLinearQuant(xtab, ytab=ytab, knots=knots, tau=tau, monot=monot, solver=solver, weight=weight)
    if degree==2:
           return SplineQuadraticQuant(xtab, ytab=ytab, knots=knots, tau=tau, monot=monot, cv=cv, solver=solver, weight=weight)
    if degree==3:
           return SplineCubicQuant(xtab, ytab=ytab, knots=knots, tau=tau, monot=monot, cv=cv,der3=der3, solver=solver, weight=weight)
    if degree==4:
           return SplineQuarticQuant(xtab, ytab=ytab, knots=knots, tau=tau, monot=monot, cv=cv, der3=der3, solver=solver, weight=weight)

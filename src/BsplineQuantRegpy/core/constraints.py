#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alexandre Abbes"
__copyright__ = "Copyright 2026, Alexandre Adel Abbes"
__license__ = "GPL"
__version__ = "1.0.1"

import numpy as np
import cvxpy as cp

def apply_karlin_constraints_cubic(coeffs_cubic, sign=1):
    """
    Applique les contraintes de Karlin pour un polynôme cubique (dérivée première)
    selon le théorème 3 de l'article
    
    sign > 0 : p(u) >= 0 sur [0,1]
    sign < 0 : p(u) <= 0 sur [0,1]  (soit -p(u) >= 0)
    """
    a, b, c, d = coeffs_cubic
    
    constraints = []
    
    if sign > 0:
        # p(u) >= 0
        coeffs = (a, b, c, d)
        final_sign = 1
    else:
        # p(u) <= 0  <=>  -p(u) >= 0
        coeffs = (-a, -b, -c, -d)  # Les coefficients de -p(u)
        final_sign = 1  # On veut -p(u) >= 0, donc signe positif
    
    a1, b1, c1, d1 = coeffs
    
    # Variables auxiliaires selon le théorème 3
    y0 = cp.Variable()
    y1 = cp.Variable()
    y2 = cp.Variable()
    x0 = cp.Variable()
    x1 = cp.Variable()
    x2 = cp.Variable()
    
    # Équations (6a)-(6d) pour le polynôme (p ou -p selon le signe)
    constraints.append(d1 == y0)
    constraints.append(c1 == 2*y1 + x0 - y0)
    constraints.append(b1 == y2 + 2*x1 - 2*y1)
    constraints.append(a1 == x2 - y2)
    
    # Contraintes de cône second-order (6e)-(6f)
    constraints.append(cp.SOC(x0 + x2, cp.hstack([x0 - x2, 2*x1])))
    constraints.append(cp.SOC(y0 + y2, cp.hstack([y0 - y2, 2*y1])))
    
    # Conditions aux bornes (pour le polynôme transformé)
    constraints.append(d1 >= 0)
    constraints.append(a1 + b1 + c1 + d1 >= 0)
    
    return constraints

def apply_karlin_constraints_cubic_bak(coeffs_cubic, monot_sign=1):
    """
    Applique les contraintes de Karlin pour un polynôme cubique (dérivée première)
    selon le théorème 3 de l'article
    """
    # coeffs_cubic = [a, b, c, d] pour a*u^3 + b*u^2 + c*u + d
    a, b, c, d = coeffs_cubic
    
    # Variables auxiliaires selon le théorème 3
    y0 = cp.Variable()
    y1 = cp.Variable()
    y2 = cp.Variable()
    x0 = cp.Variable()
    x1 = cp.Variable()
    x2 = cp.Variable()
    
    constraints = []
    
    # Équations (6a)-(6d) adaptées pour un polynôme cubique
    constraints.append(d == y0)
    constraints.append(c == 2*y1 + x0 - y0)
    constraints.append(b == y2 + 2*x1 - 2*y1)
    constraints.append(a == x2 - y2)
    
    # Contraintes de cône second-order (6e)-(6f)
    constraints.append(cp.SOC(x0 + x2, cp.hstack([x0 - x2, 2*x1])))
    constraints.append(cp.SOC(y0 + y2, cp.hstack([y0 - y2, 2*y1])))
    
    # Pour la monotonie: si monot_sign > 0, p(u) >= 0 pour u ∈ [0,1]
    # si monot_sign < 0, -p(u) >= 0 pour u ∈ [0,1]
    if monot_sign > 0:
        # p(0) = d >= 0 et p(1) = a + b + c + d >= 0
        constraints.append(d >= 0)
        constraints.append(a + b + c + d >= 0)
    elif monot_sign < 0:
        # -p(0) = -d >= 0 et -p(1) = -(a + b + c + d) >= 0
        constraints.append(-d >= 0)
        constraints.append(-(a + b + c + d) >= 0)
    
    return constraints

def apply_karlin_constraints_quadratic(coeffs_quad, const_sign=1):
    """
    Applique les contraintes de Karlin pour un polynôme quadratique (dérivée seconde)
    selon la Proposition 5 du document PDF
    """
    # coeffs_quad = [a, b, c] pour a*u^2 + b*u + c
    # Note: selon la notation du PDF: p(x) = p0 + p1*x + p2*x^2
    # Donc: p0 = c, p1 = b, p2 = a
    p0, p1, p2 = coeffs_quad[2], coeffs_quad[1], coeffs_quad[0]
    #Karlin's matrices
    K1 = np.array([[1, 0, -1, -1],
                   [0, 1, 0, -1]])
    K2 = np.array([1, 0, 1, 1])
    
    constraints = []
    
    if const_sign != 0:
        # Variable auxiliaire z0 >= 0
        z0 = cp.Variable()
        constraints.append(z0 >= 0)
        P=const_sign*np.array([p0,p1,p2,const_sign*z0])
        x1 =    K2@P
        [x2,x3]=K1@P
            
        # Pour cv_sign > 0: p(x) >= 0 sur [0,1]
        #if cv_sign > 0:
            # Selon Proposition 5: (p0 + p2 + z0, p0 - p2 - z0, p1 - z0) ∈ Q3
            #x1 = p0 + p2 + z0
            #x2 = p0 - p2 - z0
            #x3 = p1 - z0
        #    P=cv_sign*np.array([p0,p1,p2,cv_sign*z0])
        #    x1 =    K2@P
        #    [x2,x3]=K1@P
            
            # Contrainte SOC: x1 >= ||(x2, x3)||_2
        constraints.append(cp.SOC(x1, cp.hstack([x2, x3])))  
    
    return constraints


def apply_val_constraints(const, sign=1):
    """
    Applique les contraintes pour un polynôme linéaire (dérivée troisième)
    p(u) = a*u + b >= 0 (ou <= 0) pour u ∈ [0,1]
    """
    constraints = []
    
    if sign > 0:
        # p(u) >= 0 sur [0,1] ↔ min(p(0), p(1)) >= 0
        constraints.append(const >= 0)      # p(0) >= 0
        #constraints.append(a + b >= 0)  # p(1) >= 0
    elif sign < 0:
        # p(u) <= 0 sur [0,1] ↔ max(p(0), p(1)) <= 0
        constraints.append(const <= 0)      # p(0) <= 0
        #constraints.append(a + b <= 0)  # p(1) <= 0
    
    return constraints

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alexandre Abbes"
__copyright__ = "Copyright 2026, Alexandre Adel Abbes"
__license__ = "GPL"
__version__ = "1.0.1"

import numpy as np
from scipy.interpolate import BSpline, PPoly


def build_bsplines_and_deriv(knots, degree):
    """
    Returns the derivatives of the B-spline according to the degree.
    
    For linear and constant derivatives returns a vector of values at knots.
    When derivatives are splines of degree 2 or 3, returns a matrix
    of normalised coefficients on the local power basis, i.e. the PP-form 
    of the derivative of the spline prepared for applying Karlin-Studden constraints.
    
    Parameters
    ----------
    knots : array-like
        Knots positions
    degree : int
        Degree of the spline (1, 2, 3, or 4)
    
    Returns
    -------
    List_Bsplines : list
        List of B-spline basis functions
    Der1_array : ndarray
        First derivative coefficients or values
    Der2_array : ndarray, optional
        Second derivative coefficients or values
    Der3_array : ndarray, optional
        Third derivative coefficients or values
    """
    kn = len(knots) - 1
    N = kn + degree
    l_end = np.min(knots)
    r_end = np.max(knots)
    
    # Extension de la séquence de nœuds
    s = np.concatenate([[l_end] * degree, knots, [r_end] * degree])
    
    List_Bsplines = []
    
    # Allocation des tableaux selon le degré
    if degree == 4:
        Der1_array = np.zeros((N, degree, kn))
        Der2_array = np.zeros((N, degree - 1, kn))
        Der3_array = np.zeros((N, kn + 1))
    elif degree == 3:
        Der1_array = np.zeros((N, degree, kn))
        Der2_array = np.zeros((N, kn + 1))
        Der3_array = np.zeros((N, kn))
    elif degree == 2:
        Der1_array = np.zeros((N, kn + 1))
        Der2_array = np.zeros((N, kn))
    elif degree == 1:
        Der1_array = np.zeros((N, kn))
    
    # Création des B-splines de base
    for j in range(N):
        coefs = np.zeros(N)
        coefs[j] = 1
        spline_j = BSpline(s, coefs, degree)
        List_Bsplines.append(spline_j)
        
        ppoly = PPoly.from_spline(List_Bsplines[j])
        ppoly_der1 = ppoly.derivative(1)
        
        if degree >= 2:
            ppoly_der2 = ppoly.derivative(2)
            if degree >= 3:
                ppoly_der3 = ppoly.derivative(3)
        
        # Pour chaque intervalle
        for l in range(0, degree + 1):
            nu = j - l + degree
            if (nu >= degree) and (nu < N):
                t_k, t_k1 = s[nu], s[nu + 1]
                h = t_k1 - t_k
                
                F1 = ppoly_der1.c[:, nu]
                
                if degree == 4:
                    # Première dérivée (cubique)
                    B = np.array([h**3, h**2, h, 1])
                    Der1_array[j, :, nu - degree] = B * F1
                    
                    # Deuxième dérivée (quadratique)
                    F2 = ppoly_der2.c[:, nu]
                    B2 = np.array([h**2, h, 1])
                    Der2_array[j, :, nu - degree] = B2 * F2[0:3]
                
                elif degree == 3:
                    # Première dérivée (quadratique)
                    B2 = np.array([h**2, h, 1])
                    Der1_array[j, :, nu - degree] = B2 * F1
        
        # Dérivées aux nœuds
        if degree == 4:
            Der3_array[j, :] = ppoly_der3(knots)
        elif degree == 3:
            Der2_array[j, :] = ppoly_der2(knots)
            Der3_array[j, :] = ppoly_der3(knots[0:kn])
        elif degree == 2:
            Der1_array[j, :] = ppoly_der1(knots)
            Der2_array[j, :] = ppoly_der2(knots[0:kn])
        elif degree == 1:
            Der1_array[j, :] = ppoly_der1(knots[0:kn])
    
    # Retour selon le degré
    if degree == 1:
        return List_Bsplines, Der1_array
    elif degree == 2:
        return List_Bsplines, Der1_array, Der2_array
    else:  # degree >= 3
        return List_Bsplines, Der1_array, Der2_array, Der3_array
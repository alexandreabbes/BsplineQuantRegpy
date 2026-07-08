#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alexandre Abbes"
__copyright__ = "Copyright 2026, Alexandre Adel Abbes"
__license__ = "GPL"
__version__ = "1.0.1"

import numpy as np
from scipy.interpolate import BSpline, PPoly



def build_bsplines_and_deriv(knots,degree):
    """Returns the derivatives of the Bspline according to the degree
    For linear and constant derivatives returns a vector of values at knots.
    When  derivatives are splines of degree 2 or 3, returns a matrix
    of normalised coefficients on the local power basis, i.e. the PP-form of the derivative of the spline
    prepared for applying Karlin-Studden constraints
    """
    kn=len(knots)-1
    N=kn+degree
    l_end = np.min(knots)
    r_end = np.max(knots)
    
    # Traitement des nœuds
    
    # Filtrage des données dans l'intervalle des nœuds
    #mask = (xtab >= np.min(knots))
    #xtab = xtab[mask]
    #ytab = ytab[mask]
    #weight = weight[mask]
    #n = len(xtab)
    
    # Extension de la séquence de nœuds
    s = np.concatenate([[l_end]*degree, knots, [r_end]*degree])
    
    List_Bsplines=[]
    #List_Bsplines_der2=[]
    
    if degree==4:
        Der1_array = np.zeros((N, degree ,kn ))   
        Der2_array = np.zeros((N,degree-1, kn))
        Der3_array = np.zeros((N,kn+1))

    if degree==3:
        Der1_array = np.zeros((N, degree ,kn ))   
        Der2_array = np.zeros((N,kn+1))
        Der3_array = np.zeros((N,kn))
        
    if degree==2:
        Der1_array = np.zeros((N,kn+1))   
        Der2_array = np.zeros((N,kn))

    if degree==1:
        Diff1=np.array([1,0])
        Der1_array = np.zeros((N,kn))   
        
    for j in range(N):
        coefs = np.zeros(N)
        coefs[j] = 1        # j-th Bspline element of the basis 
        spline_j=BSpline(s, coefs,degree)
        List_Bsplines.append(spline_j)
        
        ppoly=PPoly.from_spline(List_Bsplines[j])
        ppoly_der1=ppoly.derivative(1)
        if degree>=2:
            ppoly_der2=ppoly.derivative(2)
            if degree>=3:
                ppoly_der3=ppoly.derivative(3)
        #coeffs_local=ppoly.c    
        for l in range(0,degree+1):
         nu=j-l+degree
         if ((nu>=degree) & (nu <N)):
            t_k, t_k1 = s[nu],s[nu+1]
            h = t_k1 - t_k
        

            #coeffs_local_der = ppoly_der1.c[:, nu]
            
            F1 = ppoly_der1.c[:, nu]
            
            if degree==4:           
                #Scale the local basis from (x-tk)^i to ((x-t_k)/(tk1_tk))^i,
                #First derivative
                B=np.array([h**3,h**2,h,1])
                Der1_array[j, :, nu-degree]= B*F1
                #Second derivative
                F2 = ppoly_der2.c[:, nu] 
                B2=[h**2,h,1]                
                Der2_array[j,:,nu-degree]=B2*F2[0:3]
            if degree==3:
                B2=np.array([h**2,h,1])
                Der1_array[j, :, nu-degree]=B2*F1 #+(t_k)*F2+(t_k)**2/2*F3)
        if degree==4:
            Der3_array[j, :]=ppoly_der3(knots)
        if degree==3:
            Der2_array[j, :]=ppoly_der2(knots)
            Der3_array[j, :]=ppoly_der3(knots[0:kn]) # coefficient de x^3       
        if degree==2:
            Der1_array[j, :]=ppoly_der1(knots)
            Der2_array[j, :]=ppoly_der2(knots[0:kn])
        if degree==1:
            Der1_array[j, :]=ppoly_der1(knots[0:kn])       
   
    if degree==1:
        return List_Bsplines, Der1_array
    if degree==2:
        return List_Bsplines, Der1_array, Der2_array
    if degree>=3:
        return List_Bsplines, Der1_array, Der2_array, Der3_array

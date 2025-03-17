#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 14:31:42 2021

@author: vincentbp
"""

# These will be my library for all helper functions

# Imports
import numpy as np
import time

def vecOfRandPerm(n,N):
    # % Successive random permutation of integers n on a vector of length N.
    # % n : 1 to n inclusive integers to randomly permute
    # % N : length of final vector
    # % EXAMPLE: 
    # % vecOfRandPerm(3,11)
    # % ans =     2     3     1     1     2     3     3     1     2     2     3
    P = np.array([],int);
    for i in range(int(np.ceil(N/n))):
        A = np.random.permutation(n)        
        P = np.block([P, A])
    # Take only N element
    P = P[0:N]
    return P

def reparray(a, n):
    B = list(a) * n
    B = np.array(B)
    B.shape = (n,len(a))
    return B

def movsum(a, n):
#a should be an np.array
    # n is how many before to sum
    if n > 0:
        b = a.cumsum()    
        b[n:] = b[n:] - b[:-n]
    else:
        b = a
    return b

def makeRaster(a,idx,w):
    
    # Create a list of index to be used for the raster
    X = np.tile(np.arange(np.diff(w))+w[0],(len(idx),1));
    Y = X.transpose() + idx
    Y = Y.transpose()
    Y = Y.flatten()
    Y = Y.astype(int)
    
    # Select data to plot as raster
    R = a[Y]
    
    # Reshape into a raster
    R = R.reshape((X.shape[0],X.shape[1]))
    
    return R

def pause(t):
    t0 = time.perf_counter()
    d = time.perf_counter() - t0
    while d < t:
        d = time.perf_counter() - t0
    return

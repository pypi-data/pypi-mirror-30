#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Collection of useful math utils.

Note: Don't import the __init__ for speed.

"""

import uncertainties as uc
from uncertainties.unumpy import matrix

#===============================================================================

def sumq(args):
  """
  Return sum in quadrature.

  >>> sumq([3, 4])
  5.0
  >>> sumq([1, 2, 2])
  3.0

  """
  return sum(x**2 for x in args)**0.5

#===============================================================================

def weighted_average(list_val_weight):
  """
  Given a list of (val,weight) pair, return the weighted average

  >>> weighted_average([(5, 2), (4, 1), (3, 2)])
  4.0

  """
  sum1 = 0.
  sum2 = 0.
  for val,weight in list_val_weight:
    sum1 += val*weight
    sum2 += weight
  return sum1/sum2

#===============================================================================

def covariance_matrix(values, errors, corr):
  """
  Given array of nominal values, errors, and their correlation matrix,
  (all of same dim N) return the covar matrix (N x N).

  Utils for uncertainties.ufloat

  >>> covariance_matrix(
  ...   [3  , 4  , 5  ],
  ...   [0.1, 0.2, 0.3],
  ...   [
  ...     [1, 0.5, 0.2],
  ...     [0.5, 1, 0.3],
  ...     [0.2, 0.3, 1],
  ...   ]
  ... )
  matrix([[0.01 , 0.01 , 0.006],
          [0.01 , 0.04 , 0.018],
          [0.006, 0.018, 0.09 ]])

  """
  acc = uc.correlated_values_norm(zip(values, errors), corr)
  return matrix(uc.covariance_matrix(acc))

#===============================================================================

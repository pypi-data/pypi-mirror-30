#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

More collection of math utils.
These guys need ``pandas`` as dependency.

"""

from __future__ import absolute_import

import pandas as pd
from uncertainties import ufloat, nominal_value, std_dev, correlated_values_norm
from uncertainties.unumpy import matrix
from .. import logger
from .misc import covariance_matrix

#===============================================================================

def weighted_harmonic_average(se, weight=None):
  """
  If weight is not given, each entry in series is of the same weight.
  If it's given, weight should have the same range as series.

  >>> se = pd.Series([3, 4, 12])
  >>> w  = 1, 1, 2
  >>> weighted_harmonic_average(se)
  4.5
  >>> weighted_harmonic_average(se, w)
  5.333...

  Fallback to arith mean if there's zero.

  >>> se = pd.Series([1, 2, 0, 4])
  >>> w  = 1, 1, 2, 2
  >>> weighted_harmonic_average(se) 
  1.75
  >>> weighted_harmonic_average(se, w)
  1.83...

  """
  try:  # optionally
    from scipy.stats import hmean
  except ImportError:  # pragma: no cover
    logger.warning('No scipy.stats.hmean. Use slow definition.')
    hmean = lambda arr: len(arr) / sum(1./x for x in arr)
  if weight is not None:
    assert len(se) == len(weight)
    ## cast weight to Series
    if isinstance(weight, (list, tuple)):
      weight = pd.Series(weight)
  ## make sure of float
  se = se.apply(lambda x: float(nominal_value(x)))

  ## define case 0: Fallback to arimethic mean
  if any(x==0. for x in se.values):
    logger.warning('Found 0 in series, fallback to arith.mean: %s'%se.name)
    if weight is not None:
      return sum(x*y for x,y in zip(se,weight)) / sum(weight)
    return se.sum()/len(se)
  logger.info('Collapsing harmonic mean: %s'%se.name)
  if weight is not None:
    return weight.sum() / sum(1.*w/x for w,x in zip(weight,se.values))
  return hmean(se)

#===============================================================================

def combine_fully_correlated(arr0):
  """
  weight = 1/rerr

  >>> u1 = ufloat(10, 1)
  >>> u2 = ufloat(10, 2)
  >>> combine_fully_correlated([u1, u2])
  10.0+/-1.333...
  >>> combine_fully_correlated([u1])
  10.0+/-1.0
  >>> combine_fully_correlated([None, None])
  nan

  """

  ## Validation: Filter bad out, return immediate if it's one element or none
  arr = [u for u in arr0 if u is not None and not pd.np.isnan(nominal_value(u))]
  N = len(arr)
  if N==0:
    logger.warning('Empty array, return NaN')
    return pd.np.nan
  if N==1: # no need to combine
    return arr[0]

  ##
  w = pd.Series([1/u.rerr for u in arr])
  O = pd.np.ones((N,N))  # square of ones , for completely correlated values
  l = [(nominal_value(u), std_dev(u)) for u in arr]
  se = pd.Series(correlated_values_norm(l, O))
  return (se*w).sum()/w.sum()

#===============================================================================

def combine_uncorrelated(arr0):
  """
  Give array of ufloat, of uncorrelated errors, combine them into one.

  >>> u1 = ufloat(12, 3)
  >>> u2 = ufloat(12, 4)
  >>> print('{:.2f}'.format(combine_uncorrelated([u1, u2])))
  12.00+/-2.40
  >>> combine_uncorrelated([u1])
  12.0+/-3.0
  >>> combine_uncorrelated([])
  nan

  """

  ## Validation: Filter bad out, return immediate if it's one element or none
  arr = [u for u in arr0 if u is not None and not pd.np.isnan(nominal_value(u))]
  N = len(arr)
  if N==0:
    logger.warning('Empty array, return NaN')
    return pd.np.nan
  if N==1: # no need to combine
    return arr[0]

  ## Preparation
  values, errors = zip(*[(nominal_value(u), std_dev(u)) for u in arr])
  x = matrix(values).T  # make sure to have column-vector
  U = pd.np.ones((N,1))  # array of ones, all channels are used for 1 POI (csc).
  # O = pd.np.ones((N,N))  # square of ones , for completely correlated values
  I = pd.np.identity(N)  # identity matrix, for completely uncorrelated values
  V = covariance_matrix(values, errors, I)

  ## Lambda (weights)
  L = ( U.T * V.I * U ).I * (U.T * V.I)
  B = L * x

  ## extract result
  val   = B[0,0]
  error = (L*V*L.T)[0,0]**0.5
  return ufloat(val, error)

  # chi2          = ((x-(U*B)).T * V.I * (x-(U*B)))[0,0]
  # errors        = {}
  # for name, cov in covar_matrices.iteritems():
  #   errors[name] = (L*cov*L.T)[0,0]**0.5
  # ## Finally
  # return {
  #   'nominal_value': nominal_value,
  #   'weights'      : L.tolist()[0],
  #   'chi2'         : chi2,
  #   'chi2pdof'     : chi2/(N-1),
  #   'error'        : error,
  #   # 'errors'       : errors,
  #   # 'covars'       : covar_matrices,
  # }

#===============================================================================

def combine_BLUE( values, **covar_matrices ):
  """
  Given the array of base values, and dict of covariances matrix,
  return the combined result using BLUE method as
  
  result = {
    'nominal_value': combined nominal values.
    'weights'      : list of weights from each contribution.
    'chi2'         : Chi-square of the combination.
    'errors'       : dict of uncertainties from each source.
  }

  Against example in Valassi
  "Combining correlated measurements of several different physical quantities"

  >>> from uncertainties.unumpy import matrix
  >>> s1 = "VAL: {0[nominal_value]:.4f} +- {0[error]:.4f}, "
  >>> s2 = "CHI2PDOF: {0[chi2]:.2f}/{0[ndf]}"
  >>> fmt = lambda res: (s1+s2).format(res)

  >>> values = 0.1050, 0.1350, 0.0950, 0.1400
  >>> covar = matrix([
  ...   [1e-4, 0, 0, 0],
  ...   [0, 9e-4, 0, 0],
  ...   [0, 0, 9e-4, 0],
  ...   [0, 0, 0, 9e-4],
  ... ])
  >>> print(fmt(combine_BLUE(values, err=covar)))
  VAL: 0.1096 +- 0.0087, CHI2PDOF: 2.19/3

  >>> covar = matrix([
  ...   [1e-4, 0.45e-4, 0, 0],
  ...   [0.45e-4, 9e-4, 0, 0],
  ...   [0, 0, 9e-4, 0],
  ...   [0, 0, 0, 9e-4],
  ... ])
  >>> print(fmt(combine_BLUE(values, err=covar)))
  VAL: 0.1087 +- 0.0089, CHI2PDOF: 2.32/3

  ## Expect: (10.71 +- 0.90)%, chi2/dof = 4.01/3
  >>> covar = matrix([
  ...   [1e-4, 0      , 0      , 0      ],
  ...   [0   , 9.00e-4, 0      , 8.96e-4],
  ...   [0   , 0      , 9.00e-4, 0      ],
  ...   [0   , 8.96e-4, 0      , 9.00e-4],
  ... ])
  >>> print(fmt(combine_BLUE(values, err=covar)))
  VAL: 0.1071 +- 0.0090, CHI2PDOF: 4.36/3

  """
  ## Preparation
  x = matrix(values).T  # make sure to have column-vector
  N = len(values)
  U = pd.np.ones((N,1))  # array of ones, all channels are used for 1 POI (csc).
  V = sum(covar_matrices.values())

  # print U
  # print V.I
  # print U.T * V.I * U  # sum of weight
  # print ( U.T * V.I * U ).I
  # print (U.T * V.I)

  ## Lambda (weights)
  L = ( U.T * V.I * U ).I * (U.T * V.I)
  B = L * x
  # extract result
  nominal_value = B[0,0]
  chi2          = ((x-(U*B)).T * V.I * (x-(U*B)))[0,0]
  errors        = {}
  sum_err_sq    = 0.
  for name, cov in covar_matrices.iteritems():
    err2 = (L*cov*L.T)[0,0]
    sum_err_sq  += err2
    errors[name] = err2**0.5

  ## Finally
  return {
    'nominal_value': nominal_value,
    'weights'      : L.tolist()[0],
    'chi2'         : chi2,
    'ndf'          : N-1,
    'chi2pdof'     : chi2/(N-1),
    'errors'       : errors,
    'error'        : sum_err_sq**0.5,
    'covars'       : covar_matrices,
  }

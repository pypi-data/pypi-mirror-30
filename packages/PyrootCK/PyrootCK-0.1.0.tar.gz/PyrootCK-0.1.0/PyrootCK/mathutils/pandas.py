#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

  Fallback to arith mean
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

def fast_combine_BLUE(arr0):
  """
  Give array of ufloat, of uncorrelated errors, combine them into one.

  >>> u1 = ufloat(12, 3)
  >>> u2 = ufloat(12, 4)
  >>> print('{:.2f}'.format(fast_combine_BLUE([u1, u2])))
  12.00+/-2.40
  >>> fast_combine_BLUE([u1])
  12.0+/-3.0
  >>> fast_combine_BLUE([])
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

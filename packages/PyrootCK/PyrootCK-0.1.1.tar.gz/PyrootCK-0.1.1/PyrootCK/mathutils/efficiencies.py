#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
from uncertainties import ufloat
from .. import logger
from .asymvar import asymvar

#===============================================================================

def Eff(total, passed):
  """
  Prototype. To be promoted to class later.
  Interfaced on TEfficiency.

  Use Clopper-Pearson, default to 68%.

  >>> Eff(5, 2)
  0.400 +0.303 -0.253

  """
  assert isinstance(total , (int,long)), "Need int, got %r: %r"%(type(total), total)
  assert isinstance(passed, (int,long)), "Need int, got %r: %r"%(type(passed), passed)
  eff = ROOT.TEfficiency('eff','eff', 1, 0, 1) # 1bin
  eff.SetTotalEvents(0, total)
  eff.SetPassedEvents(0, passed)
  eff.statisticOption = ROOT.TEfficiency.kFCP
  val   = eff.GetEfficiency(0)
  elow  = eff.GetEfficiencyErrorLow(0)
  ehigh = eff.GetEfficiencyErrorUp(0)
  return asymvar(val, ehigh, elow)

#-------------------------------------------------------------------------------

def try_int(x):
  """
  Helper method to try to safely coerce ``float`` to ``int``.

  >>> try_int(3)
  3
  >>> try_int(3L)
  3L
  >>> try_int(3.0)
  3
  >>> try_int(0.5)
  Traceback (most recent call last):
  ...
  ValueError: Need an integer: ...
  
  """
  if isinstance(x, (int, long)):
    return x
  elif isinstance(x, float) and x.is_integer():
    return int(x)
  raise ValueError('Need an integer: %s (%s)'%(x, type(x)))

def EffU( total, passed, tag=None ):
  """
  Wrapper of above, but return as uncertainties.ufloat

  Cast (total, passed) to int if checked as valid.

  >>> '{:.3f}'.format(EffU(5, 2))
  '0.425+/-0.278'

  """
  total  = try_int(total)
  passed = try_int(passed)
  vn,vs  = Eff(total,passed).sym
  return ufloat(vn, vs, tag)

#-------------------------------------------------------------------------------

def EffU_unguard(total, passed):
  """
  Custom divide in case of eff>1.0 (mumu). Fallback to normal divide,
  but retain the rerr using n=d.
  
  >>> '{:.3f}'.format(EffU_unguard(100, 50))
  '0.500+/-0.055'

  >>> '{:.3f}'.format(EffU_unguard(100, 101))
  '1.010+/-0.009'

  Convert ``ZeroDivisionError`` to ``nan``

  >>> EffU_unguard(0, 2)
  nan

  """
  if passed <= total:
    return EffU(total, passed)
  x = EffU(total, total)
  try:
    return (1. * passed/total) * ufloat(1, x.rerr)
  except ZeroDivisionError, e:
    logger.warning(e)
    logger.warning('passed=%i, total=%i. Return NaN.'%(passed, total))
    return float('NaN')

#===============================================================================

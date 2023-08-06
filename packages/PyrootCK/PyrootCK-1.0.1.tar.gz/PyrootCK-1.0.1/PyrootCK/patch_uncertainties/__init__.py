#!/usr/bin/env python

"""

Provide patcher to ``uncertainties`` library

"""

import re
import math
import uncertainties
from uncertainties import ufloat, UFloat
from PythonCK.stringutils import try_int_else_float

def var(n, tag=None):
  """
  Use so frequently: 1-arg constructor with Poisson err.

  >>> var(9)
  9.0+/-3.0

  >>> var(16, 'stat')
  < stat = 16.0+/-4.0 >

  """
  return ufloat(float(n), n**0.5, tag)

def isinstance_ufloat(x):
  """
  Helper method to avoid deep import

  >>> isinstance_ufloat(var(3))
  True
  >>> isinstance_ufloat(42)
  False
  >>> isinstance_ufloat(3.14)
  False

  """
  return isinstance(x, uncertainties.UFloat)

#-------------------------------------------------------------------------------

def rerr(u):
  """
  Relative error.
  
  >>> ufloat(4, 1).rerr
  0.25

  >>> ufloat(0, 1).rerr
  0.0

  """
  return abs(u.s/u.n) if u.n else 0.

def upperlim(u, sigma=2):
  """
  Upper limit, default to 2 sigma

  >>> ufloat(10, 3).upperlim()
  16.0

  """
  return u.n + 2*u.s

def tags(u):
  """
  Return set of all tags in this ufloat instance.

  >>> v = ufloat(1, 0.2, 'stat') * ufloat(1, 0.1, 'syst')
  >>> v.tags
  set(['syst', 'stat'])

  """
  return {v.tag for v,_ in u.error_components().items()}

def interval(u):
  """
  Return the string representing the interval.
  Compacify the notation (float to int) whenever possible.
  
  >>> ufloat(2.5, 0.5).interval
  '(2, 3]'
  >>> ufloat(2.125, 0.125).interval
  '(2, 2.25]'

  """
  return '(%s, %s]'%(try_int_else_float(u.low), try_int_else_float(u.high))

def from_interval(s):
  """
  Convert from interval string to ufloat instance.
  Do nothing if it's already ufloat

  Args:
    s (str,int,ufloat): support inputs heterogeneously.

  >>> ufloat.from_interval('(10, 30]')
  20.0+/-10.0
  >>> ufloat.from_interval('[10, 30]')
  20.0+/-10.0

  >>> ufloat.from_interval(50)
  50.0+/-0
  >>> ufloat.from_interval('50')
  50.0+/-0

  >>> ufloat.from_interval(var(4))  # do nothing
  4.0+/-2.0

  """
  ## Do nothing
  if isinstance_ufloat(s):
    return s
  ## If is digit return ufloat of zero error
  if isinstance(s, (int, float)):
    return ufloat(s, 0.)
  if isinstance(s, basestring) and s.isdigit():
    return ufloat(float(s), 0.)
  ## try to parse as interval
  vlow, vhigh = re.findall(r'[\(\[](\S+),\s*(\S+)[\]\)]', s)[0]
  vlow, vhigh = float(vlow), float(vhigh)
  vmid, vdiff = (vhigh+vlow)*0.5, (vhigh-vlow)*0.5
  return ufloat(vmid, vdiff)

def rounding_PDG(u):
  """
  Return a 3-tuple (sf, nmag, smag) representing the appropriate formatting
  places following PDF rule, suitable for fine latex formatting.

  >>> ufloat(0.827, 0.119).rounding_PDG()
  (2, 1, 1)

  >>> ufloat(0.827, 0.367).rounding_PDG()
  (1, 1, 1)

  >>> ufloat(14.674, 0.964).rounding_PDG()
  (2, 2, 1)

  nmag, smag are the magnitude of value when written in full form (e.g. 5346+-123)
  not scientific form (e.g., 5.34+-0.12 e2)

  """
  s3f  = int(u.s * 1000)
  sf   = 2 if (s3f >= 100 and s3f <= 354) or (s3f >= 950 and s3f <= 999) else 1
  nmag = int(math.log10(u.n))+1
  smag = max(int(math.log10(u.s)), 0)+1
  return sf, nmag, smag

def get_error(u, tag):
  """
  Helper method to return sum of errors only from given tag

  >>> v = ufloat(1, 0.2, 'stat') * ufloat(1, 0.1, 'syst')
  >>> v.get_error('syst')
  0.1

  """
  gen = u.error_components().items()
  return math.sqrt(sum(error**2 for (var, error) in gen if var.tag == tag))

def get_rerr(u, tag):
  """
  Like above, but return the relative error

  >>> v = ufloat(3, 0.2, 'stat') * ufloat(4, 1, 'syst')
  >>> v.get_rerr('syst')
  0.25
  
  """
  return u.get_error(tag)/u.n

#===============================================================================

uncertainties.core.Variable.rerr          = property(rerr)
uncertainties.core.Variable.upperlim      = upperlim
uncertainties.core.Variable.tags          = property(tags)
uncertainties.core.Variable.low           = property(lambda x: x.n-x.s)
uncertainties.core.Variable.high          = property(lambda x: x.n+x.s)
uncertainties.core.Variable.interval      = property(interval)
uncertainties.core.Variable.rounding_PDG  = rounding_PDG

ufloat.from_interval = from_interval

uncertainties.core.AffineScalarFunc.rerr      = property(rerr)
uncertainties.core.AffineScalarFunc.upperlim  = upperlim
uncertainties.core.AffineScalarFunc.tags      = property(tags)
uncertainties.core.AffineScalarFunc.low       = property(lambda x: x.n-x.s)
uncertainties.core.AffineScalarFunc.high      = property(lambda x: x.n+x.s)
uncertainties.core.AffineScalarFunc.get_error = get_error
uncertainties.core.AffineScalarFunc.get_rerr  = get_rerr 
uncertainties.core.AffineScalarFunc.rounding_PDG = rounding_PDG

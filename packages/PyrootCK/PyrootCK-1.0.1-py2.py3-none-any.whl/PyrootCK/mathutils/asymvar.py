#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from uncertainties import ufloat
from .misc import sumq

#===============================================================================

class AuxOp(object):
  """
  Provide auxiliary math operators given that add,mult,pow is already defined.
  http://www.rafekettler.com/magicmethods.html

  """
  __slots__ = ()
  def __radd__(self, other):
    return self + other
  def __neg__(self):
    return self * (-1.)
  def __sub__(self, other):
    return self + (-other)
  def __rsub__(self, other):
    return other + (-self)
  def __rmul__(self, other):
    return self * other
  def __div__(self, other):
    return self * (other**-1.)
  def __rdiv__( self, other ):
    return (self**-1.) * other

#-------------------------------------------------------------------------------

MetaBaseVar = namedtuple('MetaBaseVar', 'val ehigh elow')

class asymvar(AuxOp, MetaBaseVar):
  """
  Base class for variable with (possibly asymmetric) error, allowing basic
  arimetic operation where error is propagated in quadrature.

  - Assume no correlation.

  Usage:

      Basic
  
      >>> x = asymvar(50, 30, 40)
      >>> y = asymvar(60, 40, 30)
      >>> x, y
      (50.000 +30.000 -40.000, 60.000 +40.000 -30.000)

      Addition/subtraction, commutativity.

      >>> -x
      -50.000 +30.000 -40.000
      >>> x + y
      110.000 +50.000 -50.000
      >>> x+y == y+x
      True
      >>> x + 25
      75.000 +30.000 -40.000
      >>> x+25 == 25+x
      True
      >>> x-20 == -(20-x)
      True
      
      Multiplication/division, commutativity.

      >>> x/2.
      25.000 +15.000 -20.000
      >>> 1./x
      0.020 +0.012 -0.016
      >>> x * y
      3000.000 +2690.725 -2830.194
      >>> x*y == y*x
      True
      >>> 2 * x
      100.000 +60.000 -80.000
      >>> 2*x == x*2
      True

      Power, exponent
      
      >>> x**2
      2500.000 +3000.000 -4000.000
      >>> x**-1 == 1./x
      True

  """
  __slots__ = []

  def __new__(cls, val, ehigh, elow):
    """
    Cast to float
    """
    assert ehigh >= 0 and elow >= 0, 'Need positive error for both high/low.'
    val   = float(val)
    ehigh = float(ehigh)
    elow  = float(elow)
    return super(asymvar, cls).__new__(cls, val, ehigh, elow)

  def __float__(self):
    """
    This will discard the uncertainty part and return actual value as float.
    """
    return self.val

  @classmethod
  def from_const(cls, val):
    """
    Return an instance of this class of zero-error (const).

    >>> asymvar.from_const(5)
    5.000 +0.000 -0.000
    """
    return cls(val, 0., 0.)

  @classmethod
  def from_ufloat(cls, val):
    """
    Return new instance given the ufloat.

    >>> from uncertainties import ufloat
    >>> asymvar.from_ufloat(ufloat(1, 0.2))
    1.000 +0.200 -0.200
    >>> asymvar.from_ufloat(0.5)
    0.500 +0.000 -0.000

    """
    ## allow implicitly the conversion from int/float too.
    if isinstance(val, (int,float)):
      return cls.from_const(val)
    return cls(val.n, val.s, val.s)

  @property
  def sym(self):
    """
    Return a (val,err) pair that represent symmetricized uncertainty.
    """
    err = (self.ehigh+abs(self.elow))/2
    val = float(self) + (self.ehigh-abs(self.elow))/2
    return val,err

  def to_ufloat(self):
    """
    Convert from my asymmetric var instance to ufloat instance.

    >>> asymvar(5, 3, 4).to_ufloat()
    4.5+/-3.5
    
    """
    return ufloat(*self.sym)

  def __repr__(self):
    return '{0.val:.3f} +{0.ehigh:.3f} -{0.elow:.3f}'.format(self)

  def __add__(self, other):
    if isinstance(other, (int,float)):
      other = self.from_const( other )
    val   = self.val + other.val
    elow  = sumq([self.elow , other.elow ])
    ehigh = sumq([self.ehigh, other.ehigh])
    return asymvar(val, ehigh, elow)

  def __mul__(self, other):
    ## Treat pure number as no uncertainty
    if isinstance(other, (int,float)):
      other = self.from_const(other)
    val   = self.val * other.val
    elow  = sumq([self.val*other.elow , self.elow *other.val])
    ehigh = sumq([self.val*other.ehigh, self.ehigh*other.val])
    return asymvar(val, ehigh, elow)

  def __pow__(self, power):
    assert isinstance(power, (int,float))
    val   = self.val ** power
    elow  = abs(val * power / self.val) * self.elow
    ehigh = abs(val * power / self.val) * self.ehigh
    return asymvar(val, ehigh, elow)

#===============================================================================

# class Var(asymvar):
#   """
#   - Symmetric error
#   - If no error given, use Poissonian error by default (sqrt(val)).
#   - Slightly more compact __str__
#   """
#   __slots__ = []

#   def __new__(cls, val=0, err=None):
#     err = abs(float(err)) if err is not None else abs(val**0.5)
#     return super(Var, cls).__new__( cls, val, err, err )

#   def __str__(self):
#     template = '{0} ± {0}'.format(self.fig)
#     if self.name:
#       template = ('Var: %s = '%self.name) + template
#     return template%(self.val, self.ehigh)

#   def __repr__(self):
#     return self.__str__()

#   @classmethod
#   def const(cls, val):
#     """Return an instance of this class of zero-error (const)."""
#     return cls( val, 0. )

#   def __add__(self, other):
#     """Attempt to retain the same class"""
#     ## Treat pure number as no uncertainty
#     if isinstance( other, (int,float)):
#       other = self.const( other )
#     if self.__class__ != other.__class__:
#       return super(Var,self).__add__(other)
#     val   = self.val + other.val
#     elow  = sumq( self.elow , other.elow  )
#     return Var( val, elow )

#   def __mul__(self, other):
#     """Attempt to retain the same class"""
#     ## Treat pure number as no uncertainty
#     if isinstance( other, (int,float)):
#       other = self.const( other )
#     if self.__class__ != other.__class__:
#       return super(Var,self).__mul__(other)
#     val   = self.val * other.val
#     elow  = sumq( self.val*other.elow , self.elow*other.val )
#     return Var( val, elow )

#   def __pow__( self, power ):
#     assert isinstance( power, (int,float))
#     val   = self.val ** power
#     elow  = abs( val * power / self.val ) * self.elow
#     return Var( val, elow )


#===============================================================================


# class Var(AuxVar, namedtuple('Var', 'name val err')):
#   """
#   Helper class to calculate basic arimethic operation of variable with uncertainty.
#   """
#   __slots__ = []
#   decimal = 4 # default decimal places
#   def __new__(cls, val, err=None):
#     """
#     - Cast to float
#     - If no error is given, assume Poissonian.

#     >>> Var( 5, 2 )
#     Var(val=5.0, err=2.0)

#     """
#     name  = hackname()
#     val   = float(val)
#     err   = abs(float(err)) if err is not None else abs(val**0.5)
#     return super(cls, Var).__new__( cls, name, val, err )
#   @staticmethod
#   def const(val):
#     return Var( val, 0. )
  # @property
  # def rerr(self):
  #   """Relative error."""
  #   return abs(self.err / self.val)
  # def __str__(self):
  #   fig = '%.{}f'.format(str(int(self.decimal)))
  #   template = '{0} ± {0}'.format(fig)
  #   if self.name:
  #     template = ('Varr: %s = '%self.name) + template
  #   return template%(self.val, self.err)
  # def __add__(self, other):
  #   if isinstance( other, (int,float)):
  #     other = Var.const( other )
  #   val = self.val + other.val
  #   err = sumq( self.err, other.err)
  #   return Var( val, err )
  # def __mul__(self, other):
  #   ## Treat pure number as no uncertainty
  #   if isinstance( other, (int,float)):
  #     other = Var.const( other )
  #   val = self.val * other.val
  #   err = sumq( self.rerr, other.rerr )*val
  #   return Var( val, err )
  # def __pow__( self, power ):
  #   assert isinstance( power, (int,float))
  #   val = self.val ** power
  #   err = abs( val * power / self.val ) * self.err
  #   return Var( val, err )

#===============================================================================


# class Varr(AuxVar, namedtuple('ProtoVarr', 'name val syst stat')):
#   decimal = 4 # default decimal places
#   def __new__(cls, val, syst=None, stat=None):
#     """
#     If both syst and stat is None, treat as Poissonian error on stat.
#     If only one (non-kwarg) err is given, by pythonic convention, it's syst.

#     >> Var( 100 )            # syst = 0. , stat = 10.
#     >> Var( 100, syst=True ) # syst = 10., stat =  0.
#     >> Var( 100, 0.5 )       # syst = 0.5, stat =  0.

#     """
#     name  = hackname()
#     val   = float(val)
#     if stat is None:
#       err = abs(val**0.5)
#       if syst is None:
#         syst = 0.
#         stat = err
#       elif syst is True:
#         syst = err
#         stat = 0.
#       elif isinstance( syst, (int,float)):
#         syst = float(syst)
#         stat = 0.
#       else:
#         raise ValueError('Unknown strategy.')
#     return super(cls, Varr).__new__( cls, name, val, syst, stat )
#   @staticmethod
#   def const(val):
#     return Varr( val, 0., 0. )
#   @property
#   def rsyst(self):
#     return abs(self.syst / self.val)
#   @property
#   def rstat(self):
#     """Relative error."""
#     return abs(self.stat / self.val)
#   def __str__(self):
#     ## Remark, return stat first, per LHCb convention
#     fig = '%.{}f'.format(str(int(self.decimal)))
#     template = '{0} ± {0} \stat ± {0} \syst'.format(fig)
#     if self.name:
#       template = ('Varr: %s = '%self.name) + template
#     return template%(self.val, self.stat, self.syst)
#   def __add__(self, other):
#     if isinstance( other, (int,float)):
#       other = self.const(other)
#     val   = self.val + other.val
#     syst  = sumq( self.syst, other.syst )
#     stat  = sumq( self.stat, other.stat )
#     return Varr( val, syst, stat )
#   def __mul__(self, other):
#     ## Treat pure number as no uncertainty
#     if isinstance( other, (int,float)):
#       other = self.const(other)
#     val   = self.val * other.val
#     syst  = sumq( self.rsyst, other.rsyst )*val
#     stat  = sumq( self.rstat, other.rstat )*val
#     return Varr( val, syst, stat )
#   def __pow__( self, power ):
#     assert isinstance( power, (int,float))
#     val   = self.val ** power
#     syst  = abs( val * power / self.val ) * self.syst
#     stat  = abs( val * power / self.val ) * self.stat
#     return Varr( val, syst, stat )

#===============================================================================

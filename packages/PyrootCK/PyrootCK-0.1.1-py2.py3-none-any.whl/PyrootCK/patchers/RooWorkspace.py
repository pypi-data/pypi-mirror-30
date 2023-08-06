
from uncertainties import ufloat

def series(w):
  """
  Returns all vars in this workspace into ``pd.Series``.
  
  >>> w = ROOT.RooWorkspace()
  >>> a = w.factory('a[1]')
  >>> b = w.factory('b[2,5]')
  >>> c = w.factory('c[3,1,10]')
  >>> c.setError(0.2)
  >>> w.series()
  a              1
  b            3.5
  c    3.00+/-0.20
  dtype: object

  """
  import pandas as pd
  acc = pd.Series()
  for v in w.allVars():
    n,s = v.val, v.error
    acc[v.name] = n if s==0. else ufloat(n,s)
  return acc

def PrintVars(w):
  """
  Print all its variables in the workspace.
  """
  print 'Variables'
  print '---------'
  for v in w.allVars():
    v.Print()
  print

def factoryArgs(w, s, l):
  """
  Similar the RooWorkspace factory, but allow second argument to be the list of
  strings as argument in first param s. Make things slightly more dynamic. 
  
  This is used mainly in extended-likelihood modelling of Higgs->mutau analysis
  where the template has to conform lots of model variation dynamically 
  (channel, regime, pdf, etc.)

  In other word, the new syntax::
      
      w.factoryArgs('prod:nsig', ['x', 'y', 'z'])

  is equivalent to the existing syntax::

      w.factory('prod:nsig("x", "y", "z")')

  Args:
    s (str): ``cls:name`` factory syntax
    l (list of str): args for the ``cls`` constructor.

  Usage:
  
  >>> w = ROOT.RooWorkspace()
  >>> _ = w.factory('x[3]')
  >>> _ = w.factory('y[4]')
  >>> w.factoryArgs('prod:nsig', ['x', 'y'])
  <ROOT.RooProduct object ("nsig") at ...>

  """
  assert isinstance(l, (tuple, list))
  assert all(isinstance(x, basestring) for x in l)
  return w.factory(s+'({})'.format(','.join(l)))

def load_from_RooFitResult(self, res):
  """
  Given the ``RooFitResult``, set the value/error of variables found in workspace
  as listed in the ``RooFitResult``, similar to how ``loadSnapshot``? works.

  >>> w = getfixture('rooworkspace')
  >>> r = getfixture('roofitresult')
  >>> w.load_from_RooFitResult(r)

  """
  for key, val in res.series().iteritems():
    if self.var(key):
      self.var(key).val = val.n
      self.var(key).error = val.s

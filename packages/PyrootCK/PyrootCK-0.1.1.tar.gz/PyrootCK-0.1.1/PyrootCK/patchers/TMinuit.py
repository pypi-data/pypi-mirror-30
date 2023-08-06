from array import array
from uncertainties import ufloat

def parameters(self):
  """
  Return the list of ``ufloat``, representing the fit parameters.

  >>> m = ROOT.TMinuit(2)
  >>> m.printLevel = -1
  >>> m.mnparm(0, 'a', .1783, 1e-3, .1783*0.9, .1783*1.1, array('i', [0]))
  >>> m.mnparm(1, 'b', .5011, 1e-3, .5011*0.9, .5011*1.1, array('i', [0]))
  >>> m.parameters
  [0.1783+/-0.001, 0.5011+/-0.001]

  """
  val = array('d', [0.])
  err = array('d', [0.])
  acc = []
  for i in xrange(self.numPars):
    self.GetParameter(i, val, err)
    acc.append(ufloat(val[0], err[0]))
  return acc

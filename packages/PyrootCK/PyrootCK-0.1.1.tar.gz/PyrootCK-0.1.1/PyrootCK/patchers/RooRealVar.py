from uncertainties import ufloat as UFloat

def ufloat(self):
  """
  Return new ufloat instance that correspond to this var.

  >>> r = ROOT.RooRealVar('name', 'title', 5)
  >>> r.error = 0.2
  >>> r.ufloat()
  5.0+/-0.2
  
  """
  return UFloat(self.val, self.error)

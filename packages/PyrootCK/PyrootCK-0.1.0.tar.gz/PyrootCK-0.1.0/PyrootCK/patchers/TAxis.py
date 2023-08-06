from PythonCK.stringutils import try_int_else_float

def bins(self):
  """
  Return python list of axis marks, with length already fixed to TAxis.GetNbins()+1

  >>> ROOT.TAxis(5, 0, 5).bins
  [0, 1, 2, 3, 4, 5]

  - Fallback to GetBinLowEdge,GetBinUpEdge in (strangely) rare case with TProfile2D.
  """
  n = self.nbins
  try:
    return [ try_int_else_float(self.xbins[i]) for i in xrange(n+1)]
  except IndexError:
    return [ try_int_else_float(self.GetBinUpEdge(i)) for i in xrange(n+1) ]

def labels(old_method):
  """
  OVERRIDING the existing `GetLabels`. It's not practical enough.
  Return the list of strings, same length of number of bins, as a pretty
  representative of bin name

  >>> axis = ROOT.TAxis(3, 0, 3)
  >>> axis.labels
  ['(0, 1]', '(1, 2]', '(2, 3]']
  >>> axis.SetBinLabel(1, 'a')
  >>> axis.SetBinLabel(2, 'b')
  >>> axis.SetBinLabel(3, 'c')
  >>> axis.labels
  ['a', 'b', 'c']

  """
  def wrap(self):
    if self.IsAlphanumeric(): # true when all labels are assigned.
      return [str(old_method(self)[i]) for i in xrange(self.nbins)]
    else: # pragma: no cover
      # by default it return null pointer here, I'll decide later.
      acc = []
      for i in xrange(self.nbins):
        vmin = str(try_int_else_float(self.GetBinLowEdge(i+1)))
        vmax = str(try_int_else_float(self.GetBinUpEdge(i+1)))
        acc.append('(%s, %s]'%(vmin, vmax))
      return acc
  return wrap

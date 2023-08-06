
from uncertainties import ufloat, nominal_value

#===============================================================================

def series(self):
  """
  Convert ``TH1`` instance to ``pd.Series``.

  >>> getfixture('th1f').series()
  (0, 1]      0.0+/-0
  (1, 2]    3.0+/-1.7
  (2, 3]    5.0+/-2.2
  (3, 4]      0.0+/-0
  dtype: object

  """
  import pandas as pd
  acc = []
  for i in xrange(1, self.xaxis.nbins+1):
    acc.append(ufloat(self.GetBinContent(i), self.GetBinError(i)))
  se = pd.Series(acc)
  ## make an index intv
  se.index = pd.cut([], self.xaxis.bins).categories
  return se

#===============================================================================

def vlookup(self, arr, wrap=True):
  """
  Given an array of values (exists on xaxis), return the array of same length
  where each entry is the corresponding content in that bin.

  Args:
    arr (list of numbers): Array of value to check.
    wrap (bool): If the value are outside the range (overflow, underflow), 
                 then depends on the flag ``wrap``. If True, it'll correct with 
                 the at the border, otherwise it's ``nan``.

  >>> h = getfixture('th1f')
  >>> h.vlookup([1.2, 2.5])
  [3.0, 5.0]
  >>> h.vlookup([1.2, 5])  # with overflow
  [3.0, 0.0]

  """
  import pandas as pd
  se     = self.series().apply(nominal_value)
  bins   = self.xaxis.bins
  binned = pd.cut(arr, bins)
  ## correct for underflow, overflow
  if wrap:
    for i,(x,b) in enumerate(zip(arr, binned)):
      if isinstance(b, float) and pd.np.isnan(b):
        binned[i] = se.index[0] if x <= bins[0] else se.index[-1]
  ## Use merge under the hood
  se.name = 'temp'
  df = pd.DataFrame({'temp':binned}).set_index('temp').join(se)
  return df.iloc[:,-1].tolist()

#===============================================================================

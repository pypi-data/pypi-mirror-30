import uncertainties

def from_pair_ufloats(cls, lx, ly):
  """
  Convert a pair of ufloat-array into TGraphErrors,
  where the first array if list of X, and another is list of Y.
  - Also sort in X.
  - dropna
  - Skip None

  Because ufloat is symmetric, support only to symmetric-error
  TGraphErrors for now.

  >>> ROOT.TGraphErrors.from_pair_ufloats([ 1,2,3 ], [
  ...   ufloat(1, 0.5),
  ...   ufloat(2, 0.6),
  ...   ufloat(4, 1.2),
  ... ])
  <ROOT.TGraphErrors object ("Graph") at ...>

  """
  Nom = uncertainties.nominal_value
  Err = uncertainties.std_dev

  ## sort the XY-pair by X
  lxy = sorted(list(zip(lx, ly)), key=lambda p:p[0])
  x   = []
  y   = []
  ex  = []
  ey  = []
  for valx, valy in lxy:
    if Nom(valx) is not None and Nom(valy) is not None:
      x.append (Nom(valx))
      ex.append(Err(valx))
      y.append (Nom(valy))
      ey.append(Err(valy))
  g = cls(len(x), x, y, ex, ey)
  g.ownership = False
  return g

# #===============================================================================

# def series(self):
#   import pandas as pd

#   print [self.X[i] for i in xrange(self.n)]

#   # acc  = pd.Series()
#   # xarr = list(pd.cut([], self.xaxis.bins).categories)

#   # print self.xaxis.bins
#   # print xarr

#   # for i, xlabel in enumerate(xarr):
#   #   acc[xlabel] = ufloat(self.Y[i], self.EY[i])
#   # return acc

# #===============================================================================

# def vlookup(self, arr):
#   import pandas as pd
#   bins   = self.xaxis.bins
#   binned = pd.cut(arr, bins)

#   print bins
#   print 

#   ## Use merge under the hood
#   # se     = self.series()

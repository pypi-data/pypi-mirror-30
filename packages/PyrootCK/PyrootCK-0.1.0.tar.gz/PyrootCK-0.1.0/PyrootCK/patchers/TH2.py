#!/usr/bin/env python

import pandas as pd
from uncertainties import ufloat, nominal_value, std_dev

#===============================================================================

# @classmethod
def from_uframe(cls, df):
  """
  Convert from pandas.DataFrame of ufloat to TH2.

  Usage:
  >>> df = pd.DataFrame([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
  >>> df.index.name = 'IDX'
  >>> df.columns.name = 'COL'
  >>> ROOT.TH2F.from_uframe(df)
  <ROOT.TH2F object ("name") at ...

  """
  nrow,ncol = df.shape
  h = cls('name', 'title', ncol,0,ncol, nrow,0,nrow)
  h.ownership  = False
  h.markerSize = 2.

  ## Init array
  for prod,col in df.iteritems():
    for orig,_ in col.iteritems():
      h.Fill(prod, orig, 0.)

  ## Fill array
  for j,(_,row) in enumerate(df.iterrows()):
    for i,(_,cell) in enumerate(row.iteritems()):
      h.SetBinContent(i+1, j+1, nominal_value(cell))
      h.SetBinError  (i+1, j+1, std_dev(cell))

  ## optional if axis label exists
  if df.index.name:
    h.yaxis.title = df.index.name
  if df.columns.name:
    h.xaxis.title = df.columns.name

  ## Finally
  return h 

#===============================================================================

def dataframe(self):
  """
  Convert TH2 instance to DataFrame.

  In addition to convert to pandas.DataFrame:
  - value as ufloat is used
  - correct the columns,index to be an interval-string.

  Usage:
  >>> h = getfixture('th2f')
  >>> h.dataframe()
             (0, 1]   (1, 2]   (2, 3]
  (0, 1]  1.0+/-1.0  0.0+/-0  0.0+/-0
  (1, 2]  4.0+/-2.0  0.0+/-0  0.0+/-0
  (2, 3]    0.0+/-0  0.0+/-0  0.0+/-0

  """
  ## Loop over rows & cols
  rows  = []
  nx    = self.xaxis.nbins
  ny    = self.yaxis.nbins
  for ix in xrange(1,nx+1):
    col = []
    for iy in xrange(1,ny+1):
      val = ufloat(self.GetBinContent(ix,iy), self.GetBinError(ix,iy))
      col.append(val)
    rows.append(col)
  df = pd.DataFrame(rows).T
  ## Prepare labels
  # df.columns = self.xaxis.labels
  # df.index   = self.yaxis.labels
  ## type: <type 'pandas._libs.interval.Interval'>
  df.columns = pd.cut([], self.xaxis.bins).categories # for vlookup
  df.index   = pd.cut([], self.yaxis.bins).categories
  ## finally
  df.name = self.name
  return df

#===============================================================================

def vlookup(self, xarr, yarr, wrap=False):
  """
  arr is the pd.Series of (x,y) values to look up.
  Return clean series of lookedup values.

  >>> xarr = pd.Series([0.2, 0.5, 1.3])
  >>> yarr = pd.Series([1.5, 2.2, 0.1])
  >>> h = getfixture('th2f')
  >>> h.vlookup(xarr, yarr, wrap=True)
  [4.0, 0.0, 0.0]

  """

  ## To work with wrapping, modify the input to come back into bound instead
  if wrap:
    nudge = 1 + 1e-3 # the lower edge is exclusive, so it need some nudging.
    xmin = self.xaxis.bins[0]
    xmax = self.xaxis.bins[-1]
    ymin = self.yaxis.bins[0]
    ymax = self.yaxis.bins[-1]
    xarr = xarr.apply(lambda val: min(max(val, xmin*nudge), xmax))
    yarr = yarr.apply(lambda val: min(max(val, ymin*nudge), ymax))
  
  ## start 2d binning
  g1 = pd.cut(xarr, self.xaxis.bins)
  g2 = pd.cut(yarr, self.yaxis.bins)
  df = pd.DataFrame()
  df['x'] = xarr
  df['y'] = yarr
  se_source = self.dataframe().T.stack().apply(nominal_value)
  se_source.name = 'temp'
  se_source.index.names = 'lv0', 'lv1'
  df_query = pd.DataFrame({'lv0':g1, 'lv1':g2}).set_index(['lv0', 'lv1'])
  return df_query.join(se_source).iloc[:,-1].tolist()

#===============================================================================

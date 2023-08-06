
import ROOT
import pandas as pd
from uncertainties import ufloat

def dataframe(self):
  """
  Return a dataframe of of values, to be post-process later by user.

  >>> x = ROOT.TGraphAsymmErrors(3, [1,2,3], [4,5,6])
  >>> x.dataframe()
       x    y  exhigh  exlow  eyhigh  eylow
  0  1.0  4.0     0.0    0.0     0.0    0.0
  1  2.0  5.0     0.0    0.0     0.0    0.0
  2  3.0  6.0     0.0    0.0     0.0    0.0

  """
  acc = []
  for i in xrange(self.n):
    acc.append([
      self.X[i],
      self.Y[i],
      self.EXhigh[i],
      self.EXlow[i],
      self.EYhigh[i],
      self.EYlow[i],
    ])
  df = pd.DataFrame(acc)
  df.columns = [ 'x', 'y', 'exhigh', 'exlow', 'eyhigh', 'eylow' ]
  return df

#===============================================================================

def series(self):
  """
  Return a ``pd.Series`` representation of given ``TGraphAsymmErrors``.
  Compact version of above,

  >>> x = ROOT.TGraphAsymmErrors(3, [1,2,3], [4,5,6])
  >>> x.series()
  1.0+/-0    4.0+/-0
  2.0+/-0    5.0+/-0
  3.0+/-0    6.0+/-0
  dtype: object

  """
  acc = pd.Series()
  for _,se in self.dataframe().iterrows():
    x = ufloat(se.x, se.exlow)
    y = ufloat(se.y, max(se.eyhigh,se.eylow))
    acc[x] = y 
  return acc

#===============================================================================

# @classmethod
def from_pair_asymvar(cls, lx, ly):
  """
  Using ``asymvar``. Need this interface: ``.val``, ``.ehigh``, ``.elow``.

  >>> xarr = 1,2,3
  >>> yarr = 3,4,5 
  >>> ROOT.TGraphAsymmErrors.from_pair_asymvar(xarr, yarr)
  <ROOT.TGraphAsymmErrors object ("Graph") at ...>
  
  """
  from PyrootCK.mathutils import asymvar
  from uncertainties import nominal_value, std_dev

  ## triple compat: float, ufloat, asymvar
  def get_nom(v):
    return v.val if isinstance(v, asymvar) else nominal_value(v)
  def get_ehi(v):
    return v.ehigh if isinstance(v, asymvar) else std_dev(v)
  def get_elo(v):
    return abs(v.elow) if isinstance(v, asymvar) else std_dev(v)

  ## sort the XY-pair by X
  lxy = sorted(list(zip(lx, ly)), key=lambda p:p[0])
  x   = []
  y   = []
  exh = []
  eyh = []
  exl = []
  eyl = []
  for valx, valy in lxy:
    x.append  (get_nom(valx))
    exh.append(get_ehi(valx))
    exl.append(get_elo(valx))
    y.append  (get_nom(valy))
    eyh.append(get_ehi(valy))
    eyl.append(get_elo(valy))
  g = cls(len(x), x, y, exl, exh, eyl, eyh)
  g.ownership = False
  return g

#===============================================================================

# @classmethod
def from_TH1(cls, h):
  """
  Return new instance of TGraphAsymmErrors with:

  - kPoisson error
  - zero-content bins removed.

  Suitable for making new pull histogram.

  >>> h = getfixture('th1f')
  >>> ROOT.TGraphAsymmErrors.from_TH1(h)
  <ROOT.TGraphAsymmErrors object ("Data") at ...>

  """
  h = h.Clone('h2')
  h.ownership      = False
  h.binErrorOption = ROOT.TH1.kPoisson

  ## Collect points
  points = []
  for i in xrange(h.nbinsX):
    x = h.GetBinCenter(i)
    y = h.GetBinContent(i)
    l = h.GetBinErrorLow(i)
    u = h.GetBinErrorUp(i)
    if y!=0:
      points.append([x,y,0.,0.,l,u])
  
  ## Make a TGraph
  g = cls(len(points), *zip(*points))
  g.UseCurrentStyle()
  g.name         = 'Data'
  g.title        = ''
  g.ownership    = False
  g.markerStyle  = 2
  g.xaxis.limits = h.xaxis.xmin, h.xaxis.xmax 
  h.Delete()
  return g

#===============================================================================

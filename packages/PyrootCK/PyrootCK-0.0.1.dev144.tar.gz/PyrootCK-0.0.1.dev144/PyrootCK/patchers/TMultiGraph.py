import ROOT

@classmethod
def brazillian(cls, df):
  """
  Return the TMultiGraph instance stylized for Brazillian
  confidence interval plot.

  The input is pd.DataFrame, with 4 columns: exp, exp1, exp2, obs.
  Each row will be plotted along the xaxis.
  
  """
  xarr = [float(m) for m in df.index]
  exp0 = df['exp']
  exp1 = df['exp1']
  exp2 = df['exp2']
  obs  = df['obs']

  ## Graph elements
  gobs  = ROOT.TGraphErrors.from_pair_ufloats(xarr, obs)
  gexp0 = ROOT.TGraphErrors.from_pair_ufloats(xarr, exp0)
  gexp1 = ROOT.TGraphErrors.from_pair_ufloats(xarr, exp1)
  gexp2 = ROOT.TGraphErrors.from_pair_ufloats(xarr, exp2)

  ## Default name, good for legend
  gobs.title  = 'Observed'
  gexp0.title = 'Expected'
  gexp1.title = '#pm1#sigma'
  gexp2.title = '#pm2#sigma'

  ## Stylize
  gobs.markerStyle  = 8
  gobs.markerSize   = 0.5
  gobs.lineWidth    = 2
  gexp0.markerStyle = 8
  gexp0.markerSize  = 0.5
  gexp0.lineStyle   = ROOT.kDashed
  gexp0.lineWidth   = 2
  # hide skeleton
  gobs.fillColor    = 0
  gexp0.fillColor   = 0
  gexp1.markerSize  = 0
  gexp2.markerSize  = 0
  gexp1.lineWidth   = 0
  gexp2.lineWidth   = 0
  # finally band colors
  gexp1.fillColor   = ROOT.kGreen
  gexp2.fillColor   = ROOT.kYellow

  ## Add by correct order
  g = cls()
  g.Add(gexp2, '3')  # 2-sigma yellow band
  g.Add(gexp1, '3')  # 1-sigma green band
  g.Add(gexp0, 'LP') # dashed expected value
  g.Add(gobs , 'LP') # normal line observed value
  return g

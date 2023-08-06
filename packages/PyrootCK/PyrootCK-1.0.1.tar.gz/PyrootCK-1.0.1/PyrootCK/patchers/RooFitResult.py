import uncertainties

def series(self):
  """
  For result extraction.
  Computed the array of ufloat, with correlation.

  >>> res = getfixture('roofitresult')
  >>> se = res.series()
  >>> type(se)
  <class 'pandas.core.series.Series'>
  >>> se
  cscbr            -0.6+/-3.0
  e_EWK             4.2+/-2.4
  e_Other         2.99+/-0.25
  e_Zll             4.4+/-1.1
  e_Ztau           13.8+/-1.7
  e_brtau     0.1783+/-0.0004
  e_erec        0.578+/-0.014
  e_esel        0.223+/-0.008
  h1_EWK             139+/-14
  h1_Other        1.99+/-0.21
  h1_QCD               17+/-6
  h1_Zll            2.5+/-1.1
  h1_Ztau          18.8+/-1.6
  h1_brtau    0.5011+/-0.0009
  h1_erec       0.490+/-0.017
  h1_esel       0.294+/-0.006
  h3_EWK               16+/-7
  h3_Other        0.65+/-0.14
  h3_QCD                9+/-4
  h3_Ztau           9.0+/-1.1
  h3_brtau    0.1457+/-0.0007
  h3_erec       0.155+/-0.008
  h3_esel       0.425+/-0.018
  lumi              1976+/-23
  mu_erec       0.651+/-0.016
  std_eacc         -0.0+/-1.0
  dtype: object

  """
  import pandas as pd
  raws = self.floatParsFinal()
  acc  = [(raws[i].valV, raws[i].error) for i in xrange(len(raws))]
  corr = self.correlationMatrix().to_lists()
  uarr = uncertainties.correlated_values_norm(acc, corr)
  acc  = pd.Series({raws[i].name:u for i,u in enumerate(uarr)})
  return acc

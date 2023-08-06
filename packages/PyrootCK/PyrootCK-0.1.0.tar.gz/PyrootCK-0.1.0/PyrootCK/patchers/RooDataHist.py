
def weights(self):
  """
  Return list of weights from each bin.

  >>> h = getfixture('th1f')
  >>> x = ROOT.RooRealVar('name', 'title', 0, 5)
  >>> dh = ROOT.RooDataHist('dh', 'dh', [x], h)
  >>> dh.weights()
  [0.0, 3.0, 5.0, 0.0]
  
  """
  acc = []
  for i in xrange(self.numEntries()):
    self.get(i)
    acc.append(self.weight())
  self.get() # reset pointer
  return acc

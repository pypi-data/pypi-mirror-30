
def to_lists(self):
  """
  Convert ``ROOT.TMatrix`` to pythonic list of list.

  >>> ROOT.TMatrixTSym('double')(2)
  <ROOT.TMatrixTSym<double> object ("TMatrixTSym<double>") at ...>
  >>> _.to_lists()
  [[0.0, 0.0], [0.0, 0.0]]

  """
  rows = []
  for i in xrange(self.nrows):
    row = [ self[i][j] for j in xrange(self.ncols) ]
    rows.append(row)
  return rows

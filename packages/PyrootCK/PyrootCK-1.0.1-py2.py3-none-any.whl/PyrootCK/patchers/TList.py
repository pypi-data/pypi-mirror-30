
def Reverse(self):
  """
  In-place reverse the order of item in this TList.

  >>> l = ROOT.TList()
  >>> l.Add(ROOT.TNamed('n1', 'n1'))
  >>> l.Add(ROOT.TNamed('n2', 'n2'))
  >>> l.Add(ROOT.TNamed('n3', 'n3'))
  >>> [x.name for x in l]
  ['n1', 'n2', 'n3']
  >>> l.Reverse()
  >>> [x.name for x in l]
  ['n3', 'n2', 'n1']
  
  """
  n = len(self)-1
  for i in xrange(-1 * n, 0, ): # count backward
    self.AddAt(self[i], 0)
  for _ in xrange(n):
    self.RemoveLast()

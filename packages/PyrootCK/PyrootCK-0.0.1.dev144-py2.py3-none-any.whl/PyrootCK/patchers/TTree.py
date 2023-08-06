#!/usr/bin/env python

"""

Collection of additional methods for TTree

Some of these will required 3rd-party library, 
such as root_numpy, pandas.

"""

import itertools
import ROOT
import pandas as pd
from root_numpy import array2tree, tree2array
from . import logger

#===============================================================================

@property
def get_selected_cols(t):
  """
  Return number of variables used in the recent draw-call. 
  Return 0 if none has been made.
  Simialr to selectedRows

  >>
  ncol = tree.selectedCols
  """

  # print t.selectedRows
  # print t.select
  # print t.GetVar(0)
  # print t.GetVar(1)
  # print t.GetVar(10)
  # print t.GetVar(11)
  # print t.GetVar(12)

  icol = 0
  obj = True
  while obj:
    obj = t.GetVar(icol)
    icol += 1
  return icol-1

#===============================================================================

def count_ent_evt(tree, cut='', indices=['runNumber', 'eventNumber']):
  """
  Count unique run-evt after cut applied. 
  Used in LHCb-Gaudi tuple. Need a branch named 'runNumber', 'eventNumber'.

  Use pandas.Groupby, very fast.

  Args:
    cut (string): Optional, a selection string to be applied.

  Return:
    (int,int): Pair of entries, events yielded from the cut.

  Usage:
  >>> tree.count_ent_evt()
  (303, 252)
  >>> tree.count_ent_evt('M > 20e3')
  (286, 240)
  >>> tree.count_ent_evt('M < 0')
  (0, 0)

  """
  ## Precheck null result to skip warning. 
  if not tree.entries:
    return (0,0)

  ## Now with the cut
  nentries = int(tree.GetEntries(cut))
  if nentries==0:
    nevt = 0
  else:
    ## Do actual unique count
    tree.estimate = nentries+1
    p = ':'.join(indices)
    n = tree.Draw(p, cut, 'goff') # slow??
    if n <= 0 : # failed / null
      nevt = 0
    else:
      nevt = len(tree.sliced_dataframe().groupby(indices)) # use pandas, fast
      # nevt = len({ (tree.v1[i],tree.v2[i]) for i in xrange(nentries) }) # legacy

  ## Report
  logger.debug('Tree      : %r (%r)'%(tree.name, tree.title))
  logger.debug('Selection : %r'%cut)
  logger.debug('Count     : %s,%s'%(nentries,nevt))
  return nentries,nevt

#===============================================================================

def dataframe(tree, selection=None):
  """
  Convert from TTree to pandas.DataFrame.
  Internally used `root_numpy.tree2rec`.
  
  Args:
    cut (string): Optional, a selection string to be applied.

  Return:
    pandas.DataFrame: Dataframe object.

  Usage:
  >>> df = tree.dataframe()
  >>> df.iloc[:6,:6]
     nPVs  nTracks  nSPDhits  runNumber  eventNumber  BCID
  0     1       72       108    3877561       733142     0
  1     1      116       177    3877180       234649     0
  2     1       80       120    3877328       428234     0
  3     1       59        93    3877251       327720     0
  4     1       92       178    3877336       438711     0
  5     1       86       137    3877322       420541     0

  """
  rec = tree2array(tree, selection=selection).view(pd.np.recarray)
  df = pd.DataFrame(rec)
  logger.debug('convert successfully')
  df.name = tree.name
  return df

#-------------------------------------------------------------------------------

def sliced(t):
  """
  Basis for sliced objects below, yield a row of entries.

  Purely stay in ROOT framework, but ready to be extensible for below

  Note: The importent of using TTree::Draw as a base because of the aliases.
  The competitor, root_numpy.tree2arr is almost perfect but doesn't support
  the alias.

  FROM ROOT
  Important note: By default TTree::Draw creates the arrays obtained with GetW, 
  GetV1, GetV2, GetV3, GetV4, GetVal with a length corresponding to the parameter 
  fEstimate. The content will be the last GetSelectedRows() % GetEstimate() values 
  calculated. By default fEstimate=1000000 and can be modified via TTree::SetEstimate. 
  To keep in memory all the results (in case where there is only one result per entry), 

  tree->SetEstimate(tree->GetEntries()+1); // same as tree->SetEstimate(-1);
  
  You must call SetEstimate if the expected number of selected rows you need to 
  look at is greater than 1000000.

  """
  ncol = t.selectedCols
  nrow = t.selectedRows
  ## guard check for out-of-range array.
  if nrow > t.estimate:
    logger.warning('nrow [%i] > estimate [%i]'%(nrow, t.estimate))
    raise ValueError('Please call t.SetEstimate(t.entries+1) before TTree::Draw.')
  logger.debug('Slicing: %r'%locals())
  gen = itertools.izip(*[t.GetVal(i) for i in xrange(ncol)])
  return itertools.islice(gen, nrow)


def sliced_header(t, rename=None):
  """
  The rename works similar to `pandas` package.
  - list: Must be exactly same range as params
  - dict: Selectively rename some.

  >>> _ = tree.Draw('mu_PT/1e3:pi_PT/1e3', '', 'goff')
  >>> tree.sliced_header()
  ['mu_PT/1e3', 'pi_PT/1e3']

  """
  ## some assertion beforehand
  if isinstance(rename, (list, tuple)):
    msg = "Need rename list (%i) of the same length as columns (%i)."
    n1  = len(rename)
    n2  = t.selectedCols
    assert n1 == n2, msg%(n1,n2)

  ## Start picking up the label
  acc  = []
  for i in xrange(t.selectedCols):
    val = str(t.GetVar(i).expFormula)
    val = val.replace('()','')
    ## custom rename
    if rename:
      if isinstance(rename, (list, tuple)):
        val = rename[i]
      if isinstance(rename, dict):
        if val in rename:
          val = rename[val]
    acc.append(val)
  return acc


def sliced_dataframe(t):
  """
  Return a DataFrame AFTER the result of TTree.Draw call.

  See also "How to obtain more info from TTree::Draw"
  """
  df = pd.DataFrame(list(t.sliced()))
  df.columns = t.sliced_header()
  return df


def sliced_tree(t, treename=None, rename_branches=None):
  if treename is None:
    treename = t.name
  ## Return new tree if empty
  rawarray = list(t.sliced())
  if not rawarray:
    return ROOT.TTree(treename, treename)
  rec = pd.np.rec.fromrecords(rawarray, names=t.sliced_header(rename_branches))
  return array2tree(rec, treename)

  ## TODO: Compat version: Using ROOT Only


def sliced_dataset(t, variables):
  """
  variables should be a list of RooRealVar such that the
  the variable title is the one used in Draw().

  The constraint should be simplified in the future

  """
  branches = {v.title:v.name for v in variables}
  t2 = t.sliced_tree(rename_branches=branches)
  ds = ROOT.RooFit.RooDataSet(t.name, t.title, t2, set(variables))
  return ds

#===============================================================================

def dataset( tree, param, cut=None ):
  """
  Return new instance of RooDataSet. Less syntax.

  Support only single param & single cut for now.

  If param is string, then the branch of same name is searched,
  and the result will be (dataset, roorealvar)

  If param is already RooRealVar, only the dataset is returned.


  Usage1: passing string::

    >>> ds,var = tree.dataset('mu_PT', 'nPVs==1')
    >>> ds
    <ROOT.RooDataSet object ("DitauCandTupleWriter/h1_mu") at ...>
    >>> var
    <ROOT.RooRealVar object ("mu_PT") at ...>

  Usage2: passing RooRealVar::

    >>> var = ROOT.RooRealVar('mu_PT', 'Impactparam', 0.)
    >>> tree.dataset(var)
    <ROOT.RooDataSet object ("DitauCandTupleWriter/h1_mu") at ...>

  Bad input:

    >>> tree.dataset(42)
    Traceback (most recent call last):
        ...
    ValueError: Invalid input. Expect string, RooRealVar

  """
  if isinstance(param, ROOT.RooRealVar):
    var = param
  elif isinstance(param, basestring):
    var = ROOT.RooRealVar(param, param, 0)
  else:
    raise ValueError('Invalid input. Expect string, RooRealVar')
  name  = tree.name
  title = tree.title
  logger.info('Converting TTree->RooDataSet: %s'%title)
  if cut:
    tree = tree.CopyTree(cut)
  ds = ROOT.RooDataSet(name, title, tree, {var})
  if isinstance(param, ROOT.RooRealVar):
    return ds
  return ds,var

#===============================================================================

def drop(tree, selection, by=[], ascending=[], index=['runNumber','eventNumber']):
  """
  - Given a tree, filter it first by given selection
  - Then sort the field by 'by' with order in 'ascending', see also pandas.DataFrame.sort_values
  - Then, save only the first entry if multiple existed in the index (event)

  Note: Needs root_numpy, pandas

  Usage:
    >>> tree.entries
    303L
    >>> tree2 = tree.drop('mu_PT>20e3', by=['mu_PT','pi_PT'], ascending=[False,False] )
    >>> tree2
    <ROOT.TTree object ("DitauCandTupleWriter/h1_mu_trimmed") at ...>
    >>> tree2.entries
    153L

  """

  ## 0. Possible to skip if there's no need
  ent, evt = tree.count_ent_evt(selection, index)
  if ent==evt:
    logger.info('Drop is unnecessary, return original.')
    return tree

  ## Casting
  by        = list(by)
  ascending = list(ascending)

  ## report
  logger.info('Tree      : %r (%r)'%(tree.name, tree.title))
  logger.info('Selection : %r'%selection)
  logger.info('Index     : %r'%index)
  logger.info('By        : %r'%by)
  logger.info('Ascend    : %r'%ascending)

  ## 1. Filter main selection, convert to recarray --> DataFrame
  df = tree.dataframe(selection)
  ## 2. Sort, ready to be dropped
  if by and ascending:
    df.sort_values(by=by, ascending=ascending, inplace=True)
  ## 3. Drop dup
  nbefore = len(df.index)
  df.drop_duplicates(index, inplace=True)
  nafter  = len(df.index)

  ## report
  logger.info('Trimmed   : %i --> %i --> %i' % (tree.entries, nbefore, nafter))

  ## 4. Convert back to tree
  t = array2tree(df.to_records(), name=tree.name+'_trimmed' )
  t.title = tree.title

  ## 5. Transfer the alias
  if tree.aliases:
    for x in tree.aliases:
      key = x.name 
      val = tree.GetAlias(key)
      t.SetAlias( key, val )

  ## Finally
  return t

#===============================================================================

def make_aliases_from_prefix(self, **kwargs):
  """
  Loop over all existing branches, if its name starts with `existing_prefix`,
  provide an alternative one of `new_prefix`

  Usage:
  >>> tree.make_aliases_from_prefix(mu_TOS_='TRIG_')
  {'TRIG_ELECTRON': 'mu_TOS_ELECTRON', 'TRIG_MUON': 'mu_TOS_MUON'}

  """
  acc = {}
  for branch in self.branches:
    oldname = branch.name
    for existing_prefix, new_prefix in kwargs.iteritems():
      if oldname.startswith(existing_prefix):
        newname = new_prefix + oldname[len(existing_prefix):]
        logger.debug('Aliasing: %s <-- %s'%(oldname, newname))
        self.SetAlias(newname, oldname)
        acc[newname] = oldname # report changes
  return acc

#===============================================================================

# def absorb_friends( tree ):
#   """
#   Return a new TTree with all its friends absorbed into it.
#   """
#   raise NotImplementedError
#   
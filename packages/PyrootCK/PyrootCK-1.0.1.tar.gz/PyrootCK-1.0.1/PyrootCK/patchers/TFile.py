#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import ROOT
import hashlib
import cStringIO
import subprocess
import multiprocessing
from glob import glob
from contextlib import contextmanager

from . import logger
from ..ioutils import tfile_seeker

#===============================================================================

@contextmanager
def open_metadata(fout):
  """

  Helper function to provide buffer object allowing metadata to be added into
  the desired TFile.
  The object should be simple (i.e, str, dict)

  Usage:

  >>> _ = getfixture('chtmpdir')
  >>> fout = ROOT.TFile('name.root', 'recreate')
  >>> with fout.open_metadata() as writer:
  ...   writer('hello world')
  ...   writer({'author': 'author', 'year': 2012, 'CoM (TeV)': 8, 'WG':'QEE'})
  >>> fout.Get('metadata')
  <ROOT.TCanvas object ("metadata") at ...
  >>> fout.Close()

  """
  output = cStringIO.StringIO()
  writer = lambda x: output.write(str(x)+'\n')
  #
  yield writer
  #
  stdout = output.getvalue()
  output.close()
  #
  p = ROOT.TCanvas('metadata')
  t = ROOT.TPaveText(0., 0., 1., 1.)
  t.textAlign = 12
  t.textFont  = 83
  t.textSize  = 12
  for line in stdout.split('\n'):
    t.AddText(line)
  t.Draw()
  ROOT.gPad.Update()
  p.Write()

#===============================================================================

# @staticmethod  # apply in patcher for correct pytest discovery.
def export_trees(trees, target, params=None, filt='',
                 dname=None, prepc=None, postpc=None, compression=None):
  """
  Export all given trees with branches in params into target root file, 
  with the filt applied.
  Put all these trees in the TDirectory dname if given.

  Args:
    trees (dict/list of TTree): Input tree. In case of dict, use key as treename.
    target (str): Output file.
    params (list of str): Branches to export
    filt (str): Selection string
    dname (str): Put tree in this ``TDirectory``
    prepc (callable): Pre-processing given (treename, tree), return tree.
    postpc (callable): Post-processing given (treename, tree), return tree.
    compression (int): For TFile.

  Doctest::

      Inputs:
      
      >>> fin = getfixture('tfile_ditau')
      >>> tree1 = fin.Get('DitauCandTupleWriter/h1_mu')
      >>> tree2 = fin.Get('DitauCandTupleWriter/h3_mu')
      >>> tree3 = fin.Get('DitauCandTupleWriter/e_mu')
      >>> _ = getfixture('chtmpdir')

      Export:
      
      >>> ROOT.TFile.export_trees(
      ...   trees  = [tree1, tree2, tree3],
      ...   target = 'temp.root',
      ...   params = ['M', 'nPVs', 'APT'],
      ...   filt   = 'mu_PT > 20e3',
      ... )

      pre/post-processor:

      >>> def prepc(tname, tree):
      ...   return tree
      >>> def postpc(tname, tree):
      ...   return tree

      Export:

      >>> ROOT.TFile.export_trees(
      ...   trees       = {'h1mu':tree1, 'h3mu':tree2, 'emu':tree3},
      ...   target      = 'temp.root',
      ...   params      = None,            # all branches
      ...   dname       = 'prelim',        # put trees in subdir
      ...   filt        = 'mu_PT > 100e3', # very harsh to handle empty tree
      ...   compression = 9,
      ...   prepc       = prepc,
      ...   postpc      = postpc,
      ... )

  """
  logger.info('Target: %s'%target)

  ## Prepare output file
  mode = 'RECREATE'
  if compression is not None:
    fout = ROOT.TFile(target, mode, '', compression)
  else:
    fout = ROOT.TFile(target, mode, '')
  if dname:
    if not fout.Get(dname):
      fout.mkdir(dname)
    fout.cd(dname)

  ## Persist trees
  param = ':'.join(params) if params else None

  ## Loop def
  if isinstance(trees, dict):
    gen = sorted(trees.iteritems())
  elif isinstance(trees, (list, tuple)):
    gen = sorted({t.name: t for t in trees}.iteritems())
  else:
    raise ValueError("Unknown iterable")

  ## Start looping
  for tname, tree in gen:
    logger.debug('Starting %s, %s'%(tname, tree))
    ## preprocessor & veto
    if prepc:
      tree = prepc(tname, tree)
    ## Skip empty tree:
    if tree.entries == 0:
      logger.warning('Skip empty tree before draw: %s'%tname)
      continue
    ## check entries after draw
    n = tree.GetEntries(filt)
    if n == 0:
      logger.info('Skip empty tree after draw: %s'%tname)
      continue
    tree.estimate = n+1

    ## Actual draw
    logger.debug('Processing %r expect [%i]'%(tname, n))
    if param: # some branch
      tree.Draw(param, filt, 'para goff')
      ## Slice after I'm sure it's non-null
      t2 = tree.sliced_tree(tname)
      t2.ownership = False
    else: # all branch
      if filt:
        ## don't do this: memory-resident tree cause leakage.
        # ROOT.gROOT.cd() # need before CopyTree to prevent src tree included into new file
        t2 = tree.CopyTree(filt)
        logger.debug('CopyTree completes')
        t2.name  = tree.name # to allow postpc to work on it
        t2.title = tree.title
      else:
        t2 = tree
      # t2.ownership = False

    ## postprocessor
    if postpc:
      logger.debug('Applying post-processor')
      t2 = postpc(tname, t2)
    ## cd again (I forgot why)
    fout.cd(dname) if dname else fout.cd()
    logger.debug('Start writing')
    t2.Write(tname, ROOT.TObject.kOverwrite)
    logger.info('Written: %s [%i]'%(tname,n))

  fout.ls()

  ## finally
  fout.Close()
  logger.info('Export completed: %s'%target)

#===============================================================================

def _extract_single(fpath, tname, params, selection, aliases, **kwargs):
  """
  Handle the memory with care.
  """
  logger.info('Reading: %s'%fpath)
  if fpath.startswith('root://'):
    fin = ROOT.TFile.Open(fpath)
  else:
    fin = ROOT.TFile(fpath)
  tree = fin.Get(tname)
  if not tree:
    logger.warning('Tree not found in %s, skip'%fpath)
    return
  ## Apply alias
  for s1, s2 in aliases.iteritems():
    tree.SetAlias(s1, s2)
  ## Be prepared for large tree, then draw
  tree.estimate = tree.entries+1
  param = ':'.join(params)
  tree.Draw(param, selection, 'para goff')

  ## extract to output file. Be careful of transient problem.
  fid   = hashlib.sha1(fpath).hexdigest()
  fname = 'extract_%s.root'%fid
  fout  = ROOT.TFile(fname, 'recreate')
  t2    = tree.sliced_tree()
  t2.Write()
  fout.Close()
  fin.Close()
  logger.info('Written: %s'%fname)


# @staticmethod
def slice_tree(src, tname, params, selection='', dest='extracted.root', aliases={}, nprocs=4):
  """
  Loop over input files, grab the tree, slice for given spec, write & hadd.
  More memory-friendly than the above version.

  Args:
    src (str): Path to TFile
    tname (str): Name of tree in that file.
    params (list of str): List of branches to export
    selection (str): Selection before export
    dest (str): Destination file name
    aliases (dict): For SetAlias on the trees before selection
    nprocs (int): Multiprocessing pools.

  Usage::

      >>> src = os.path.join(os.getcwd(), 'res/ditau.root')
      >>> _ = getfixture('chtmpdir')
      >>> ROOT.TFile.slice_tree(
      ...   src       = src,
      ...   tname     = 'DitauCandTupleWriter/h1_mu',
      ...   aliases   = {'PT1': 'mu_PT/1e3', 'PT2':'pi_PT/1e3'},
      ...   params    = ['M', 'PT1', 'PT2', 'APT'],
      ...   selection = 'PT1>20',
      ...   dest      = 'extracted.root',
      ... )
      hadd Target file: extracted.root
      hadd compression setting for all ouput: 1
      hadd Source file 1: extract_...
      hadd Target path: extracted.root:/
      <BLANKLINE>

  """

  ## Get clean area first
  for fpath in glob('extract*.root'):
    os.remove(fpath)
  ## Loop each, with concurrency
  files = tfile_seeker(src)
  pool  = multiprocessing.Pool(nprocs)
  acc   = []
  for fpath in files:
    args = fpath, tname, params, selection, aliases
    res = pool.apply_async(_extract_single, args=args)
    acc.append(res)
  pool.close()
  pool.join()
  for res in acc:
    res.get()

  ## hadd, then delete
  files = glob('extract_*.root')
  args  = ['hadd', dest] + list(files)
  print subprocess.check_output(args)
  for fpath in files:
    os.remove(fpath)
  logger.info('Sliced tree completed.')

#===============================================================================

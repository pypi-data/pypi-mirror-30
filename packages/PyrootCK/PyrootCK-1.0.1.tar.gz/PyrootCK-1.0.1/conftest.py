#!/usr/bin/env python

import os
import pytest
import ROOT
import pandas as pd
from uncertainties import ufloat
ROOT.gROOT.SetBatch(True)

#===============================================================================

@pytest.fixture(autouse=True, scope='session')
def add_imports(doctest_namespace):
  """
  Expose these import in the doctest.
  """
  fin = ROOT.TFile('res/ditau.root')
  tname = 'DitauCandTupleWriter/h1_mu'
  tree = fin.Get(tname)
  tree.name = tree.title = 'DitauCandTupleWriter/h1_mu'
  doctest_namespace['os']     = os
  doctest_namespace['tree']   = tree
  doctest_namespace['pd']     = pd
  doctest_namespace['ROOT']   = ROOT
  doctest_namespace['ufloat'] = ufloat
  yield
  fin.Close()

#===============================================================================
# IOUTILS
#===============================================================================

@pytest.fixture
def chtmpdir(tmpdir):
  """
  Temporary chdir to temp dir.
  """
  olddir = tmpdir.chdir()
  yield tmpdir
  olddir.chdir()

@pytest.fixture
def export_TFILEPATH(monkeypatch):
  path = '/panfs/USER:/home/USER/gangadir/workspace/USER/LocalXML'
  monkeypatch.setenv('TFILEPATH', path)

#===============================================================================

@pytest.fixture
def tfile_ditau():
  fin = ROOT.TFile('res/ditau.root')
  yield fin
  fin.Close()  

@pytest.fixture
def tfile_upperlim():
  fin = ROOT.TFile('res/upperlim.root')
  yield fin
  fin.Close()

@pytest.fixture
def roofitresult(tfile_upperlim):
  """
  Dummy instance of RooFitResult.
  """
  return tfile_upperlim.Get('mllres_keyspdf_tight_4pi_withsyst_125')

@pytest.fixture
def rooworkspace(tfile_upperlim):
  return tfile_upperlim.Get('mll_keyspdf_tight_4pi_withsyst_125')

@pytest.fixture
def th1f():
  """
  Dummy instance of TH1F, prepared with Poissonian error.
  """
  h = ROOT.TH1F('h', 'h', 4, 0, 4)
  h.binErrorOption = ROOT.TH1.kPoisson
  for _ in xrange(3):
    h.Fill(1)
  for _ in xrange(5):
    h.Fill(2)
  yield h
  h.Delete()

@pytest.fixture
def th2f():
  h = ROOT.TH2F('h2', 'h2', 3, 0, 3, 3, 0, 3)
  h.SetBinContent(1, 1, 1)
  h.SetBinContent(1, 2, 4)
  yield h
  h.Delete()

#!/usr/bin/env python
"""

Apply all the patching on ROOT here.
The auxiliary classes are only to provide unclustered namespace.

"""

from .. import logger, pyroot_zen
import functools
import ROOT  # reimport it directly outside lazy call.
logger.debug('Patching ROOT starts.')

#===============================================================================
# OUTER PATCH: EXTRA FUNCTIONALITY
#===============================================================================

from . import TNamed
ROOT.TNamed.SetTitle = TNamed.SetTitle(ROOT.TNamed.SetTitle)
del TNamed

from . import TList
ROOT.TList.Reverse = TList.Reverse
del TList

#-------------------------------------------------------------------------------

from . import TFile
ROOT.TFile.open_metadata = TFile.open_metadata
ROOT.TFile.slice_tree    = staticmethod(TFile.slice_tree)
ROOT.TFile.export_trees  = staticmethod(TFile.export_trees)
del TFile

#-------------------------------------------------------------------------------

from . import TTree
ROOT.TTree.count_ent_evt    = TTree.count_ent_evt
ROOT.TTree.dataset          = TTree.dataset
ROOT.TTree.dataframe        = TTree.dataframe
ROOT.TTree.drop             = TTree.drop
ROOT.TTree.selectedCols     = TTree.get_selected_cols
#
ROOT.TTree.make_aliases_from_prefix = TTree.make_aliases_from_prefix

ROOT.TTree.sliced           = TTree.sliced
ROOT.TTree.sliced_header    = TTree.sliced_header
ROOT.TTree.sliced_dataframe = TTree.sliced_dataframe
ROOT.TTree.sliced_tree      = TTree.sliced_tree
ROOT.TTree.sliced_dataset   = TTree.sliced_dataset

del TTree

#-------------------------------------------------------------------------------

from . import TAxis
ROOT.TAxis.bins      = property(TAxis.bins)  # doctest bug
ROOT.TAxis.GetLabels = TAxis.labels(ROOT.TAxis.GetLabels)
del TAxis

#-------------------------------------------------------------------------------

from . import TH1
ROOT.TH1.series    = TH1.series
ROOT.TH1.vlookup   = TH1.vlookup
del TH1

#-------------------------------------------------------------------------------

from . import TH2
ROOT.TH2.vlookup     = TH2.vlookup  
ROOT.TH2.dataframe   = TH2.dataframe
ROOT.TH2.from_uframe = classmethod(TH2.from_uframe)
del TH2

#-------------------------------------------------------------------------------

from . import TGraphErrors, TGraphAsymmErrors, TMultiGraph
ROOT.TGraphErrors.from_pair_ufloats = classmethod(TGraphErrors.from_pair_ufloats)
#
ROOT.TGraphAsymmErrors.dataframe         = TGraphAsymmErrors.dataframe
ROOT.TGraphAsymmErrors.series            = TGraphAsymmErrors.series
ROOT.TGraphAsymmErrors.from_pair_asymvar = classmethod(TGraphAsymmErrors.from_pair_asymvar)
ROOT.TGraphAsymmErrors.from_TH1          = classmethod(TGraphAsymmErrors.from_TH1)
#
ROOT.TMultiGraph.brazillian = classmethod(TMultiGraph.brazillian)
del TGraphErrors, TGraphAsymmErrors, TMultiGraph

#-------------------------------------------------------------------------------

from . import TMatrix
ROOT.TMatrixTSym('double').to_lists = TMatrix.to_lists
del TMatrix

#-------------------------------------------------------------------------------

# note: For some reason I don't yet understand, if `property` is delcared inside
# the TMinuit file the doctest will not be picked up.
from . import TMinuit
ROOT.TMinuit.parameters = property(TMinuit.parameters)
del TMinuit

#===============================================================================
# ROOFIT HOOK
#===============================================================================

def hook_wait_roofit(name):
  if name.startswith('Roo'):
    import __init_RooFit__
    pyroot_zen.entrypoints.at_cpp_lookup.remove('hook_wait_roofit') # expired

pyroot_zen.entrypoints.at_cpp_lookup.inject_before(hook_wait_roofit)
del hook_wait_roofit

#===============================================================================

## Finally
logger.info('Patching ROOT completed.')

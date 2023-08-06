#!/usr/bin/env python
"""

Provide patching for RooFit classes & functions.

Note: Don't use the separate handle anymore as it's more important to respect
the original namespace.

"""
import ROOT # vanilla handle
from . import logger
logger.debug('Patching RooFit starts.')

## Trigger RooFit library, one more time.
ROOT.RooFit

#===============================================================================
# OUTER PATCH
#===============================================================================

from . import RooFitResult
ROOT.RooFitResult.series = RooFitResult.series
del RooFitResult

## Additional retriever
from . import RooRealVar
ROOT.RooRealVar.ufloat = RooRealVar.ufloat
del RooRealVar

from . import RooWorkspace
ROOT.RooWorkspace.series                 = RooWorkspace.series
ROOT.RooWorkspace.PrintVars              = RooWorkspace.PrintVars
ROOT.RooWorkspace.factoryArgs            = RooWorkspace.factoryArgs
ROOT.RooWorkspace.load_from_RooFitResult = RooWorkspace.load_from_RooFitResult
del RooWorkspace

from . import RooDataHist
ROOT.RooDataHist.weights = RooDataHist.weights
del RooDataHist

#===============================================================================

logger.info('Patching RooFit completed.')

from __future__ import absolute_import
from .. import logger

## Expose these APIs
from .asymvar import asymvar
from .misc import sumq, weighted_average, covariance_matrix
from .efficiencies import Eff, EffU, EffU_unguard

## Optional import this one which requires pandas.
try:
  from .pandas import (
    weighted_harmonic_average, combine_fully_correlated, fast_combine_BLUE
  )
except ImportError, e: # pragma: no cover
  logger.warning(e)

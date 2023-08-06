"""

Improving PyROOT for more utils.

It helps me get through my PhD.

"""

__author__  = 'Chitsanu Khurewathanakul'
__email__   = 'chitsanu.khurewathanakul@gmail.com'
__license__ = 'GNU GPLv3'


## Core 3rd-party libs. Use namespacing as Zen told.
from PythonCK import logger
logger.setLevel(logger.INFO)

## Mandatory 3rd party, expose these API
from .patch_uncertainties import ufloat, var, isinstance_ufloat

## Non-lazy ROOT import & patch
import pyroot_zen  # 3rd party
import patchers
del pyroot_zen
del patchers

## Expose for fast usage
import os
import sys
import ROOT

## Expose these API
from ioutils import *

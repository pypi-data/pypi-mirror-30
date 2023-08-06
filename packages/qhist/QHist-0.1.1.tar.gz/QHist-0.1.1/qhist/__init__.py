"""

`QHist` -- A Quick Histogram drawer for `ROOT::TTree` for smoother HEP analysis!

"""

__author__  = 'Chitsanu Khurewathanakul'
__email__   = 'chitsanu.khurewathanakul@gmail.com'
__license__ = 'GNU GPLv3'

## Core 3rd-party libs.
from pyroot_zen import ROOT
from PythonCK import logger
logger.setLevel(logger.INFO)

## Apply (minimal) patching essential to this package, but not natural enough
# for pyroot_zen, and not forward enough for PythonCK
import patching

## Use this abstraction to mask the parent layers (v3 too long).
# from v2.core import QHist as QHistV2 # DEPRECATED
from v3.lifecycle import QHist

## Apply default style of QHist
import styles
styles.set_qhist_color_palette()

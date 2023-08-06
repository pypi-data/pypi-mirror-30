#!/usr/bin/env python
"""
Some patching is needed.
"""

import types
import ROOT

#===============================================================================

def normalize(self, nmz=True):
  """
  automatically perform h.Scale such that it fits the given normalization method.

  >>> ROOT.TH1F().normalize()   # do nothing for empty histogram
  0.0
  >>> h = getfixture('th1f')
  >>> h.normalize(True)  # normalize to one
  1.0
  >>> h.normalize(25.3)  # normalize to some number
  25.300...
  >>> h.normalize(False)  # do nothing
  25.300...
  >>> h.normalize(lambda x: 2*x)  # normalize relative to current integral.
  50.600...
  >>> h.normalize('flag')
  Traceback (most recent call last):
  ...
  ValueError: ...

  """
  intg = self.Integral()
  ## First, do nothing if this is empty histogram
  if intg == 0:
    return intg
  ## If it's False/None leave it be.
  if (nmz is False) or (nmz is None):
    return intg
  ## If it's boolean == True, renorm to 1 
  if nmz is True:
    self.Scale(1./intg)
    return 1.
  ## If it's some int/float value, do renorm to that value
  if isinstance(nmz, (int,float,long)):
    self.Scale(nmz/intg)
    return self.Integral()
  ## If it's a function (scalar -> scalar), attempt to call it
  if isinstance(nmz, types.FunctionType):
    self.Scale(nmz(intg)/intg)
    return self.Integral()
  ## Unknow strategy, raise me.
  raise ValueError('Unknown renormalization strategy: %r'%nmz)

#===============================================================================

ROOT.TH1.normalize = normalize

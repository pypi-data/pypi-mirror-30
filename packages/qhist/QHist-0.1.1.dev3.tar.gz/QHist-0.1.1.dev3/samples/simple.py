#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Simple examples.

## doctest will pick this up.
>>> main()
Finished successfully

"""

import atexit
import ROOT
from qhist import QHist
ROOT.gROOT.batch = True

def main():

  ## Load some tree first
  fin = ROOT.TFile('res/ditau.root')
  tree = fin.Get('DitauCandTupleWriter/h1_mu')
  atexit.register(fin.Close)
  tree.SetAlias('PT1', 'mu_PT/1e3')
  tree.SetAlias('PT2', 'pi_PT/1e3')
  tree.SetAlias('ISO1', 'mu_0.50_cc_IT')

  ## Base template
  H = QHist(auto_name=True)

  ## 1D simple
  h = H()
  h.trees = tree
  h.params = 'PT1'
  h.draw()

  ## 2D-nostack
  H(trees=tree, params='PT1:PT2', xmax=60, ymax=60, xlog=True, ylog=True, option='col').draw()

  ## 1D-prof
  H(trees=tree, params='ISO1:PT1', xmin=0, xmax=60, xbin=6, option='prof').draw()

  ## 1D-stacked
  Hst = H(trees=tree, params=['PT1','PT2'], xmin=0, xmax=60, xbin=24)
  Hst(name='1d_code1', st_code=1).draw()
  Hst(name='1d_code2', st_code=2).draw()

  ## finally
  print 'Finished successfully'

if __name__ == '__main__':
  main()
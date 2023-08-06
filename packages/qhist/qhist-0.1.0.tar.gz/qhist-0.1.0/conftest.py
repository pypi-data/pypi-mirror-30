#!/usr/bin/env python

import os
import shutil
import pytest
import ROOT
from glob import glob
from qhist import QHist
ROOT.gROOT.SetBatch(True)
# ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

#===============================================================================

@pytest.fixture(autouse=True, scope='session')
def add_imports(doctest_namespace):
  """
  Expose these import in the doctest.
  """
  doctest_namespace['ROOT'] = ROOT
  doctest_namespace['QHist'] = QHist

@pytest.fixture(autouse=True, scope='session')
def add_objects(doctest_namespace):
  """
  For README.md,
  prepare local variables to not disturb the example flow.
  Use the large TTree here only.
  """
  ## trees
  fin = ROOT.TFile('res/ditau.root')
  tree = fin.Get('DitauCandTupleWriter/h1_mu')
  tree.SetAlias('param', 'M')
  tree.SetAlias('cut'  , '0==0')
  doctest_namespace['tree'] = tree
  doctest_namespace['t1'] = tree
  doctest_namespace['t2'] = fin.Get('DitauCandTupleWriter/h3_mu')
  doctest_namespace['t3'] = fin.Get('DitauCandTupleWriter/e_mu')
  ## TPC triplets
  doctest_namespace['tpc'] = [
    ( tree, 'pi_BPVIP', 'pi_BPVIP > 0'),
    ( tree, 'mu_BPVIP', 'mu_BPVIP > 0'),
  ]
  ## Ready
  yield
  fin.Close()

@pytest.fixture(autouse=True, scope='session')
def cleanup():
  yield
  if os.path.exists('./py'): # residual drawing dir
    shutil.rmtree('./py')
  for fpath in glob('*.pdf'):
    os.remove(fpath)

#===============================================================================

@pytest.fixture
def freeze_time():
  """
  Context to freeze the current time to 2020-01-01.
  Don't use globally, as I have the timestamp inequality check.
  """
  from freezegun import freeze_time
  freezer = freeze_time('2020-01-01')
  freezer.start()
  yield
  freezer.stop()

@pytest.fixture
def os_path_abspath(monkeypatch):
  """
  Override to simple abspath.
  """
  monkeypatch.setattr(os.path, 'abspath', lambda path: '/'+path)

@pytest.fixture
def mainfile(os_path_abspath, monkeypatch):
  """
  Mock the execution filename.
  """
  import __main__
  monkeypatch.setattr(__main__, '__file__', 'mainfile', raising=False)

#===============================================================================

@pytest.fixture
def stats():
  """
  Provide mock Stats object
  """
  from qhist.v3.stats import ProtoSingleStats, Stats
  return Stats([ProtoSingleStats(entries=0, nbin=20,
    xmin=1, xmax=2, ymin=4, ymax=5, zmin=6, zmax=7, dim=3)])

@pytest.fixture
def th1f():
  """
  Dummy instance of TH1F, prepared with Poissonian error.
  """
  h = ROOT.TH1F('th1f', 'th1f', 4, 0, 4)
  h.binErrorOption = ROOT.TH1.kPoisson
  for _ in xrange(3):
    h.Fill(1)
  for _ in xrange(5):
    h.Fill(2)
  yield h
  h.Delete()

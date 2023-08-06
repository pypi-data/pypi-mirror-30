#!/usr/bin/env python

import pytest
from pyroot_zen import ROOT
ROOT.gROOT.SetBatch(True)

@pytest.fixture(autouse=True)
def add_ROOT(doctest_namespace):
  """
  Automatically import ROOT and make it available in the namespace of doctest.
  """
  doctest_namespace['ROOT'] = ROOT

@pytest.fixture
def sample_RooArgSet():
  """
  Return a sample RooArgSet for doctest
  """
  x = ROOT.RooRealVar('x', 'x', 0)
  y = ROOT.RooRealVar('y', 'y', 1)
  z = ROOT.RooRealVar('z', 'z', 2)
  x.ownership = False
  y.ownership = False
  z.ownership = False
  return ROOT.RooArgSet(x, y, z)

@pytest.fixture
def sample_RooArgList():
  """
  Return a sample RooArgList for doctest
  """
  x = ROOT.RooRealVar('x', 'x', 0)
  y = ROOT.RooRealVar('y', 'y', 1)
  z = ROOT.RooRealVar('z', 'z', 2)
  x.ownership = False
  y.ownership = False
  z.ownership = False
  return ROOT.RooArgList(x, y, z)

@pytest.fixture
def sample_RooCategory():
  cat = ROOT.RooCategory('my_category', 'MyCategory')
  cat.defineType('alpha')
  cat.defineType('beta')
  cat.defineType('gamma')
  return cat

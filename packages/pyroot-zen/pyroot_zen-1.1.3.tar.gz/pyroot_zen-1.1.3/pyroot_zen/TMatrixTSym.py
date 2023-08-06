#!/usr/bin/env python
# -*- coding: utf-8 -*-

def __iter__(self):
  """
  Limit the iteration to its length, not indefinitely.

  >>> mat = ROOT.TMatrixTSym('double')(2)
  >>> list(list(row) for row in mat)
  [[0.0, 0.0], [0.0, 0.0]]

  """
  for i in xrange(self.nrows):
    yield self[i]

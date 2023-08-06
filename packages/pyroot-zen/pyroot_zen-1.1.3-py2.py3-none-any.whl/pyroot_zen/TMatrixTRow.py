#!/usr/bin/env python
# -*- coding: utf-8 -*-

def __iter__(self):
  """
  Limit the iteration to its length, not indefinitely.
  """
  for i in xrange(self.GetMatrix().GetNcols()):
    yield self[i]

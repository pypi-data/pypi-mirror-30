#!/usr/bin/env python

import functools

def SetTitle(func):
  """
  Hack to make it return itself after completion. Used for chaining calls.
  """
  @functools.wraps(func)
  def wrap(self, title=''):
    func(self, title)
    return self 
  return wrap

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Misc helper function for TMVA

"""

import os
import re
import ROOT
from array import array
from glob import glob
from . import logger

#===============================================================================

class AssignArray(tuple):
  """
  Helper class to handle collection of array('f') instances,
  used for TMVA adapter below.

  Usage:

      >>> arr = AssignArray(4)
      >>> arr.set([1, 2, 3, 4])
      >>> for a in arr: print a
      array('f', [1.0])
      array('f', [2.0])
      array('f', [3.0])
      array('f', [4.0])

  """

  def __new__(cls, n):
    """
    Args:
      n (int): number of slots to instantiate.

    """
    tup = tuple([array('f',[0.]) for i in xrange(n)])
    return super(AssignArray, cls).__new__(cls, tup)

  def set(self, values):
    """
    Args:
      values (list): List of number (int/float) to set into arrays.
    """
    assert len(values) == len(self)
    for val,arr in zip(values, self):
      arr[0] = val

#-------------------------------------------------------------------------------

class TMVA_Adapter(object):
  """
  Helper class to facilitate the binding stages in TMVA analysis.
  Keep the reference to attached object.

  """
  def __init__(self, pairs_param_label):
    """
    Args:
      pairs_param_label (list): list of pair (str, str), representing expression
                                and labels.
    """
    params, labels      = zip(*pairs_param_label)
    self.params         = tuple(params)
    self.labels         = tuple(labels)
    self.arrays_reader  = tuple()
    self.booked_methods = list()

  def _evaluate_all_mva(self, methods):
    """
    Given the current state of arrays_reader, return the evaluated values from
    all booked methods
    """
    return [self.reader.EvaluateMVA(method) for method in methods]

  ## New paradigm uses DATALOADER
  # @property
  # def factory(self):
  #   return self._factory
  # @factory.setter
  # def factory(self, factory):
  #   """Loop over AddVariable call. Ignore other fields. Default to float 'F' """
  #   self._factory = factory
  #   for param,label in zip(self.params, self.labels):
  #     self._factory.AddVariable(param, label, '', 'F')

  @property
  def reader(self):
    return self._reader

  @reader.setter
  def reader(self, reader):
    """
    To export value in arrar.f to reader.
    """
    self._reader = reader
    self._reader.ownership = False
    ## initialize the slot for floats
    self.arrays_reader = AssignArray(len(self.params))
    ## attach the vars
    for param, arr in zip(self.params, self.arrays_reader):
      reader.AddVariable(param, arr)

  def book_reader_dir(self, dpath, prefix=None):
    """
    Given the directory containing weights xml, book all of them to the current
    reader.

    Args:
      dpath (str): path to directory containing ``*.weights.xml``
      prefix (str): additional prefix to add before insert into ``Reader.BookMVA``.

    """
    ## Check first that dir makes sense
    res = list(glob(os.path.join(dpath, '*.weights.xml')))
    if not res:
      raise ValueError('Directory contains no weights file. Check me: %s'%dpath)
    ## Loop over all weights files
    for fpath in res:
      # Fetch the actual name, found inside
      name = None
      with open(fpath) as fin:
        for line in fin:
          if 'MethodSetup' in line:
            name = re.findall(r'<MethodSetup Method="\S+::(\S+)"', line)[0]
            break
      if name is None:
        raise ValueError('Cannot find a name in the XML schema.')
      # Provide optional prefix
      if prefix:
        name = prefix + '_' + name
      # Ready to book. No need for explicit logger. TMVA does it.
      self.booked_methods.append(name)
      self.reader.BookMVA(name, fpath)


  def make_weights(self, tree, name='weights', methods=[]):
    """
    Given the source tree, loop over it to obtain the corresponding MVA values
    from the booked method, collect those result into new Tree, make friend with
    the input tree, and return the friend tree.

    Because this can be large, try to stay inside ROOT framework, not 3rd-party.
  
    Args:
      tree (``ROOT.TTree``): Tree containing input vars
      name (str): Name of the output weight tree
      methods (list of str): List of MVA response methods to use, default to all.

    """

    ## Prepare output tree
    if not methods:
      methods = self.booked_methods

    logger.info('List of methods: %s'%str(methods))
    arrays_writer = AssignArray(len(methods))
    tf = ROOT.TTree(name, name)
    # tf.ownership = False
    for method, arr in zip(methods, arrays_writer):
      tf.Branch(method, arr, method+'/F')

    ## Loop over each entry
    param = ':'.join(self.params)
    n = float(tree.Draw(param, '', 'para goff'))
    logger.info('Making weights: %-10s [%3i]'%(tree.title, n))
    j = 1
    for i,row in enumerate(tree.sliced()):
      ## progress report, every 20%
      if (5.*i/n) > j:
        j += 1
        logger.info('Fill progressed: {:.0%}'.format(i/n))

      # Bind into arrays_reader
      self.arrays_reader.set(row)

      # Read back MVA, set to the writer arrays, new Tree is ready to be filled
      arrays_writer.set(self._evaluate_all_mva(methods))
      tf.Fill()

    ## Make friend & return
    # tree.AddFriend(tf)
    return tf

#===============================================================================
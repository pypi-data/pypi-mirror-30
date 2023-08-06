#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Shelf is an underlying persistence for decorator `cache_to_file` where the
expiration is also persisted.

"""

import os
import hashlib
import pickle
import shelve
import atexit
import shutil
from glob import glob
from datetime import datetime
from collections import MutableMapping

## Local
from .. import logger
from .safe_makedir import safe_makedir

#===============================================================================

# class Entry(object):
#   """Represent schema upon retrieval from Shelf."""
#   __slots__ = ( 'key', 'hashkey', 'val', 'mtime' )

#-------------------------------------------------------------------------------

class ShardedShelf(MutableMapping):
  """
  Persist EACH keys into individual file, via `pickle`.
  """

  def __init__(self, shelfid):
    # This shelfid is path/funcName, make directory out of it
    super(ShardedShelf, self).__init__()
    self._dirname = shelfid
    if not os.path.exists(shelfid):
      safe_makedir(shelfid)

  def __contains__(self, key):
    logger.debug('key   : %s'%key)
    logger.debug('target: %s'%self._target(key))
    return os.path.exists(self._target(key))

  def __getitem__(self, key):
    """Return ( value, moditfed time )"""
    target = self._target(key)
    mtime  = datetime.fromtimestamp(os.stat(target).st_mtime)
    with open(target, 'rb') as fin: # 'rb' for python3 compat
      _,val = pickle.load(fin)
    return val, mtime

  def __setitem__(self, key, val):
    """
    Set the file ( put in both key-val because of non-reversible hashing )
    """
    with open(self._target(key), 'wb') as fout:
      pickle.dump((key,val), fout)

  def __delitem__(self, key):
    os.remove(self._target(key))

  def __iter__(self):
    """
    Return all keys (not the hashed path)
    """
    acc = []
    for target in glob(os.path.join(self._dirname, '*')):
      with open(target, 'rb') as fin: # 'rb' for python3 compat
        acc.append(pickle.load(fin)[0]) # (unhashedkey,val)
    ## Make sure it's sorted.
    for x in sorted(acc):
      yield x

  def __len__(self):
    return len(os.listdir(self._dirname))

  def _target(self, key):
    """Return fullpath of cache file."""
    fname = hashlib.sha1(key.encode('utf-8')).hexdigest()
    return os.path.join(self._dirname, fname)

  def __str__(self):
    """Show nice entry store, inspired by GAE."""
    return '\n'.join(x for x in self)

  def clear(self):
    """Remove all cache."""
    shutil.rmtree(self._dirname)
    safe_makedir(self._dirname)

#-------------------------------------------------------------------------------

class UnshardedShelf(MutableMapping):
  """
  Persist ALL keys into single file, via `shelve`.
  """

  def __init__(self, shelfid):
    super(UnshardedShelf, self).__init__()
    self._shelf = shelve.open(shelfid)  # writeback=writeback, flag='c')
    atexit.register(self._shelf.close)

  def __getitem__(self, key):
    return self._shelf[key] # In a shelf, it's (obj,mtime)

  def __setitem__(self, key, val):
    self._shelf[key] = val, datetime.now() # Put mtime too

  def __delitem__(self, key):
    del self._shelf[key]

  def __iter__(self):
    ## Make sure it's sorted.
    for x in sorted(list(iter(self._shelf))):
      yield x

  def __len__(self):
    return len(self._shelf)

  def __str__(self):
    return '\n'.join(x for x in self)

  def clear(self):
    """Remove all cache."""
    for k in self._shelf:
      del self._shelf[k]

#===============================================================================

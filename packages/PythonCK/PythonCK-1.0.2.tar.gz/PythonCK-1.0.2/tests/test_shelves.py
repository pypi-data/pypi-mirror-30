#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from PythonCK.decorators.shelves import ShardedShelf, UnshardedShelf

@pytest.mark.parametrize('cls, shelfid', (
  [ShardedShelf  , 'path/funcname'],
  [UnshardedShelf, 'funcname'],
))
def test_shelf(cls, shelfid, chtmpdir):
  """
  Trying both classes of same interface.
  """

  ## initial state
  shelf = cls(shelfid)
  assert 'key' not in shelf

  ## 1 key
  shelf['key'] = 'val'
  assert 'key' in shelf
  assert len(shelf) == 1
  assert shelf['key'][0] == 'val'

  ## 2 keys
  shelf['key2'] = 'val2'
  assert shelf['key2'][0] == 'val2'
  assert len(shelf) == 2
  shelf['key2'] = 'newval'
  assert shelf['key2'][0] == 'newval'
  assert list(shelf) == ['key', 'key2']
  assert str(shelf) == 'key\nkey2'

  ## Deleting
  del shelf['key']
  assert 'key' not in shelf
  shelf.clear()
  assert len(shelf)==0

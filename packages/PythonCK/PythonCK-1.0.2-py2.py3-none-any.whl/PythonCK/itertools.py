#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Collections of useful iteration-related tools, just like default `itertools`

"""

# rather than relative import
from __future__ import absolute_import
from six import string_types

from itertools import chain, combinations
import collections

#------------------------------------------------------------------------------

def chunks(l, n):
  """
  Yield successive n-sized chunks from l.

  Args:
    l (iterable): Itrable instance to be splitted into chunks .
    n (int): Len of each chunk.

  Usage::

    >>> result = chunks( range(10), 3 )
    >>> result
    <generator object chunks at ...>
    >>> list(result)
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

  REF:
  
  - http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python

  """
  l = list(l)
  for i in range(0, len(l), n):
    yield l[i:i+n]

#-------------------------------------------------------------------------------

def flatten(l):
  """
  Better handling with generator for arbitary-depth list flattening.
  (In exchange for speed penalty).

  https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python

  Args:
    l (iterable): Iterable instance to be flatten.

  Usage::

    >>> flatten( [1, 2, (3, 4), [5]] )
    <generator object flatten at ...>

    >>> list(flatten( [1, 2, (3, 4), [5]] ))
    [1, 2, 3, 4, 5]

    >>> list(flatten(123)) # not iterable, return simply list of that object
    [123]

  """
  if not isinstance(l, collections.Iterable):
    yield l
  else:
    for el in l:
      if isinstance(el, collections.Iterable) and not isinstance(el, string_types):
        for sub in flatten(el):
          yield sub
      else:
        yield el

#-------------------------------------------------------------------------------

def powerset(iterable):
  """
  Return the powerset of given iterable.

  Usage::

    >>> result = powerset([1, 2, 3])
    >>> result
    <itertools.chain object at ...>
    >>> list(result)
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]

  """
  l = list(iterable)
  return chain.from_iterable(combinations(l, r) for r in range(len(l)+1))

#-------------------------------------------------------------------------------

def merge_dicts(*dicts):
  """
  Merge the dictionary recursively

  Used prominently in combining the recipe in `gaudi_simulation.py`

  Usage::

    >>> d = merge_dicts( {1:1}, {2:2} )
    >>> sorted(d.items())
    [(1, 1), (2, 2)]

    >>> merge_dicts( {1:1}, {1:2} )
    Traceback (most recent call last):
      ...
    Exception: Conflict ...

    >>> d = merge_dicts( {1: {100:100}}, {1: {200:200}} )
    >>> d == { 1: {100:100, 200:200} }
    True

    >>> merge_dicts( {1:1}, {1:1} )
    {1: 1}
    >>> merge_dicts( {1:[1]}, {1:[2]} )
    {1: [1, 2]}

  """
  from functools import reduce
  return reduce(_merge_dict, dicts)

def _merge_dict(a, b, path=None):
  """Merges b into a."""
  if path is None:
    path = []
  for key in b:
    if key in a:
      if a[key] == b[key]:
        pass  # same leaf value
      elif isinstance(a[key], dict) and isinstance(b[key], dict):
        _merge_dict(a[key], b[key], path + [str(key)])
      elif isinstance(a[key], list) and isinstance(b[key], list):
        a[key].extend(b[key])  # They're both a list, combine their members
      else:
        raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
    else:
      a[key] = b[key]
  return a

#-------------------------------------------------------------------------------

class EnumElement(str):
  """
  Base clss for enumeration object
  """
  __slots__ = ()

  def __getattr__(self, s):
    return s == self

class EnumContainer(tuple):
  """
  Constructor for enumeration-pattern, subclassing tuple

  Usages:

  >>> TauTypes = EnumContainer('e', 'h1', 'h3', 'mu', 'other')
  >>> TauTypes
  ('e', 'h1', 'h3', 'mu', 'other')
  >>> isinstance( TauTypes, tuple )
  True

  >>> mytautype = TauTypes('h1')    # Constructor style init
  >>> mytautype = TauTypes.h1       # Attribute style init
  >>> TauTypes('BAD')
  Traceback (most recent call last):
    ...
  AttributeError: No element named: "BAD" in this enum.

  >>> mytautype
  'h1'
  >>> mytautype == 'h1'   # String-based check
  True
  >>> mytautype.h1        # Attr-based check
  True
  >>> mytautype == 'h3'   # This check should return False
  False
  >>> mytautype == 'UNKNOWN'
  False
  >>> mytautype + 'h1' # concat
  'h1h1'
  >>> TauTypes.index(mytautype)  # Get int-index
  1

  """
  __slots__ = ()

  def __new__(cls, *args):
    # need to go deeper than init
    return tuple.__new__(cls, args)

  def __getattr__(self, s):
    if s in self:
      return EnumElement(s)
    raise AttributeError('No element named: "%s" in this enum.'%s)

  def __call__(self, s):
    return self.__getattr__(s)

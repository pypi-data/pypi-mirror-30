#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Collection of lazy (caching) decorators

"""

import functools
import types

## Local
from .. import logger

#===============================================================================
# MEMORIZED
#===============================================================================

def memorized(func):
  """
  Memorize the computed result of this function until the end of session::

    ## Define
    >>> @memorized
    ... def f_mem(arg1, arg2):
    ...   return arg1+arg2

    ## Check consistency
    >>> x1 = f_mem(10, arg2=20)
    >>> x2 = f_mem(10, arg2=20)
    >>> x1 == x2
    True

  """
  ## record the path to defined location first.
  # may not be the same as calling location
  defpath = func.__globals__['__file__']

  @functools.wraps(func)
  def wrap(*args, **kwargs):
    """
    Make args+kwargs into immutable key, save in globals
    """
    rawkey = ['__memorized_', defpath, func.__name__]
    if args:
      rawkey.append(args)
    if kwargs:
      rawkey.append(frozenset(sorted(kwargs.items())))
    key = str(rawkey)
    if key not in globals():
      logger.debug('memorized: write new key: '+key, extra=logger.extra(func))
      val = func(*args, **kwargs)
      globals()[key] = val
    return globals().get(key)
  ## Conflict with pytest, find another way
  # wrap.func_globals['__file__'] = func.func_globals['__file__']
  return wrap

#===============================================================================
# LAZY-INSTANCE
#===============================================================================

def lazy_instance(func):
  """
  To be used on the function that return some instance. The function will delay
  its call until its resultant instance is used (via __getattr__).
  A prime example is PyrootCK.import_tree.

  Usage::

    >>> IS_INIT = False

    >>> class Heavy(object):
    ...   def __init__(self):
    ...     global IS_INIT
    ...     IS_INIT = True
    ...   def foo(self):
    ...     return 42

    >>> @lazy_instance
    ... def get_heavy():
    ...   return Heavy()

    >>> x = get_heavy()
    >>> IS_INIT
    False
    >>> x
    <PythonCK.decorators.lazy...>
    >>> x.foo()
    42
    >>> IS_INIT
    True

    ## Triggered by setter
    >>> IS_INIT = False
    >>> y = get_heavy()
    >>> IS_INIT
    False
    >>> y.attr = 'val'
    >>> IS_INIT
    True
    >>> y.attr
    'val'

  """

  # @functools.wraps(func)
  class Wrap(object):
    """
    Actual wrap logic
    """
    __slots__ = 'obj', 'args', 'kwargs'

    def __init__(self, *args, **kwargs):
      self.obj    = None
      self.args   = args
      self.kwargs = kwargs

    def __getattr__(self, key):
      if self.obj is None:
        self.obj = func(*self.args, **self.kwargs)
      return getattr(self.obj, key)

    def __setattr__(self, key, val):
      if key in self.__slots__:
        super(Wrap, self).__setattr__(key, val)
      else:
        if self.obj is None:
          self.obj = func(*self.args, **self.kwargs)
        return setattr(self.obj, key, val)
  return Wrap

#===============================================================================
# LAZY PROPERTY
#===============================================================================

def lazy_property(func):
  """
  Lazy function, only for *getter* instance-method!

  Usage:

  >>> class Foo(object):
  ...   slow_count = 0
  ...   @lazy_property
  ...   def slow(self):
  ...     self.slow_count += 1
  ...     return 'some slow result'

  >>> foo = Foo()
  >>> foo.slow_count
  0
  >>> foo.slow
  'some slow result'
  >>> foo.slow_count # increase
  1
  >>> foo.slow
  'some slow result'
  >>> foo.slow_count  # not increase anymore!
  1

  """
  attr_name = '_lazy_' + func.__name__

  @property
  @functools.wraps(func)
  def _lazyprop(self):
    if not hasattr(self, attr_name):
      val = func(self)
      assert not isinstance(val, types.GeneratorType), "Don't use this with iterator!!"
      setattr(self, attr_name, val)
    return getattr(self, attr_name)
  return _lazyprop

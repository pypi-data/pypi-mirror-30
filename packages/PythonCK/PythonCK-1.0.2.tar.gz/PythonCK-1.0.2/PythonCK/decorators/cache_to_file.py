#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

``cache_to_file`` and underlying shelf (dict with timestamp).

"""

import os
import atexit
import inspect
import tempfile
from datetime import datetime, timedelta
from six import string_types

## Local
from .meta import AbstractClassbasedDecorator
from .safe_makedir import safe_makedir
from .shelves import ShardedShelf, UnshardedShelf

#===============================================================================

def safe_name(func):
  """
  Return safe name to be used as identifier.
  """
  tag = func.__module__
  if tag == '__main__':  # pragma: no cover
    tag = inspect.stack()[-1][1].replace('./','').replace('/','.')
  return tag

#===============================================================================


## Sentinel undefined.
UNDEFINED = ()

class cache_to_file(AbstractClassbasedDecorator):
  """
  Cache the result of this function, persist on the disk (using pickle/shelve).

  Extra flag: ``force_reload``

  If flag ``force_reload=True`` is given additionally into decorated function,
  the wrapped function will be called regardless of the cache even if it's
  available. This is useful in case where the user intent to refresh the
  cache to newer value, as well as prolonging cache expiredate.

  Extra flag: ``early_giveup``

  If flag ``early_giveup=True`` is given additionally into decorated function,
  the wrapped function will return None immediately if there's no cache
  available before this call. This is useful in the situation where it's
  antipicated that the function call will be slow (expensive), and the
  calling can be postponed to better context.
  - If cache is already expired, early_giveup will also return None.
  - The default return value is None

  Note:
    ``force_reload`` and ``early_giveup`` are mutually exclusive.
    Exception will be raised if both of them are True simultaneously.

  Note:
    Cannot be used on instance.method?

  Args:
    basedir (str): Name of the directory where the cache should reside.
                    If None, this will be determined automatically.

    timeout (int): Timeout until the cache expire, in seconds.

    input_skip_write (None, bool, callable): Input-dependent callback which,
        if true, will not persist the cache.

    output_skip_write (None, bool, callable): Output-dependent callback which,
        if true, will not persist the cache.

    sharding (bool): If True, instead of collection calls from same function
                      into one shelve, shards the result into single-pickled-file,
                      one file per one unique input. This is better in term of
                      concurrency, but may make directory more dirty...

  Usages:

    >>> func = getfixture('f_cache_to_file')
    >>> func.counter        # hits & misses
    (0, 0)
    >>> func(111)           # simple call
    ((111,), {})
    >>> func.counter        # one miss
    (0, 1)
    >>> func.contains(111)  # it's cached
    True
    >>> _ = func(111)       # call again, expect hit
    >>> func.counter
    (1, 2)
    >>> _ = func(222)       # call with second key
    >>> func.contains(222)
    True
    >>> func.counter
    (1, 3)
    >>> _ = func(222)       # call with second key, again
    >>> func.contains(222)
    True
    >>> func.counter
    (2, 4)
    >>> func(111)           # call with 1st key, again
    ((111,), {})
    >>> func.contains(111)
    True
    >>> func.counter
    (3, 5)

    >>> func(111, force_reload=True)    # Using force_reload
    ((111,), {})
    >>> func.counter
    (3, 6)
    >>> func(333, early_giveup=True)    # Using early_giveup

    >>> func.contains(333)
    False
    >>> func.counter
    (3, 6)
    >>> _ = func(333)  # now there's cache
    >>> func(333, early_giveup=True)
    ((333,), {})
    >>> func.counter
    (4, 8)

    >>> func('arg', kw='kwarg')   # same thing for kwargs
    (('arg',), {'kw': 'kwarg'})
    >>> func.counter
    (4, 9)

  """

  __slots__ = (
    '_count_hit',
    '_count_total',
    '_extra',
    '_isw',
    '_osw',
    '_shelfid',
    '_shelf',
    '_timeout',
  )

  def _setup(self, basedir=tempfile.gettempdir(), timeout=None, input_skip_write=UNDEFINED, output_skip_write=UNDEFINED, sharding=True):
    ## Some validation
    self._validate(input_skip_write, output_skip_write)

    ## Establish destination & shelfid
    self._count_hit   = 0
    self._count_total = 0
    self._timeout     = timeout
    self._isw         = input_skip_write
    self._osw         = output_skip_write
    self._sharding    = sharding

    ## Making shelf id (as well as the directory)
    outdir = safe_makedir(basedir)
    module = safe_name(self.func)
    self._shelfid = os.path.join(outdir, module+'.'+self.func.__name__)

    ## Finally
    # functools.update_wrapper(self, func)
    atexit.register(self.report_stats)

  @staticmethod
  def _validate(isw, osw):
    """
    Validate the input/output filter.

    >>> _  = getfixture('chtmpdir')

    ## Bad input filter
    >>> f = cache_to_file(func0, basedir='.', input_skip_write={})
    Traceback (most recent call last):
    ...
    ValueError: Bad filter: {} <dict>

    """
    for arg in (isw, osw):
      b1 = isinstance(arg, (type(None), bool))
      b2 = callable(arg)
      b3 = arg == UNDEFINED
      if not any([b1, b2, b3]):
        raise ValueError('Bad filter: %r <%s>'%(arg, arg.__class__.__name__))

  def __setitem__(self, args_kwargs, result):
    """
    Backdoor interface to allow putting data into shelf directly without
    need for a call to host function at all.

    Useful for case where batch-call is prefered, but optimize caching
    for single entry from the batch.

    Accept 2 style of keys:
      - ready-key, made via staticmethod `makekey`
      - raw-key, compose of 2-tuple of (args,kwargs)

    Usage:
      >>> func = getfixture('f_cache_to_file')

      >>> func.contains(111)
      False
      >>> func[(111,),{}] = 111     # Set args,kwargs and results manually
      >>> func.contains(111)
      True
      >>> func.counter
      (0, 0)
      >>> func(111)                 # a new call should hit instantly
      111
      >>> func.counter
      (1, 1)

      >>> key = func.makekey('arg', kw='kwarg')   # Another set style, via makekey
      >>> func[key] = 'key_via_makekey'
      >>> func.counter
      (1, 1)
      >>> func('arg', kw='kwarg')
      'key_via_makekey'
      >>> func.counter  # hit instantly
      (2, 2)

      >>> func[1] = 2   # Other case is not accepted
      Traceback (most recent call last):
      ...
      ValueError: Invalid key for backdoor __setitem__


    """
    if isinstance(args_kwargs, string_types):
      key = args_kwargs
    elif isinstance(args_kwargs, (tuple,list)) and len(args_kwargs) == 2:
      args, kwargs = args_kwargs
      key = self.makekey(*args, **kwargs)
    else:
      raise ValueError('Invalid key for backdoor __setitem__')
    self.shelf[key] = result  # Store back. Timestamp is handled by shelf's interface

  @property
  def shelfid(self):
    return self._shelfid

  @property
  def shelf(self):
    """
    Use for cache-viewer.
    Lazily create shelf (instead of opening dangle shelf when func is defined
    but unused)
    """
    if not hasattr(self, '_shelf') or self._shelf is None:
      cls = ShardedShelf if self._sharding else UnshardedShelf
      self._shelf = cls(self.shelfid)
      self._logd('Open shelf: ' + self.shelfid)
    return self._shelf

  @property
  def counter(self):
    """
    Return the hit/total stats of this cacher.
    """
    return self._count_hit, self._count_total

  @staticmethod
  def makekey(*args, **kwargs):
    """
    Handle making unique key from args, kwargs,
    exact signature like a function.
    """
    return str((args, frozenset(sorted(kwargs.items()))))

  def contains(self, *args, **kwargs):
    """
    Return True if given args-kwargs has been cached.

    >>> func = getfixture('f_cache_to_file')
    >>> func.contains(0)
    False
    >>> _ = func('111')
    >>> func.contains('111')
    True
    >>> func.contains('111', kw=222)
    False

    """
    if not self.shelf:
      return False
    return self.makekey(*args, **kwargs) in self.shelf

  def report_stats(self):
    """
    Report the hit/total stats.

    >>> f = getfixture('f_cache_to_file')
    >>> c = getfixture('caplog2')
    >>> _ = f(42)
    >>> _ = f(42)
    >>> f.report_stats()
    >>> c.record_tuples[-1][-1]
    'cache_to_file: Hit rate : 1/2 = 0.50'

    """
    hit,total = self.counter
    rate      = '%.2f'%(1.*hit/total) if total else 'N/A'
    if total:  # Report only non-trivial case
      self._logd('Hit rate : %i/%i = %s'%(hit,total,rate))

  def timeleft(self, key):
    """
    Given a key of the shelf, return the time left until the cache is expired.
    Used in auxiliary method cache viewer::

      >>> f = getfixture('f_cache_to_file')

      ## By default, there's no cache time-out
      >>> _ = f(42)
      >>> f.timeleft(f.makekey(42)) is None
      True

      ## Check the timeout
      >>> _ = getfixture('chtmpdir')
      >>> f = cache_to_file(func0, timeout=60, basedir='.')
      >>> _ = f(42)
      >>> f.counter
      (0, 1)
      >>> t = f.timeleft(f.makekey(42)).seconds
      >>> (t > 0) and (t < 3600)
      True
      >>> _ = f(42) # try again, without timeout
      >>> f.counter
      (1, 2)

    """
    if not self._timeout:  # no expiration
      return None
    _,mtime = self.shelf[key]
    return timedelta(seconds=self._timeout) - (datetime.now() - mtime)

  def is_expired(self, time_last):
    """
    Return True if data already expired. False (not expired) if timeout not given

    >>> from datetime import datetime, timedelta
    >>> _ = getfixture('chtmpdir')
    >>> f = cache_to_file(func0, timeout=3600, basedir='.')
    >>> f.is_expired(datetime.now())
    False
    >>> f.is_expired(datetime.now()-timedelta(10000))
    True
    >>> f.is_expired(None)
    True

    """
    if self._timeout is None or self._timeout < 0:
      return False
    if not time_last:  # Missing time_last is treated as expired
      return True
    return (datetime.now() - time_last) > timedelta(seconds=self._timeout)

  def _do_write_isw(self, *args, **kwargs):
    """
    Return True if, judging from inputs & skipping, this call
    should be written to shelf.

    >>> _ = getfixture('chtmpdir')

    ## Scalar filter
    >>> f = cache_to_file(func0, basedir='./scalar1', input_skip_write=False)
    >>> _ = f(True)
    >>> f.contains(True)
    True
    >>> _ = f(False)
    >>> f.contains(False)
    False
    >>> _ = f(0)
    >>> f.contains(0)  # 0 != False
    True
    >>> _ = f('')
    >>> f.contains('')  # '' != False
    True

    >>> f = cache_to_file(func0, basedir='./scalar2', input_skip_write=None)
    >>> _ = f(None)
    >>> f.contains(None)
    False

    ## Callable filter
    >>> def filter(*args, **kwargs):
    ...   return args[0] == 'SKIP'
    >>> f = cache_to_file(func0, basedir='.', input_skip_write=filter)

    >>> _ = f('SKIP')
    >>> f.counter
    (0, 1)
    >>> f.contains('SKIP')
    False
    >>> _ = f('SKIP')
    >>> f.counter # miss
    (0, 2)
    >>> _ = f('NORMAL')
    >>> f.counter # miss
    (0, 3)
    >>> f.contains('NORMAL')
    True
    >>> _ = f('NORMAL')
    >>> f.counter # hit
    (1, 4)
    >>> _ = f('SKIP')
    >>> f.counter # miss
    (1, 5)

    """
    isw = self._isw
    if isw == UNDEFINED:
      return True
    if isw is None:
      return args[0] is not None
    if isinstance(isw, bool):
      t = type(isw)
      b1 = all(bool(x)==isw and type(x)==t for x in args)
      b2 = all(bool(x)==isw and type(x)==t for x in kwargs.values())
      return not (b1 and b2)
    if hasattr(isw, '__call__'):
      return not isw(*args,**kwargs)
    ## This should have been detected since _setup
    raise ValueError('Unknown ISW strategy.') # pragma: no cover

  def _do_write_osw(self, result):
    """
    Return True if, judging from outputs & skipping, this call
    should be written to shelf.

    >>> _ = getfixture('chtmpdir')
    >>> func0 = lambda x: x

    ## Scalar filter

    >>> f = cache_to_file(func0, basedir='./bool1', output_skip_write=None)
    >>> _ = f(True)
    >>> f.contains(True)
    True
    >>> _ = f(False)
    >>> f.contains(False)
    True
    >>> _ = f(None)
    >>> f.contains(None)
    False

    >>> f = cache_to_file(func0, basedir='./bool2', output_skip_write=False)
    >>> _ = f(False)
    >>> f.contains(False)
    False
    >>> _ = f(None)
    >>> f.contains(None)
    True


    ## Callable filter

    >>> filter = lambda result: result is None
    >>> f = cache_to_file(func0, basedir='./call', output_skip_write=filter)
    >>> _ = f('NORMAL')
    >>> f.counter
    (0, 1)
    >>> _ = f(None)
    >>> f.contains(None)
    False
    >>> f.counter
    (0, 2)
    >>> _ = f(None)
    >>> f.counter
    (0, 3)

    """
    osw = self._osw
    if osw == UNDEFINED:
      return True
    if osw is None:
      return result is not None
    if isinstance(osw, bool):
      if type(result)!=bool:
        return True
      return bool(result)!=osw
    if hasattr(osw, '__call__'):
      return not osw(result)
    ## This should have been detected since _setup
    raise ValueError('Unknown OSW strategy.') # pragma: no cover

  def _run(self, *args, **kwargs):
    """
    The heart of the execution, wrapping with the caching environment.

    >>> f = getfixture('f_cache_to_file')

    ## Runtime-error on bad flags

    >>> f(force_reload=True, early_giveup=True)
    Traceback (most recent call last):
    ...
    ValueError: Cannot have `force_reload` and `early_giveup` both True.

    ## Putting back kwargs for natively-defined func

    >>> @cache_to_file
    ... def f2(force_reload=None):
    ...   return force_reload
    >>> f2(force_reload=True)
    True

    >>> @cache_to_file
    ... def f3(early_giveup=None):
    ...   return early_giveup
    >>> f3(early_giveup=True) is None
    True

    """

    ## Precheck extra flags first... and remove from kwargs
    force_reload = kwargs.pop('force_reload', False)
    early_giveup = kwargs.pop('early_giveup', False)
    if force_reload and early_giveup:
      raise ValueError('Cannot have `force_reload` and `early_giveup` both True.')

    ## Put extra keyword back if it's native to decorated func
    # http://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-python-function-receives
    native_args = inspect.getargspec(self.func)[0]
    if 'force_reload' in native_args:
      kwargs['force_reload'] = force_reload
    if 'early_giveup' in native_args:
      kwargs['early_giveup'] = early_giveup

    ## Prep the env
    key       = self.makekey(*args, **kwargs)
    shelf     = self.shelf
    result    = None
    time_last = None
    self._logd('args        : %s'%str(args))
    self._logd('kwargs      : %s'%str(kwargs))
    self._logd('force_reload: %r'%force_reload)
    self._logd('early_giveup: %r'%early_giveup)
    self._logd('key in shelf: %r'%(key in shelf))

    ## Load key from shelf first, may/not be used, depends on expire date
    if key in shelf:
      self._logd('Loading key : '+key)
      result, time_last = shelf[key]

    ## Handle giveup scenario
    if early_giveup:
      if (key in shelf) and not self.is_expired(time_last):
        self._count_total += 1
        self._count_hit   += 1
        return result
      else:
        # Abort, also not increment the counter
        self._logd('Early giveup on key: '+key)
        return None

    ## Recalculate if new, forced, or expired
    if (key not in shelf) or force_reload or self.is_expired(time_last):
      self._logd('Calling func: %r, %r'%(args,kwargs))
      result = self.func(*args, **kwargs)
      if self._do_write_isw(*args, **kwargs) and self._do_write_osw(result):
        self._logd('Write new key: '+key)
        shelf[key] = result  # Store back. Timestamp is handled by shelf's interface
      else:
        ## Try to remove such entry from current shelf if existed.
        ## (this usually happens retroactively when function definition changes).
        if key in shelf: # pragma: no cover
          del shelf[key]
    else:
      ## Cache is used. Simply update the entry to trigger new expire date(impl by shelf)
      self._count_hit += 1
      self._logd('Write new key: '+key)
      shelf[key] = result
      ## Log additional info on new expiredate
      if self._timeout:
        newdate = datetime.now()+timedelta(seconds=self._timeout)
        self._logd('New expdate : {}'.format(newdate))
    self._count_total += 1
    return result

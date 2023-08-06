#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from contextlib import contextmanager
from io import StringIO    # for handling unicode strings

#==============================================================================

class MyLogger(logging.getLoggerClass()):

  ## Expose logging level
  DEBUG   = logging.DEBUG
  INFO    = logging.INFO
  WARNING = logging.WARNING
  ERROR   = logging.ERROR

  @staticmethod
  def extra(func):
    """
    Return dict for extra by func, used with `MyLoggingHandler` above
    Use for workaround in case of logger in nested function not delegated...

    USAGE: log.debug('val', extra=log.extra(func))

    """

    ## deco.synchronized compat
    if 'orig_f' in func.__dict__: # pragma: no cover
      func = func.__dict__['orig_f']
    name = func.__name__
    try:
      file = func.func_globals['__file__']
    except AttributeError: # pragma: no cover
      file = func.__globals__['__file__']
    return {'name_override': name, 'file_override': file}

  #---------#
  # CAPTURE #
  #---------#

  def capture_start(self):
    """
    Temporary halt the output to its handler, return instance of stringstream to use.
    """
    if not getattr(self, '_capstream', None):
      capstream = StringIO()
      handler   = logging.StreamHandler(capstream)
      handler.setFormatter(logging.Formatter(u'%(levelname)s: %(funcName)s - %(message)s'))
      self._oldhandlers = self.handlers
      self._capstream   = capstream
      self.handlers = [handler]
      self._lines = []
      return self._lines

  def capture_purge(self):
    if hasattr(self, '_capstream'):
      dat = self._capstream.getvalue()
      self._capstream.truncate(0)
      self._lines[:] = dat.replace('\x00','').strip().split('\n')
    return None

  def capture_stop(self):
    """Undo the effect of capture above to normal behavior."""
    self.handlers = self._oldhandlers
    self._capstream.close()
    del self._capstream

  @contextmanager
  def capture(self):
    """

    Usage:

    >>> logger = getfixture('logger')
    >>> with logger.capture() as lines:
    ...   print('Inside capture')
    ...   logger.info("It should be silent here")
    ...   logger.warning("even if it's very loud.")
    Inside capture

    >>> for line in lines:
    ...   print(line)
    INFO: <module> - It should be silent here
    WARNING: <module> - even if it's very loud.

    """
    stream = self.capture_start()
    yield stream
    self.capture_purge()
    self.capture_stop()

#==============================================================================

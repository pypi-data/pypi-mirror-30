#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging

#==============================================================================

class Whitelist(logging.Filter):
  """
  Filter the log by name.

  >>> filt = Whitelist('muon', 'tau')
  >>> filt.filter(LogRecord('muon'))
  True
  >>> filt.filter(LogRecord('tau.h1'))
  True
  >>> filt.filter(LogRecord('123'))
  False

  """
  def __init__(self, *whitelist):
    self.whitelist = [logging.Filter(name) for name in whitelist]

  def filter(self, record):
    return any(f.filter(record) for f in self.whitelist)


class Blacklist(Whitelist):
  """

  >>> filt = Blacklist('PythonCK')
  >>> filt.filter(LogRecord('muon'))
  True
  >>> filt.filter(LogRecord('PythonCK.logging'))
  False

  """
  def filter(self, record):
    return not Whitelist.filter(self, record)


class FuncFileNameRegexFilter(logging.Filter):
  """
  Valid if re.search returns non-null.

  >>> filt = FuncFileNameRegexFilter(r'tauh[13]')
  >>> print(filt)
  FuncFileNameRegexFilter: tauh[13]

  >>> filt.filter(LogRecord('tauh1'))
  True
  >>> filt.filter(LogRecord('tauh3'))
  True
  >>> filt.filter(LogRecord('taumu', func=func0))
  False

  """

  def __init__(self, pattern):
    self._pattern = pattern

  def __str__(self):
    return 'FuncFileNameRegexFilter: %s'%self._pattern

  def filter(self, record):
    ## At current impl, return True if found in any of these.
    queues = [record.name]
    if record.filename:
      queues.append(str(record.filename))
    if record.funcName:
      queues.append(str(record.funcName))
    return any(bool(re.search(self._pattern, text)) for text in queues if text)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Custom logging handler derived from RainbowLoggingHandler.

"""

import re
import os
import sys
import subprocess
import logging

#===============================================================================

def has_rainbow(): # pragma: no cover
  """
  Return boolean whether the package is installed or not,
  and the enviroment is appropriate for usage or not (i.e., interactive shell).
  """
  ## Disable on ganga-node-cluster
  if re.findall(r'lphe[\d][\d]', os.environ.get('SLURMD_NODENAME', '')):
    return False
  if os.environ.get('SLURM_JOB_NAME','tcsh') != 'tcsh':
    return False
  try:
    import rainbow_logging_handler  # noqa
    return True
  except ImportError:
    logging.getLogger().warning("Warning, cannot import RainbowLoggingHandler.")
  return False

def check_term_width():
  """
  Try do determine current terminal width if possible,
  otherwise default to 120
  """
  try:
    return int(subprocess.check_output(['stty', 'size']).split()[1])
  except subprocess.CalledProcessError:
    pass
  return 120

## Global const
HAS_RAINBOW = has_rainbow()
TERMWIDTH = check_term_width()

## Switch the class
if HAS_RAINBOW: # pragma: no cover
  from rainbow_logging_handler import RainbowLoggingHandler as cls_handler
else: # pragma: no cover
  cls_handler = logging.StreamHandler

#===============================================================================

def splittext(s, width):
  """
  Given a string, split into list of substring of given width.

  >>> for token in splittext('0123456789', 4):
  ...   print(token)
  0123
  4567
  89

  """
  for i in range(int(len(s)/width)+1):
    yield s[i*width:(i+1)*width]

def condense_two_strings(s1, s2, width):
  """
  Given 2 strings (e.g., funcname & filename), return 2 strings pair such that
  the length is does not exceed given width, in order to maximize space in the
  left-column of logging.

  >>> condense_two_strings('aa', 'bb', 8)
  ('aa', 'bb    ')
  >>> condense_two_strings('aaaa', 'bbbb', 8)
  ('aaaa', 'bbbb')
  >>> condense_two_strings('aaaaaaa', 'bbbb', 8)
  ('aa..', 'bbbb')
  >>> condense_two_strings('aaa', 'bbbbbbb', 8)
  ('aaa', 'bbb..')

  """
  l1 = len(s1)
  l2 = len(s2)
  if l1 + l2 > width:
    ## Trim the longer one
    if l1 > l2:
      s1 = s1[:width-2-l2]+'..'
    else:
      s2 = s2[:width-2-l1]+'..'
  else:
    ## inflate s2 to width
    fmt_s2 = '{:<%i}'%(width-l1)
    s2 = fmt_s2.format(s2)
  return s1, s2

def add_indent(lines, width_full, width_column):
  """
  Given a paragraph, add indent on each line except first one.
  """
  sep = ' | '
  acc = []
  for i,line in enumerate(lines.strip('\n').split('\n')):
    for j,block in enumerate(splittext(line, width_full-width_column-len(sep))):
      indent = '' if (i==0 and j==0) else (' '*width_column+sep)
      acc.append(indent+block)
  return '\n'.join(acc)

#===============================================================================

class MyLoggingHandler(cls_handler):
  """
  My custom log handler, with following touches
  - support extra field `name_override`, `file_override`
  - changeable column width

  """

  def __init__(self, width=34): # pragma: no cover
    ## Configuration if rainbow is available.
    if HAS_RAINBOW:
      super(MyLoggingHandler, self).__init__(
        sys.stderr,
        color_message_debug    = ('black', None, True),
        color_message_warning  = ('red'  , None, False),
        color_funcName         = ('blue' , None, False),
        color_filename         = ('cyan' , None, False),
        # datefmt                = "%H%M%S %f %w %d %Y",  # This is behavior of Rainbow. It ignore the datefmt in formetter
        # color_message_info     = ('green', None, True),
        # color_msecs = ('black',None,True),
        # color_message_critical = ('green', None, True), # alias ~ success!
      )
      self._column_color['%(message)s'][1] = ('black', None, False)  # Custom verbose level
    else:
      super(MyLoggingHandler, self).__init__()
    ## Other params
    self.width = width

  def format(self, rec):
    ## Overridden attribute
    if hasattr(rec, 'name_override'):
      rec.funcName = rec.name_override
    if hasattr(rec, 'file_override'):
      rec.filename = os.path.split(rec.file_override)[-1]

    ## clean .py(c) suffix
    rec.filename = rec.filename.replace('.pyc', '').replace('.py', '')

    ## adjust 2 strings to given width
    rec.funcName, rec.filename = condense_two_strings(rec.funcName, rec.filename, self.width)

    ## split the linebreak
    rec.msg = add_indent(rec.msg, TERMWIDTH, self.width)

    ## Finally
    return super(MyLoggingHandler, self).format(rec)

#===============================================================================

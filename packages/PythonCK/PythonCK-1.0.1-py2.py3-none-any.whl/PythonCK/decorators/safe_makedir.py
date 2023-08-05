#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import errno

def safe_makedir(target):
  """
  Workaround the race condition when multiple instances run on same node.
  https://stackoverflow.com/questions/1586648/race-condition-creating-folder-in-python

  Also:
  
  - make sure it's string (or convert to string from py.local)
  - expand var to abs path
  - return the string path.

  >>> import os
  >>> _ = getfixture('chtmpdir')
  >>> safe_makedir('subdir')
  'subdir'
  >>> os.path.exists('./subdir')
  True

  """

  # dirname = os.path.dirname(target)
  # ## Remove the file (probably unsharded) is exists
  # if os.path.exists(dirname) and os.path.isfile(dirname):
  #   os.remove(dirname)

  target = os.path.expandvars(str(target)) # basedir may be py.local
  try:
    os.makedirs(target)
  except OSError as e: # pragma: no cover
    if e.errno == errno.EEXIST and os.path.isdir(target):
      # File exists, and it's a directory,
      # another process beat us to creating this dir, that's OK.
      pass
    else:
      # Our target dir exists as a file, or different error,
      # reraise the error!
      raise e
  finally:
    return target

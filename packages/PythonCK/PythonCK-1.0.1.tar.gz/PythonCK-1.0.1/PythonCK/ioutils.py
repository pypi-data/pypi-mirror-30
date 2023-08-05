#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Collections of tools related to I/O.

"""

import sys
import os
import hashlib
import tempfile
import contextlib
import subprocess

## Python2/3 compat
from six import StringIO

## Local
from . import logger
from .decorators import cache_to_file

#===============================================================================

def dump_to_file(obj, destination=None, suffix=''):
  """
  Quickly dump file, creating folder/file along the way.
  For instance, where python/xml option file is needed to be created on-the-fly,
  in order to supply the path to that file for another process.

  Args:
    obj (object): Arbitary object to write. The str(obj) will be called.
                  If it's string and looks like URL, it'll download instead.

    destination (str): String for the destination location.
                       If None, create temp file at system's temp dir.
                       File name will be made from SHA-1 of given object,
                       this is useful for caching to reused dumped object.

    suffix (str): Suffix (extension) to append to outputfile.
                  Needed in some case where suffix will be looked ahead.

  Returns:
    String of path to dumped file.

  >>> tmpdir = getfixture('tmpdir')
  >>> oldcwd = tmpdir.chdir()

  >>> dump_to_file('some_data').split('/')[-1]
  '256be736caed19be589e439b0d5b8392340d82bc'

  >>> dump_to_file('some_data', suffix='.py').split('/')[-1]
  '256be736caed19be589e439b0d5b8392340d82bc.py'

  >>> dump_to_file('some_data', 'target').replace(str(tmpdir), '...')
  '.../target'

  >>> dump_to_file('some_data', 'target', suffix='.py').replace(str(tmpdir), '...')
  '.../target.py'

  >>> dump_to_file('some_data', 'target.py', suffix='.py').replace(str(tmpdir), '...')
  '.../target.py'

  >>> dump_to_file('some_data', 'dname/target.py').replace(str(tmpdir), '...')
  '.../dname/target.py'

  >>> _ = oldcwd.chdir()

  """
  ## Prepare the destination.
  if not destination:
    fname = hashlib.sha1(repr(obj).encode('utf-8')).hexdigest()
    destination = os.path.join(tempfile.gettempdir(), fname)
  ## Add request suffix
  if suffix and not destination.endswith(suffix):
    destination += suffix
  ## Make sure the destination dir exists
  destination = os.path.abspath(destination)
  dname = os.path.split(destination)[0]
  if not os.path.exists(dname):
    os.makedirs(dname)
  ## Finally, write out the output
  with open(destination, 'w') as fout:
    fout.write(str(obj))
  return destination

#===============================================================================

def checksum(filepath):
  """
  Given filepath to specific file, return its checksum (unique identifier).
  Optimized for large file, buffered reading.

  Args:
      filepath (str): String to filepath

  Return:
      hex string checksum

  >>> checksum('tests/res/ioutils/checksum.txt')
  '220e9a9970406e4c688e2c27b8858073f6e2bd33'

  """
  BLOCKSIZE = 65536
  hasher = hashlib.sha1()
  with open(filepath, 'rb') as afile:
    buf = afile.read(BLOCKSIZE)
    while len(buf) > 0:
      hasher.update(buf)
      buf = afile.read(BLOCKSIZE)
  return hasher.hexdigest()

#===============================================================================

@cache_to_file
def _get_size_and_date(path):
  """
  Helper method to retrieve both dirsize and its modified date,
  result is cached.

  Used internally by other function.

  """
  ## Sum the content size in dir
  arg    = "find %s -type f -exec ls -l {} \\; | awk '{sum += $5} END {print sum}'"
  stdout = subprocess.check_output(arg%path, shell=True)
  ## Can be null string for completely empty dir
  size  = int(stdout.split()[0]) if stdout.strip() else 0
  mtime = os.stat(path).st_mtime
  return size, mtime


def size(path, force_reload=False, early_giveup=False):
  """
  Retrive the total size of given path to directory.
  Try to be smart by caching the directory size, and invalidate result by
  checking the st_mtime of that path.

  Args:
    path (str): Path to directory to check

    force_reload (bool): If True, the new result will be calculated regardless
                         the cache.

    early_giveup (bool): If True, will return 0 immediately is this request has
                         no previous result cached.

  Return:
    int representing size in BYTES

  Caveats:

  - Because disc usage != file size, use `ls` instead of `du` (compatibility)
    with OSX's BSD's `du`

  Usage::
    
    >>> import time
    >>> tmpdir = getfixture('chtmpdir')

    ## In case of non-existent path, return zero.
    >>> size('non/existent/path')
    0

    ## New content
    >>> tmpdir.join("hello.txt").write("content")
    >>> size(tmpdir)
    7

    ## Second file in the same directory, invalidate the cache.
    >>> time.sleep(1)  # Need at least 1 second for st_mtime to propagate
    >>> tmpdir.join("hello2.txt").write("contents".encode('utf-8'))
    >>> size(tmpdir)
    15

    ## Make sure that if directory disappear, the cache will be deleted.
    >>> tmpdir.mkdir('sub').join('hello3.txt').write('content')
    >>> size(tmpdir.join('sub'))
    7
    >>> tmpdir.join('sub').remove()
    >>> size(tmpdir.join('sub'))
    0

    ## DEV: early_giveup, force_reload
    >>> tmpdir.mkdir('sub2').join('test.txt').write('foobar')
    >>> size(tmpdir.join('sub2'), early_giveup=True)
    0
    >>> size(tmpdir.join('sub2'), force_reload=True)
    6


  REF:
  http://superuser.com/questions/22460/how-do-i-get-the-size-of-a-linux-or-mac-os-x-directory-from-the-command-line
  """
  path = str(path)  # Pytest compat
  logger.debug('Sizing: %r'%path)
  ## Early abort if not exists
  if not os.path.exists(path):
    logger.debug('Path not existed: '+path)
    return 0
  ## Make a call, potentially from cache.
  val = _get_size_and_date(path, force_reload=force_reload, early_giveup=early_giveup)
  if val is None:  # early gaveup
    return 0
  size,mtime0 = val  # unpack
  ## Guarantee to have the newest result already
  if force_reload:
    logger.debug('Sizing: return with force_reload=True')
    return size
  ## Deal with the expiration
  mtime = os.stat(path).st_mtime
  if mtime == mtime0:  # Cache result is usable because folder hasn't changed.
    logger.debug('Sizing: return with good cache: %r' % mtime)
    return size
  ## Outdated, do force reload.
  logger.debug('outdated: %r != %r'%(mtime, mtime0))
  return _get_size_and_date(path, force_reload=True)[0]

#===============================================================================


_suffixes = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')


def humansize(nbytes):
  """
  Given the value in bytes, return the human-readible string.

  Args:
    nbytes (int): Size in BYTES

  Return:
    str: Human-readible size in string.

  Usage:

  >>> humansize(None) is None
  True
  >>> humansize(0)
  '0 B'
  >>> humansize(12)
  '12.00 B'
  >>> humansize(12000)
  '11.72 KB'
  >>> humansize(1E10)
  '9.31 GB'

  """
  if nbytes is None:
    return None
  if nbytes == 0:
    return '0 B'
  i = 0
  while nbytes >= 1024 and i < len(_suffixes)-1:
    nbytes /= 1024.
    i += 1
  return '%.2f %s' % (nbytes, _suffixes[i])

#===============================================================================

@contextlib.contextmanager
def capture():
  r"""
  REF: http://stackoverflow.com/questions/5136611/capture-stdout-from-a-script-in-python

  Usage:
    >>> with capture() as std_out_err:
    ...   print('hi')
    >>> out,err = std_out_err
    >>> out
    'hi\n'
    >>> err
    ''

  """
  oldout,olderr = sys.stdout,sys.stderr
  try:
    out = [StringIO(), StringIO()]
    sys.stdout,sys.stderr = out
    yield out
  finally:
    sys.stdout,sys.stderr = oldout, olderr
    out[0] = out[0].getvalue()
    out[1] = out[1].getvalue()

#===============================================================================

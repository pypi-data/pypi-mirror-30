# content of conftest.py

import os
import pytest
import shutil
import logging


# @pytest.fixture
# def chdirtest(monkeypatch):
#   monkeypatch.chdir(os.path.join(os.path.split(__file__)[0], 'tests'))

@pytest.fixture(autouse=True, scope="session")
def setup_clean():
  """
  Make sure there's no cache particular to this package.
  """
  import tempfile
  import subprocess
  subprocess.call('rm -rf %s/PythonCK*' % tempfile.gettempdir(), shell=True)

#===============================================================================

@pytest.fixture
def caplog2(caplog):
  """
  Temporary enable logger propagation to root logger in order to allow
  pytest.caplog test.
  """
  ## Setup
  import logging
  caplog.set_level(logging.DEBUG)
  from PythonCK import logger
  oldlv = logger.getEffectiveLevel()
  logger.setLevel(logger.DEBUG)
  logger.propagate = True  # to make this visible from caplog.text

  # ## Assimilate my formatter into pytest.LogCaptureHandler
  # old_formatter = {}
  # for i,handler in enumerate(logging.Logger.root.handlers):
  #   if handler.__class__.__name__ == 'LogCaptureHandler':
  #     old_formatter[i] = handler.formatter
  #     handler.setFormatter(logger.handlers[0].formatter)

  ## Ready
  yield caplog

  # ## Teardown
  logger.propagate = False
  logger.setLevel(oldlv)
  # for i,fmt in old_formatter.iteritems():
  #   logging.Logger.root.handlers[i] = fmt

@pytest.fixture
def chtmpdir(tmpdir):
  """
  Temporary chdir to temp dir.
  """
  olddir = tmpdir.chdir()
  yield tmpdir
  olddir.chdir()

def func0(*args, **kwargs):
  """Dummy function."""
  return args, kwargs

@pytest.fixture(autouse=True)  # , scope='session'
def add_func0(doctest_namespace):
  doctest_namespace['func0'] = func0

@pytest.fixture
def f_cache_to_file(chtmpdir):
  """
  For testing cache_to_file, make sure to clean up afterward.
  """
  from PythonCK.decorators import cache_to_file
  func = cache_to_file(func0, basedir='conftest')
  yield func
  ## remove cache shelf
  target = func.shelfid
  if os.path.exists(target):
    shutil.rmtree(target)

#------------------

def LogRecord(name, level=logging.INFO, pathname='.', lineno=0, msg='msg', args=None, exc_info=None, func=None):
  """
  Simplified constructor.
  """
  return logging.LogRecord(**locals())

@pytest.fixture(autouse=True, scope='session')
def add_log_record(doctest_namespace):
  doctest_namespace['LogRecord'] = LogRecord

@pytest.fixture
def logger():
  from PythonCK import logger
  return logger

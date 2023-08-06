#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Collection of several useful decorators.

"""

import functools

## Python2/3 compat
from six.moves import builtins

## Local
from .. import logger
from .meta import optional_arg_decorator

#===============================================================================
# PROFILE
# Provide dummy pass-through in-lieu of the line_profiler's profile decorator.
#===============================================================================

try:
  builtins.profile
except AttributeError:
  # No line profiler, provide a pass-through version
  builtins.profile = lambda func: func

#===============================================================================
# DEPRECIATED
#===============================================================================

def deprecated(func):
  """
  This will print warning whenever this decorated function is called.

  >>> caplog = getfixture('caplog2')
  >>> @deprecated
  ... def f_deprecated():
  ...   pass
  >>> f_deprecated()

  >>> 'WARNING' in caplog.text and 'deprecated' in caplog.text
  True

  """
  def wrap(*args, **kwargs):
    """
    Just show the warning
    """
    logger.warning('This function is deprecated.', extra=logger.extra(func))
    return func(*args, **kwargs)
  return wrap

# #===============================================================================
# # PRINT-TO-RETURN
# #===============================================================================

# def print_to_return(func):
#   """
#   Decorator func to wrap printing-to-stdout to return string instead.
#   The original return of that function will be discarded.
#   """
#   from IPython.utils.capture import capture_output
#   @functools.wraps(func)
#   def wraps(*args, **kwargs):
#     """
#     Borrow the functionality from IPython
#     """
#     with capture_output() as captured:
#       func(*args, **kwargs)
#     captured() # restore printing to stdout, original behavior
#     return captured.stdout
#   return wraps

#===============================================================================
# REPORT
#===============================================================================

__REPORT_INDENT = [0]

@optional_arg_decorator
def report(func, level=10, hide_input=False, hide_output=False):
  r"""
  Decorator to print information about a function call for use while debugging.
  Prints function name, arguments, and call number when the function is called.
  Prints this information again along with the return value when the function
  returns.

  It it's used inside Gaudi, the debug level is too polluted.
  Hence additional flag if given

  If `hide_output`, will show only the call, but not output result

  >>> caplog = getfixture('caplog2')

  >>> @report
  ... def foo():
  ...   return 'line1\nline2'

  >>> _ = foo()

  """

  # Note, I control the source level, not the display level
  extra = logger.extra(func)

  def flog(msg):
    logger.log(level, msg, extra=extra)

  @functools.wraps(func)
  def report_wrap(*params, **kwargs):
    call    = report_wrap.callcount = report_wrap.callcount + 1
    indent  = ' ' * __REPORT_INDENT[0]
    fcall   = ', '.join(
      [repr(a) for a in params] +
      ["%s = %s" % (a, repr(b)) for a,b in kwargs.items()]
    )

    if not hide_input:
      flog("[#%s]%s>> %s" % (call, indent, fcall))
    # flog("[#%s]%s>> %s" % (call, indent, '' if hide_input else fcall), extra=extra)
    __REPORT_INDENT[0] += 3
    result = func(*params, **kwargs)
    __REPORT_INDENT[0] -= 3
    if not hide_output:
      repr_result = repr(result)
      if '\\n' in repr_result: # large object, insert new line
        repr_result = '\n'+repr_result
      flog("[#%s]%s<< %s" % (call, indent, repr_result))
    return result
  report_wrap.callcount = 0
  return report_wrap

## Shortcuts
report_debug = report(level=logger.DEBUG)
report_info  = report(level=logger.INFO)

#===============================================================================
# SINGLETON
#===============================================================================

def singleton(cls):
  """
  Use this on a class to quickly make it becomes singleton.

  Usage:

  >>> @singleton
  ... class Foo(object):
  ...   pass
  
  >>> x1 = Foo()
  >>> x1.val = 555
  >>> x2 = Foo()
  >>> x1 == x2
  True
  >>> x2.val
  555

  """
  instances = {}

  def getinstance():
    if cls not in instances:
      instances[cls] = cls()
    return instances[cls]
  return getinstance

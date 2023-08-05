#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import six
from abc import ABCMeta, abstractmethod
from .. import logger

#===============================================================================

def optional_arg_decorator(decorator):
  """
  Meta-decorator to let the function-based decorator takes both
  argfull and argless constructor signature.

  Usage::

    ## Define decorator
    >>> @optional_arg_decorator
    ... def foo(func, arg=None):
    ...   def wrap(*args, **kwargs):
    ...     return func(*args, **kwargs), arg
    ...   return wrap

    ## Without arg
    >>> @foo
    ... def bar():
    ...   return 'bar'
    >>> bar()
    ('bar', None)

    ## With arg
    >>> @foo('more')
    ... def baz():
    ...   return 'baz'
    >>> baz()
    ('baz', 'more')

  REF:
  
  - http://stackoverflow.com/questions/3888158

  """
  @functools.wraps(decorator)
  def wrapped_decorator(*args, **kwargs):
    """
    # In case where first item is a func
    # CASE1: Stand-alone: f = deco(f)
    # CASE2: Non-arg deco:  @deco;def f():
    """
    if len(args) >= 1 and callable(args[0]):
      func = args[0]
      return decorator(func, *args[1:], **kwargs)
    else:
      def real_decorator(decoratee):
        """
        In case of decorator with optional args
        """
        return decorator(decoratee, *args, **kwargs)
      return real_decorator
  return wrapped_decorator


#============================#
# Base Class-based Decorator #
#============================#

@six.add_metaclass(ABCMeta)
class AbstractClassbasedDecorator(object):
  """
  Baseclass to be used for all class-based decorator involving optional init arg.

  The difficulty lies in the fact that there're 2 ways to init a decorator instance.

  Without kwargs:

  - ``__init__`` will have ``func`` equal to the decorated function.
  - ``__call__`` will have all (args,kwargs) input for func

  With kwargs:

  - ``__init__`` will have all args to init decorator, but no func available yet
  - ``__call__`` will be invoked 2 times:

    * 1st-time: func will be passed as first arg, save it, then return self to invoke 2nd
    * 2nd-time: The (args,kwargs) for decorated function will be received here.

  Note:
  - Not possible to use simple args for init, too ambiguous.
  - The decorated function is accessible through property ``self.func``
    Its setter ``self.func = xxx`` will be handled implicitly under the hood,
    so there should be no need to call this manually.

  Test cases::

    ## Abstract, need implementation
    
    >>> class Foo(AbstractClassbasedDecorator):
    ...   pass
    >>> Foo()
    Traceback (most recent call last):
    ...
    TypeError: Can't instantiate abstract class Foo with abstract methods _run, _setup

    >>> class foo(AbstractClassbasedDecorator):
    ...   def _setup(self, *args, **kwargs):
    ...     pass
    ...   def _run(self, *args, **kwargs):
    ...     return self.func(*args, **kwargs)

    ## Decorating function, with/without decorator kwarg.

    >>> @foo
    ... def func_without_kwargs():
    ...   return 'without'
    >>> func_without_kwargs()
    'without'

    >>> @foo(kw='kwarg')
    ... def func_with_kwargs():
    ...   return 'with'
    >>> func_with_kwargs()
    'with'

    ## Decorating instance method

    >>> class Aileus:
    ...   @foo
    ...   def bondus(self):
    ...     return 'bondus'
    ...   @foo(kw='kwargs')
    ...   def callus(self):
    ...     return 'callus'
    >>> a = Aileus()
    >>> a.bondus()
    'bondus'
    >>> a.callus()
    'callus'

  REF:

  - http://tech.novapost.fr/python-class-based-decorators-en.html
  - http://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods/

  """

  @abstractmethod
  def _setup(self, *args, **kwargs): # pragma: no cover
    """
    Define the signature for decorator's init arguments here.

    Example:
      def _setup(self, basedir=None, timeout=None)
        ...
    """
    pass

  @abstractmethod
  def _run(self, *args, **kwargs): # pragma: no cover
    """
    Define the core logic of the decorator here
    """
    pass

  @property
  def func(self):
    """
    Return the instance of decorated function
    """
    return self._func

  @func.setter
  def func(self, val):
    """
    Upon setting the valid function, the _setup will be called
    """
    self._func = val
    if val is not None:  # Ready, ignite!
      assert callable(val), 'Cannot decorate non callable object "{}"'.format(val)
      args,kwargs = self._init_args_kwargs
      self._extra = logger.extra(self.func)
      self._setup(*args, **kwargs)
      functools.update_wrapper(self, self._func)

  def _logd(self, message):
    """
    Helper logging function that handles wrapped info.
    """
    logger.debug(self.__class__.__name__+': '+message, extra=self._extra)

  def __init__(self, func=None, *args, **kwargs):
    # print '__init__', locals()
    self._instance = None  # For instance-method decoration
    self._init_args_kwargs = (args,kwargs)  # Keep for late-init
    self.func = func

  ## Support for instance-method decoration...
  def __get__(self, instance, owner):
    # print '__get__', locals()
    self._instance = instance
    if instance is None:
      raise NotImplementedError('Need test case here') # pragma: no cover
      # return self.func
    return self

  def __call__(self, *args, **kwargs):
    # print '__call__', locals()

    ## If it's the late-init
    if not self.func:
      if args[1:] or kwargs:
        raise NotImplementedError('Need test case here') # pragma: no cover
        # raise ValueError('Cannot decorate and setup simultaneously '
        #                  'with __call__(). Use __init__() or '
        #                  'setup() for setup. Use __call__() or '
        #                  'decorate() to decorate.')
      self.func = args[0]
      return self  # To have recursive __call__
    ## For instance-method decoration
    if self._instance:
      return self._run(self._instance, *args, **kwargs)
    ## For standalone-function decoration
    return self._run(*args, **kwargs)

#===============================================================================

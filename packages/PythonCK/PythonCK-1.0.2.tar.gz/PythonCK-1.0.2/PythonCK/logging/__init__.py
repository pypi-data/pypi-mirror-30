#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Entry point to using my custom logging facility.

- Colored log (via RainbowLoggingHandler).
- Log capture contextmanager.
- Flexible 2-columns width.
- Regex filter.

REF:

- https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
- https://docs.python.org/2/library/logging.config.html
- https://logmatic.io/blog/python-logging-with-json-steroids/
- https://stackoverflow.com/questions/21127360
- https://stackoverflow.com/questions/14097061

"""

import os
import logging
import logging.config
# import yaml

def init(path=os.path.join(os.path.split(__file__)[0], 'conf.ini')): # pragma: no cover
  """
  Load & apply my custom configuration to logging system.

  TODO: Accept '-v' flag from argparse at runtime to change LEVEL

  """

  ## Override the default class first, before loading config.
  from .logger import MyLogger
  logging.setLoggerClass(MyLogger)

  ## Load the config file
  if os.path.exists(path):
    # ## YAML
    # with open(path, 'rt') as f:
    #   conf = yaml.safe_load(f.read())
    # logging.config.dictConfig(conf)
    ## INI
    logging.config.fileConfig(path)
  else:
    logging.basicConfig(level=logging.INFO)

  # ## Hack to look for sys.argv flag. Don't consume as some other lib will use the same flag.
  # import sys
  # if '-v' in sys.argv:
  #   logger.setLevel(logging.DEBUG)
  #   # sys.argv.remove('-v')
  # # elif '-vv' in sys.argv:
  # #   logger.setLevel(logging.VERBOSE)
  #   # sys.argv.remove('-vv')
  # elif '--log-level=30' in sys.argv:  # TODO: Use argparse
  #   logger.setLevel(logging.WARNING)
  #   # sys.argv.remove('--log-level=30')

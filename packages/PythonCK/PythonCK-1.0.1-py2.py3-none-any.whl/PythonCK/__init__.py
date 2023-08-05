#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Prevent compatibility regressions
from __future__ import absolute_import

## Metadata
__author__  = 'Chitsanu Khurewathanakul'
__email__   = 'chitsanu.khurewathanakul@gmail.com'
__license__ = 'GNU GPLv3'

## Trigger this at runtime, then make this logger avilable.
from .logging import init
init()
del init
import logging
logger = logging.getLogger(__name__)

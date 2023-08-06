#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Utilities related to string

"""

from six.moves import zip_longest  # itertools
import re

#===============================================================================

def concat_multilines(*msgs):
  r"""
  Concat horizontally list of multi-line strings.

  Useful for printing long-thin paragraph together.

  Args:
    msgs (list of str): list of paragraphs.

  Usage::

    >>> print(concat_multilines('line11\nline12', 'line21\nline22'))
    line11 line21
    line12 line22

  """
  widths = [max(len(line) for line in msg.split('\n')) for msg in msgs]
  tmp    = (('{:%i} '*len(widths))%tuple(widths)).strip()
  gen    = zip_longest(*[msg.split('\n') for msg in msgs], fillvalue='')
  return '\n'.join([tmp.format(*words) for words in gen]).strip()

#===============================================================================

def insert_line(msg, index, line):
  r"""
  Similar to list.insert, for inserting line into a paragraph.

  >>> print(insert_line('line1\nline2\nline3', 1, 'xxx'))
  line1
  xxx
  line2
  line3

  """
  l = msg.split('\n')
  l.insert(index, line)
  return '\n'.join(l)

#===============================================================================

def lreplace(string, pattern, sub):
  """
  Replaces 'pattern' in 'string' with 'sub' if 'pattern' STARTS WITH 'string'.
  It's actually better if I remember this regex by heart.

  >>> lreplace('prefix_word', 'prefix_', 'new_')
  'new_word'

  """
  return re.sub('^%s' % pattern, sub, string)

#===============================================================================

def _remove_vertical_duplicate(paragraph, tag):
  """
  Given a paragraph, remove the duplicate substring if it's directly below
  the first occurence. Useful for showing the multiindex in markdown.
  """
  n       = len(tag)
  newtag  = [' ']*n
  lines   = paragraph.split('\n')
  for i, line in enumerate(lines):
    if tag in line:
      idx = line.index(tag)
      ## seek the next lines for replacement, only for consecutive lines
      for j, line2 in enumerate(lines[i+1:]):
        if line2[idx:idx+n] == tag:
          # replace
          l = list(line2)
          l[idx:idx+n] = newtag
          lines[i+1+j] = ''.join(l)
        else:
          break
  return '\n'.join(lines)

def remove_vertical_duplicate(paragraph, *tags):
  r"""
  Generic extension where arbitary amount of tags can be used to remove.

  >>> print(remove_vertical_duplicate(
  ...   "muon PT\n"
  ...   "muon Eta\n"
  ...   "muon Phi\n"
  ...   "tau  PT\n"
  ...   "tau  Eta\n"
  ...   "tau  Phi"
  ... , 'muon ', 'tau '))
  muon PT
       Eta
       Phi
  tau  PT
       Eta
       Phi

  """
  for tag in tags:
    paragraph = _remove_vertical_duplicate(paragraph, tag)
  return paragraph

#===============================================================================

def try_int_else_float(s):
  """
  Given the string of number, return the float of that number, and cast to int
  if possible. Raise exception otherwise

  >>> try_int_else_float('2.00')
  2
  >>> try_int_else_float('2.50')
  2.5

  Note: python2,3 has slightly different error msg for below.::

    >>> try_int_else_float('not_a_number')
    Traceback (most recent call last):
    ...
    ValueError: could not convert string to float: ...

  """
  x = float(s)
  return int(x) if x.is_integer() else x

#===============================================================================

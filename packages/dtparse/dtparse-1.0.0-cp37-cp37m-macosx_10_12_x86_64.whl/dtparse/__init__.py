from __future__ import absolute_import

from datetime import datetime
from ._dtparse import Parser

__all__ = ['parse']


parse = Parser(datetime).parse

"""
FrankerFaceZ Api Wrapper
~~~~~~~~~~~~~~~~~~~~~~~~
An unofficial wrapper for FrankerFaceZ.

:copyright: (c) 2020-2020 uKaigo
:license: MIT, see LICENSE for more details.
"""
__title__ = 'ffz'
__version__ = '0.1.4a'  # There was a problem with the versioning system. =(
__author__ = 'uKaigo'
__copyright__ = 'Copyright 2020-2020 uKaigo'
__license__ = 'MIT'

from collections import namedtuple

from .client import Client
from .models import *
from .errors import *

ver_tuple = namedtuple('version_info', 'major minor micro releaselevel serial')
version_info = ver_tuple(0, 1, 3, 'alpha', 0)

del(namedtuple)
del(ver_tuple)

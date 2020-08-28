"""
FrankerFaceZ API Wrapper
========================

A basic wrapper for the FrankerFaceZ Api.


© 2020 uKaigo

License: MIT, see LICENSE.

"""

__title__ = 'ffz'
__version__ = '1.4.0a1' # Seriously, idk what to do with name changes.
__license__ = 'MIT'
__author__ = 'uKaigo'
__copyright__ = 'Copyright 2020-2020 uKaigo'

import logging
from collections import namedtuple

from .client import Client
from .models import *
from .exceptions import *
from .abc import *

VersionInfo = namedtuple(
    'VersionInfo', 
    'major minor micro releaselevel serial')
version_info = VersionInfo(1, 4, 0, 'alpha', 1)

logging.getLogger(__name__).addHandler(logging.NullHandler())
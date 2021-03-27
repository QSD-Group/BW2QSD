#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License. Please refer to
https://github.com/QSD-Group/BW2QSD/blob/master/LICENSE.txt
for license details.
'''

import pkg_resources
try:
    __version__ = pkg_resources.get_distribution('bw2qsd').version
except pkg_resources.DistributionNotFound:
    __version__ = None
    
    
# import brightway2 as bw2
# from bw2 import Database, methods, get_activity, LCA
# del bw2

from ._exceptions import *
from ._db_importer import *



from . import (
    _exceptions,
    _db_importer,    
    )

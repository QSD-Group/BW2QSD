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

import pkg_resources, sys
try:
    __version__ = pkg_resources.get_distribution('bw2qsd').version
except pkg_resources.DistributionNotFound:
    __version__ = None

from ._exceptions import *

try:
    import brightway2 as bw2
except Exception as e:
    name, msg = str(sys.exc_info()[0]), str(sys.exc_info()[1])
    # breakpoint()
    if 'ImportError' in name and "cannot import name 'databases'" in msg:
            raise BW2Error('This error is due to an outdated pickle file, ' \
                            'to get more instructions, update your ``bw2data`` package ' \
                            'according to https://github.com/brightway-lca/brightway2-data/commit/9c52e76c84bfa7d3d9719da152c0616d4039a3c3.')
    elif 'PickleError' in name and 'setups.pickle' in msg:
        print('\n')
        print('===================================================================')
        print('You can fix the following error by removing the setups.pickle file.')
        print('===================================================================')
        print('\n')
        # pass
        print(e, '\n')
    
        print('Would you like to remove the file?')
    
        raise e
    else:
        raise e

if 'biosphere3' not in bw2.databases:
    bw2.bw2setup()


from ._db_downloader import *
from ._db_importer import *

from . import (
    _exceptions,
    _db_downloader,
    _db_importer,    
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
for license details.
'''

import pkg_resources, sys, os
try:
    __version__ = pkg_resources.get_distribution('bw2qsd').version
except pkg_resources.DistributionNotFound:
    __version__ = None

from ._exceptions import *

try:
    import brightway2 as bw2
except Exception as e:
    name, msg = str(sys.exc_info()[0]), str(sys.exc_info()[1])
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
        print(e, '\n')
    
        print('Would you like to automatically remove the file? ' \
              'If yes, the file will be permanently removed ' \
              '(i.e., cannot be recovered from Trash or Recycle Bin).')
        if input('[y]/[n]: ') in ('y', 'Y', 'yes', 'Yes', 'YES'):
             path = msg.split("'")[-2]
             if not 'setups.pickle' in path:
                 print('\nError in parsing directory, for cautious purpose, ' \
                       f'please mannual remove the file in {msg} (always backup).\n')
                 raise e
             else:
                 os.remove(path)
                 print('\nFile successfully removed. Please rerun the code.\n')
                 sys.exit()
    
        else:
            raise e
    else:
        raise e

if 'biosphere3' not in bw2.databases:
    bw2.bw2setup()


from .utils import *
from ._db_downloader import *
from ._cf_getter import *

from . import (
    _exceptions,
    utils,
    _db_downloader,
    _cf_getter,    
    )

__all__ = (
    'remove_setup_pickle',
    *_db_downloader.__all__,
    *_cf_getter.__all__,
    )






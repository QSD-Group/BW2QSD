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

from warnings import warn
from ._exceptions import *

try:
    import brightway2 as bw2
except Exception as e:
    name, msg = str(sys.exc_info()[0]), str(sys.exc_info()[1])
    if 'ImportError' in name and "cannot import name 'databases'" in msg:
        raise BW2Error('This error is due to an outdated pickle file, ' \
                        'to get more instructions, update your ``bw2data`` package ' \
                        'according to https://github.com/brightway-lca/brightway2-data/commit/9c52e76c84bfa7d3d9719da152c0616d4039a3c3')
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
        if input('[y]/[n]: ') in ('y', 'yes', 'Y', 'Yes', 'YES'):
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


def remove_setups_pickle():
    '''
    Remove the "setups.pickle" file in the project directory,
    outdated file will cause an error the next time ``BW2QSD`` is loaded.
    
    .. note::
        
        Only run this function before you quitting the program.
    
    '''
    
    from bw2data import projects
    setup_path = os.path.join(projects.dir, 'setups.pickle')
    try:
        os.remove(setup_path)
        print('File "setups.pickle" successfully removed from directory "{projects.dir}".')
    except FileNotFoundError:
        warn(f'"setups.pickle" not found in directory "{projects.dir}", no file removed.',
             stacklevel=2)

from ._db_downloader import *
from ._db_importer import *

from . import (
    _exceptions,
    _db_downloader,
    _db_importer,    
    )

__all__ = (
    *_db_downloader.__all__,
    *_db_importer.__all__,
    'remove_setup_pickle',
    )






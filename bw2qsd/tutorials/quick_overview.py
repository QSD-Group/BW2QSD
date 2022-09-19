#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
BW2QSD: Bridging Brightway2 and QSD packages for LCA

This module is developed by:

    Yalin Li <mailto.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/BW2QSD/blob/main/LICENSE.txt
for license details.

This module contains the same script as in the Jupyter Notebook,
and is included here for convenience.
'''

# %%

import bw2qsd as bq
print(f'This tutorial was made with bw2qsd v{bq.__version__} '
      f'and brightway2 v{bq.bw2_version}.')


# %%

from bw2qsd import DataDownloader
downloader = DataDownloader()
downloader.download_ecoinvent()

downloader.available_databases

# %%

from bw2qsd import CFgetter

ei = CFgetter('ei')
ei.load_database('ecoinvent_apos371')

ei.load_indicators(add=False)
ei.load_indicators(add=True, method='TRACI', category='', indicator='')
ei.remove('indicators', (('TRACI (obsolete)', 'human health', 'non-carcinogenics'),))

act_dct = ei.load_activities(string='building', add=False, limit=10)
act_dct

ei.show_activity(act_dct['building construction, hostel'])

ei.load_activities('building', True)

info = ei.show_activity('building construction, hostel')
info

info['building construction, hostel']['comment']

df = ei.get_CFs(show=False, path='')
df

# %%

from bw2qsd import remove_setups_pickle
remove_setups_pickle()
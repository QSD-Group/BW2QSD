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

__all__ = ('remove_setups_pickle', 'export_df','format_name',)

import os
from warnings import warn

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
        print(f'File "setups.pickle" successfully removed from directory "{projects.dir}".')
    except FileNotFoundError:
        warn(f'"setups.pickle" not found in directory "{projects.dir}", no file removed.',
             stacklevel=2)


def export_df(df, path, show=False):
    if show:
        print(df)

    if path:
        if path.endswith('.tsv'):
            df.to_csv(path, sep='\t')
        elif path.endswith('.csv'):
            df.to_csv(path)
        elif (path.endswith('.xlsx') or path.endswith('.xls')):
            df.to_excel(path)
        else:
            extension = path.split('.')[-1]
            raise ValueError('Only "tsv", "csv", "xlsx", or "xls" files are supported, ' \
                             f'not {extension}.')

        file_path, file_name = os.path.split(path)
        print(f'File "{file_name}" has been exported to "{file_path}".')
    

def format_name(name):
    name = name.replace(', ', ' ')
    name = name.replace('-', ' ')
    return ''.join([i[0].capitalize() + i[1:] for i in name.split(' ')])
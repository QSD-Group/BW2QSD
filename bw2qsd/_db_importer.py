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

import sys, os
import pandas as pd
import brightway2 as bw2
from bw2data.backends.peewee import Activity

isinstance = isinstance

__all__ = ('DataImporter',)

class DataImporter:
    '''
    To import environmental impact characterization factors from databases through
    ``Brightway2``, users can choose different life cycle inventory (LCI) databases
    and life cycle impact assessment (LCIA).
    
    Tip
    ---
    Basic steps:
        
        [1] Load database (you can only load one at a time).
        
        [2] Load indicators (you can load multiple).
        
        [3] Load activities (you can load multiple).


    .. note::
        
        You need to first download the database using :class:`DataDownloader`.


    See Also
    --------
    `Brightway2 <2.docs.brightway.dev>`_
    
    '''

    def __init__(self, name):
        self.name = name
        self._database = None
        self._indicators = set()
        self._activities = {}
        self._ind_aliases = {}
        self._act_aliases = {}


    def load_database(self, database):
        '''
        Load designated database.
        
        Parameters
        ----------
        database: str
            Name of the database.        
        '''        
        db_lower = database.lower()
        
        if db_lower not in bw2.databases:
            raise ValueError(f'Database "{database}" not available. ' \
                             'Please first download the data using `DataDownloader`.')
        else:
            self._database = db = bw2.Database(database)

        print(f'Database {db} with {len(db)} inventories has been loaded.')

        
    def load_indicators(self, add: bool, method='', category='', indicator=''):
        '''
        Select and/or load designated impact indicators.
        
        Parameters
        ----------
        add : bool
            Whether to add the indicators for data importing.
            If False, a dict of the indicators that satisfy the search criteria
            will be returned.
        method: str
            Impact assessment method of the indicator (e.g., TRACI).
        category: str
            Category of the indicator (e.g., environmental impact).
        indicator: str
            Name of the indicator (e.g., global warming).

        Tip
        ---
        Leave the method, category, or indicator field as blank (i.e., '')
        if want all of the options. E.g., load_indicators() will return
        all indicators available in the package (800+ in total).
        
        '''
        
        indicators = set(ind for ind in bw2.methods if (
            method in ind[0] and
            category in ind[1] and
            indicator in ind[2]
            ))
        
        if add:
            self._indicators = self._indicators.union(indicators)
            print(f'{len(indicators)} indicator(s) loaded/updated.')

        else:
            return indicators

    
    def load_activities(self, string: str, add: bool, limit=20, show=False,
                        **kwargs):
        '''
        Select and/or load activities of interest.

        Parameters
        ----------
        string : str
            Search string.
        add : bool
            Whether to add the activities for data importing.
            If False, a dict of the activities that satisfy the search criteria
            will be returned.
        limit : int
            Maximum number of search results to return.
        show : bool
            Whether to print the detailed information associated with the activities.
        kwargs :
            Other keyword arguments that will be passed to ```Brightway2-data``.
        
        See Also
        --------
        :func:`search` in `Brightway2-data SQLiteBackend <https://2.docs.brightway.dev/technical/bw2data.html#default-backend-databases-stored-in-a-sqlite-database>`_

        '''

        activities = self.database.search(string, limit=limit, **kwargs)
        act_dct = {act.as_dict()['name']: act for act in activities}

        for act in activities:
            if show:
                self.show_activity(act)
 
        if add:
            self._activities.update(act_dct)
            print(f'{len(act_dct)} activity(ies) loaded/updated.')

        else:
            return act_dct

    def show_activity(self, activity):
        '''
        Show detailed description about an activity.
        
        Parameters
        ----------
        activity : str or :class:`Activity`
            Name of the activity as str, or the :class:`Activity` in ``Brightway2-data``.


        .. note::
            
            When given as a str, the function will first try to search within
            the loaded activities, if there is no match,
            then it will search the entire database.

        '''
        if isinstance(activity, str):
            try:
                activities = [self.activities[activity]]
            except KeyError:
                try:
                    activity = self._act_aliases[activity]
                    activities = [self.activities[activity]]
                except KeyError:
                    activities = self.database.search(activity)
                    if not activities:
                        raise ValueError(f'No search results for "{activity}".')
        
        else:
            if not isinstance(activity, Activity):
                raise TypeError(f'The input activity type "{type(activity).__name__}" is not valid.')
            else:
                activities = [activity]

        dfs = []
        for act in activities:
            act_dct = act.as_dict()
            name = act_dct['name']
            df = pd.DataFrame(
                data={name: [v for v in act_dct.values()]},
                index=[k for k in act_dct.keys()])
            print(f'{df.fillna("N/A")}\n')
            
            dfs.append(df)
        
        if len(dfs) == 1:
            return df        
        else:
            return dfs
        

    def remove(self, kind, keys):
        '''
        Remove loaded indicators or activities.
        
        Parameters
        ----------
        kind : str
            Can be "indicator" or "activity".
        keys : iterable    
            Key(s) of the item(s) to be removed.
        '''
        
        kind_lower = kind.lower()
        if kind_lower in ('indicator', 'indicators'):
            for k in keys:
                self._indicators.remove(k)

        elif kind_lower in ('activity', 'activities'):
            for k in keys:
                self._activities.pop(k)

        else:
            raise ValueError('kind can only be "indicator" or "activity", ' \
                             f'not "{kind}".')
        
    def add_alias(self, kind, alias_dct):
        '''
        Add alternative names for loaded indicators or activities.
        
        Parameters
        ----------
        kind : str
            Can be "indicator" or "activity".
        alias_dct : dict    
            Keys should be the entries in the `indicators` attribute or the
            keys of the `activities` attribute, values should be the aliases.
            
        '''
        
        

    def get_CF(self, indicators=(), activities=(), show=False, path=''):
        '''
        Get impact characterization factors.
        
        Parameters
        ----------
        indicators : iterable
            Keys of the indicators in the ``indicators`` property.
            Will be defaulted to all loaded indicators if not provided.
        activities : iterable
            Keys of the activities in the ``activities`` property.        
            Will be defaulted to all loaded indicators if not provided.
        show : bool
            Whether to print all characterization factors in the console.
        path : str
            If provided, the :class:`pandas.DataFrame` will be saved to the given file path.
        
        Returns
        -------
        [:class:`pandas.DataFrame`]
            Characterization factors.
        
        Tip
        ---
        [1] Use ``show_activity`` to see the functional unit of the activity.
        The quantity will be 1.
        
        [2] If you run into an "FileNotFoundError", most likely there are some
        indicators that do not acutally have corresponding impact assessment methods,
        try to load indicators one at a time to look for the culprit.
        
        '''
        
        if not self.indicators:
            raise ValueError('No loaded indicators.')
        elif not self.activities:
            raise ValueError('No loaded activities.')
        
        if not set(indicators).issubset(self.indicators):
            raise ValueError('Provided indicator(s) not all loaded.')
        
        inds = indicators if indicators else self.indicators
        acts = [self.activities[k] for k in activities] if activities \
            else [v for v in self.activities.values()]
        
        bw2.calculation_setups['multiLCA'] = {'inv': [{a:1} for a in acts],
                                              'ia': inds}
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        mlca = bw2.MultiLCA('multiLCA')
        sys.stdout = stdout

        pd_indices = [a['name'] for a in acts]
        pd_cols = pd.MultiIndex.from_tuples(inds, names=('method', 'category', 'indicator'))        
        df = pd.DataFrame(data=mlca.results, index=pd_indices, columns=pd_cols)
        df[('-', '-', 'functional unit')] = [a['unit'] for a in acts]
        df.sort_index(axis=1, inplace=True)

        if show:
            print(df)

        if path:
            if path.endswith('.csv'):
                df.to_csv(path)
            elif (path.endswith('.xlsx') or path.endswith('.xls')):
                df.to_excel(path)
            else:
                extension = path.split('.')[-1]
                raise ValueError('Only "csv", "xlsx", or "xls" files are supported, ' \
                                 f'not {extension}.')

        return df


    @property
    def available_databases(self):
        '''All databases that have been loaded into ``Brightway2``.'''
        return bw2.databases

    @property
    def database(self):
        '''Loaded database.'''
        return self._database
    @database.setter
    def database(self, i):
        raise AttributeError('Use ``load_database`` to load/switch database.')

    @property
    def indicators(self):
        '''[list] Loaded impact indicators.'''
        return list(self._indicators)
    @indicators.setter
    def indicators(self, i):
        raise AttributeError('Use ``load_indicators``/``remove`` to add/remove indicators.')

    @property
    def activities(self):
        '''[dict] Loaded activities.'''
        return self._activities
    @activities.setter
    def activities(self, i):
        raise AttributeError('Use ``load_activities``/``remove`` to add/remove activities.')




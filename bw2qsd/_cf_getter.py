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

'''
TODO:
    Improve search ability, update docs

'''


import sys, os
import pandas as pd
import brightway2 as bw2
from collections.abc import Iterable
from bw2data.backends.peewee import Activity
from .utils import export_df, format_name

isinstance = isinstance

__all__ = ('CFgetter',)


    
def _filter_inds(inds, cats, include):
    for n, cat in enumerate(cats):
        if cat:
            if isinstance(cat, str):
                cat = (cat, )
            elif not isinstance(cat, Iterable):
                raise TypeError(f'"{cat}" can only be str or iterable, ' \
                                f'not {type(cat).__name__}.')
            if include is True:
                for string in cat:
                    string_lower = string.lower()
                    inds = [ind for ind in inds if string_lower in ind[n].lower()]
            else:                
                for string in cat:
                    string_lower = string.lower()
                    inds = [ind for ind in inds if not string_lower in ind[n].lower()]
                
    return inds


class CFgetter:
    '''
    To get environmental impact characterization factors from databases through
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

    __slots__ = ('name', '_database', '_indicators', '_activities', '_CFs')

    def __init__(self, name):
        self.name = name
        self._database = None
        self._indicators = set()
        self._activities = {}
        self._CFs = None

    def __repr__(self):
        return f'<CFgetter: {self.name}>'

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


    def load_indicators(self, add=False, method='', method_exclude='',
                        category='', category_exclude='',
                        indicator='', indicator_exclude=''):
        '''
        Select and/or load designated impact indicators.
        
        Parameters
        ----------
        add : bool
            Whether to include the indicators in impact assessment for characterization factors.
            If False, a dict of the indicators that satisfy the search criteria
            will be returned.
        method: str or Iterable
            Impact assessment method of the indicator (e.g., TRACI).
        method_exclude: str or Iterable
            Strings to be excluded from the method field.
        category: str or Iterable
            Category of the indicator (e.g., environmental impact).
        category_exclude: str or Iterable
            Strings to be excluded from the category field.
        indicator: str or Iterable
            Name of the indicator (e.g., global warming).
        indicator_exclude: str or Iterable
            Strings to be excluded from the indicator field.

        Tip
        ---
        Leave all fields as blank (i.e., '') if want all of the options.
        E.g., load_indicators() will return
        all indicators available in the package (800+ in total).
        
        '''       
        indicators = bw2.methods.list
        indicators = _filter_inds(indicators, (method, category, indicator), True)
        indicators = _filter_inds(indicators, 
                                  (method_exclude, category_exclude, indicator_exclude),
                                  False)

        if add:
            self._indicators = self._indicators.union(set(indicators))
            msg = 'indicator' if len(indicators) > 1 else 'indicators'
            print(f'\n{len(indicators)} {msg} loaded/updated for {self.name}.')

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
            Whether to include the activities in impact assessment for characterization factors.
            If False, a dict of the activities that satisfy the search criteria
            will be returned.
        limit : int
            Maximum number of search results to return.
        show : bool
            Whether to print the detailed information associated with the activities.
        kwargs :
            Other keyword arguments that will be passed to ```bw2data``.
        
        See Also
        --------
        :func:`search` in `bw2data SQLiteBackend <https://2.docs.brightway.dev/technical/bw2data.html#default-backend-databases-stored-in-a-sqlite-database>`_

        '''
        activities = self.database.search(string, limit=limit, **kwargs)
        act_dct = {act.as_dict()['name']: act for act in activities}

        for act in activities:
            if show:
                self.show_activity(act)
 
        if add:
            self._activities.update(act_dct)
            msg = 'activities' if len(act_dct) > 1 else 'activity'
            print(f'{len(act_dct)} {msg} loaded/updated for {self.name}.\n')

        else:
            return act_dct

    def show_activity(self, activity, **kwargs):
        '''
        Show detailed description about an activity.
        
        Parameters
        ----------
        activity : str or :class:`Activity`
            Name of the activity as str, or the :class:`Activity` in ``bw2data``.
        kwargs :
            Other keyword arguments that will be passed to ```bw2data``.

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
                    activities = [self.activities[activity]]
                except KeyError:
                    activities = self.database.search(activity, **kwargs)
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
        num = 0
        if kind_lower in ('indicator', 'indicators'):
            for k in keys:
                self._indicators.remove(k)
                num += 1
            msg = 'indicators' if num > 1 else 'indicator'

        elif kind_lower in ('activity', 'activities'):
            for k in keys:
                self._activities.pop(k)
                num += 1
            msg = 'activities' if num > 1 else 'activity'
        
        else:
            raise ValueError('kind can only be "indicator" or "activity", ' \
                             f'not "{kind}".')
    
        print(f'Successfully removed {num} {msg} from {self.name}.')
    
    def export_indicators(self, indicators=(), aliases={}, descriptions={},
                          show=False, path=''):
        '''
        Show information about the loaded impact indicators in a :class`pandas.DataFrame`,
        the :class`pandas.DataFrame` will be exported to the path if provided.
        
        Parameters
        ----------
        indicators : iterable
            Keys of the indicators in the ``indicators`` property.
            Will be defaulted to all loaded indicators if not provided.
        aliases : dict
            Keys should be the keys of the indicators in the ``indicators`` property,
            values should be the aliases of the indicators.
        descriptions : dict
            Keys should be the keys of the indicators in the ``indicators`` property,
            values should be the descriptions of the indicators.
        show : bool
            Whether to print the generated :class:`pandas.DataFrame` in the console.
        path : str
            If provided, the :class:`pandas.DataFrame` will be saved to the given file path.
        
        Returns
        -------
        df: :class:`pandas.DataFrame`
            Characterization factors.
            
        Tip
        ---
        The exported file can be directly import into QSD packages to create
        :class:`ImpactIndicator` items.
        
        
        '''
        if not self.indicators:
            raise ValueError('No loaded indicators.')
        if not set(indicators).issubset(self.indicators):
            raise ValueError('Provided indicator(s) not all loaded.')
        
        inds = indicators if indicators else self.indicators

        df = pd.DataFrame({
            'alias': [aliases[ind] if ind in aliases.keys() else '' for ind in inds],
            'unit': [bw2.methods.get(i)['unit'] for i in inds],
            'method': [ind[0] for ind in inds],
            'category': [ind[1] for ind in inds],
            'description': [descriptions[ind] if ind in descriptions.keys() else '' for ind in inds]
            },
            index=pd.Index(data=[format_name(ind[2]) for ind in inds], name='indicator'))
        
        export_df(df, path, show)

        return df
        
    

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
        df: :class:`pandas.DataFrame`
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
        ind_units = [bw2.methods.get(i)['unit'] for i in inds] + ['-']
        acts = [self.activities[k] for k in activities] if activities \
            else [v for v in self.activities.values()]
        
        bw2.calculation_setups['multiLCA'] = {'inv': [{a:1} for a in acts],
                                              'ia': inds}
        # This is to prevent bw2 from printing in the console
        stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        mlca = bw2.MultiLCA('multiLCA')
        sys.stdout = stdout

        pd_indices = [a['name'] for a in acts]
        pd_cols = pd.MultiIndex.from_tuples(inds, names=('method', 'category', 'indicator'))        
        cf_df = pd.DataFrame(data=mlca.results, index=pd_indices, columns=pd_cols)
        cf_df[('-', '-', 'activity functional unit')] = [a['unit'] for a in acts]

        unit_df = pd.DataFrame(data={k: v for k, v in zip(cf_df.columns, ind_units)},
                               index=['indicator unit'])

        df = pd.concat((unit_df, cf_df))
        df.sort_index(axis=1, inplace=True)
        
        if show:
            print(df)

        export_df(df, path, show)
        self._CFs = df

        return df

    def copy(self, name, omit=()):
        '''
        Return a copy of the :class:`CFgetter`.
        
        .. note:
            
            ``CFs`` is not copied.
        
        
        Parameters
        ----------
        name : str
            Name of the copy.
        omit: str or Iterable
            Property(ies) not to be copied.
        
        '''
        new = self.__class__.__new__(self.__class__)
        new.name = name
        new._CFs = None
        if isinstance(omit, str):
            omit = (omit,)
        omit = (*(f'_{o}' for o in omit), 'name', '_CFs')
        
        for s in self.__slots__:
            if not s in omit:
                if s == '_database':
                    new._database = self._database
                else:
                    setattr(new, s, getattr(self, s).copy())
        
        return new

    __copy__ = copy

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

    @property
    def CFs(self):
        '''Results from :func:`get_CF`.'''
        if not self._CFs is None:
            return self._CFs
        else:
            try: return self.get_CF()
            except: return

